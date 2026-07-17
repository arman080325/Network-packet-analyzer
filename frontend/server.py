#!/usr/bin/env python3
"""
frontend/server.py
------------------
Live dashboard backend for NetScope.

Serves the dashboard HTML over HTTP and streams analysed packets to the
browser over a WebSocket — both implemented with ONLY the Python standard
library (socket, threading, hashlib, base64). No `websockets`, no Flask,
no aiohttp. The single external dependency (scapy) is needed for *live*
capture only; `--demo` runs with the standard library alone.

Wire protocol (server -> browser, newline-free JSON frames):
    {"type":"init",      "packets":[...], "alerts":[...], "stats":{...}}
    {"type":"packet",    "packet":{...},  "alerts":[...], "stats":{...}}
    {"type":"heartbeat", "stats":{...}}

Run directly:
    python3 frontend/server.py --demo
    sudo python3 frontend/server.py -i eth0
"""

import os
import sys
import json
import time
import base64
import hashlib
import struct
import socket
import threading
import argparse
from collections import deque
from datetime import datetime

# Make the project root importable when run as `python3 frontend/server.py`
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.analyzer import PacketAnalyzer
from core.anomaly import AnomalyDetector
from core.crypto_detector import CryptoDetector
from core.threat import ThreatScorer
from core.netinfo import classify_ip, service_name

WS_MAGIC = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DASHBOARD_HTML = os.path.join(ROOT, "dashboard.html")


# ════════════════════════════════════════════════════════════════════════════
#  Shared analysis hub — fed by demo or live capture, read by all WS clients
# ════════════════════════════════════════════════════════════════════════════

class Hub:
    """Owns the analysis engines and a ring buffer of recent packets/alerts."""

    def __init__(self, syn_threshold=100, port_scan_threshold=20):
        self.analyzer = PacketAnalyzer()
        self.anomaly  = AnomalyDetector(syn_threshold=syn_threshold,
                                        port_scan_threshold=port_scan_threshold)
        self.crypto   = CryptoDetector()
        self.threat   = ThreatScorer()

        self.recent_packets = deque(maxlen=400)
        self.recent_alerts  = deque(maxlen=120)
        self.recent_crypto  = deque(maxlen=120)

        self._subscribers = []          # list of WSClient
        self._lock = threading.Lock()
        self._seq = 0

    # ── Client registration ─────────────────────────────────────────────
    def subscribe(self, client):
        with self._lock:
            self._subscribers.append(client)

    def unsubscribe(self, client):
        with self._lock:
            if client in self._subscribers:
                self._subscribers.remove(client)

    def snapshot_init(self):
        return {
            "type":    "init",
            "packets": list(self.recent_packets),
            "alerts":  list(self.recent_alerts),
            "stats":   self.stats(),
        }

    # ── Core ingest — one packet through the whole pipeline ──────────────
    def ingest(self, pkt: dict):
        self.analyzer.process(pkt)
        self.anomaly.check(pkt)
        self.crypto.inspect(pkt)

        new_alerts = self.anomaly.get_new_alerts()
        for a in new_alerts:
            self.threat.register(a)
            self.recent_alerts.append(self._clean_alert(a))

        # Pull crypto detections produced for THIS packet (last one, if any)
        wire_pkt = self._wire_packet(pkt)
        crypto_hit = self._last_crypto_for(pkt)
        if crypto_hit:
            wire_pkt["enc"] = True
            wire_pkt["enc_methods"] = crypto_hit
            self.recent_crypto.append({
                "timestamp": wire_pkt["timestamp"], "src": wire_pkt["src_ip"],
                "dst": wire_pkt["dst_ip"], "dst_port": wire_pkt["dst_port"],
                "methods": crypto_hit, "bytes": wire_pkt["length"],
            })

        self.recent_packets.append(wire_pkt)

        msg = {
            "type":   "packet",
            "packet": wire_pkt,
            "alerts": [self._clean_alert(a) for a in new_alerts],
            "stats":  self.stats(),
        }
        self._broadcast(msg)

    def heartbeat(self):
        self._broadcast({"type": "heartbeat", "stats": self.stats()})

    # ── Stats assembled for the wire ─────────────────────────────────────
    def stats(self):
        snap = self.analyzer.live_snapshot()
        crep = self.crypto.report()
        trep = self.threat.report()
        proto = snap["protocol_counts"]
        return {
            "total_packets":   snap["total_packets"],
            "total_bytes":     snap["total_bytes"],
            "pps":             snap["pps"],
            "tcp":             proto.get("TCP", 0),
            "udp":             proto.get("UDP", 0),
            "icmp":            proto.get("ICMP", 0),
            "arp":             proto.get("ARP", 0),
            "protocol_counts": proto,
            "ipclass_counts":  snap["ipclass_counts"],
            "connections_est": snap["connections_est"],
            "connections_total": snap["connections_total"],
            "retransmissions": snap["retransmissions"],
            "throughput":      snap["throughput"],
            "top_services":    snap["top_services"],
            "top_flows":       snap["top_flows"],
            "alerts_total":    len(self.anomaly._all_alerts),
            "alerts_by_type":  self.anomaly.full_report()["by_type"],
            "crypto": {
                "encrypted":      crep["encrypted_payloads"],
                "encrypted_pct":  crep["encrypted_pct"],
                "high_entropy":   crep["high_entropy_payloads"],
                "avg_entropy":    crep["avg_entropy"],
                "recent_entropy": crep["recent_avg_entropy"],
                "last_entropy":   crep["last_entropy"],
                "breakdown":      crep["protocol_breakdown"],
            },
            "threat": {
                "hosts_tracked": trep["hosts_tracked"],
                "malicious":     trep["malicious"],
                "suspicious":    trep["suspicious"],
                "top":           trep["top"][:12],
            },
        }

    # ── Helpers ──────────────────────────────────────────────────────────
    def _wire_packet(self, pkt):
        self._seq += 1
        src = pkt.get("src_ip", "")
        dst = pkt.get("dst_ip", "")
        dport = pkt.get("dst_port")
        return {
            "id":        self._seq,
            "timestamp": pkt.get("timestamp", ""),
            "protocol":  pkt.get("protocol", "UNKNOWN"),
            "src_ip":    src,
            "dst_ip":    dst,
            "src_port":  pkt.get("src_port"),
            "dst_port":  dport,
            "length":    pkt.get("length", 0),
            "flags":     pkt.get("flags", ""),
            "info":      pkt.get("info", ""),
            "ttl":       pkt.get("ttl"),
            "src_class": classify_ip(src),
            "dst_class": classify_ip(dst),
            "service":   service_name(dport),
            "enc":       False,
        }

    def _last_crypto_for(self, pkt):
        """Return method names if the crypto detector just recorded this packet."""
        results = self.crypto._results
        if not results:
            return None
        last = results[-1]
        if last.get("src") == pkt.get("src_ip") and last.get("timestamp") == pkt.get("timestamp"):
            return [f["method"] for f in last.get("findings", [])]
        return None

    @staticmethod
    def _clean_alert(a):
        return {k: v for k, v in a.items() if not k.startswith("_")}

    def _broadcast(self, msg):
        payload = json.dumps(msg, default=str)
        with self._lock:
            dead = []
            for c in self._subscribers:
                try:
                    c.send(payload)
                except Exception:
                    dead.append(c)
            for c in dead:
                if c in self._subscribers:
                    self._subscribers.remove(c)


# ════════════════════════════════════════════════════════════════════════════
#  Minimal WebSocket server (RFC 6455, text frames, server->client + ping)
# ════════════════════════════════════════════════════════════════════════════

class WSClient:
    def __init__(self, conn):
        self.conn = conn
        self._lock = threading.Lock()

    def handshake(self):
        data = b""
        self.conn.settimeout(5)
        while b"\r\n\r\n" not in data:
            chunk = self.conn.recv(1024)
            if not chunk:
                return False
            data += chunk
        self.conn.settimeout(None)
        headers = {}
        for line in data.decode("latin1").split("\r\n")[1:]:
            if ":" in line:
                k, v = line.split(":", 1)
                headers[k.strip().lower()] = v.strip()
        key = headers.get("sec-websocket-key")
        if not key:
            return False
        accept = base64.b64encode(
            hashlib.sha1((key + WS_MAGIC).encode()).digest()
        ).decode()
        resp = (
            "HTTP/1.1 101 Switching Protocols\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Accept: {accept}\r\n\r\n"
        )
        self.conn.sendall(resp.encode())
        return True

    def send(self, text: str):
        data = text.encode("utf-8")
        header = bytearray([0x81])  # FIN + text opcode
        n = len(data)
        if n < 126:
            header.append(n)
        elif n < 65536:
            header.append(126)
            header += struct.pack(">H", n)
        else:
            header.append(127)
            header += struct.pack(">Q", n)
        with self._lock:
            self.conn.sendall(bytes(header) + data)

    def read_loop(self):
        """Drain client frames (we ignore content, just detect close)."""
        try:
            while True:
                first = self._recv_exact(2)
                if not first:
                    break
                opcode = first[0] & 0x0F
                masked = first[1] & 0x80
                length = first[1] & 0x7F
                if length == 126:
                    length = struct.unpack(">H", self._recv_exact(2))[0]
                elif length == 127:
                    length = struct.unpack(">Q", self._recv_exact(8))[0]
                mask = self._recv_exact(4) if masked else b""
                payload = self._recv_exact(length) if length else b""
                if opcode == 0x8:   # close
                    break
        except Exception:
            pass

    def _recv_exact(self, n):
        buf = b""
        while len(buf) < n:
            chunk = self.conn.recv(n - len(buf))
            if not chunk:
                return None
            buf += chunk
        return buf

    def close(self):
        try:
            self.conn.close()
        except Exception:
            pass


def ws_server(hub, host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(16)

    def handle(conn):
        client = WSClient(conn)
        try:
            if not client.handshake():
                client.close()
                return
            hub.subscribe(client)
            client.send(json.dumps(hub.snapshot_init(), default=str))
            client.read_loop()       # blocks until the browser disconnects
        finally:
            hub.unsubscribe(client)
            client.close()

    while True:
        conn, _ = s.accept()
        threading.Thread(target=handle, args=(conn,), daemon=True).start()


# ════════════════════════════════════════════════════════════════════════════
#  Tiny static HTTP server (serves dashboard.html only)
# ════════════════════════════════════════════════════════════════════════════

def http_server(host, port, ws_port):
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):  # silence default logging
            pass

        def do_GET(self):
            path = self.path.split("?")[0]
            if path in ("/", "/dashboard.html"):
                try:
                    with open(DASHBOARD_HTML, "r", encoding="utf-8") as f:
                        html = f.read()
                    # Inject the WS port the server is actually using
                    html = html.replace("__WS_PORT__", str(ws_port))
                    body = html.encode("utf-8")
                except FileNotFoundError:
                    self.send_error(404, "dashboard.html not found")
                    return
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            elif path == "/health":
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"ok")
            else:
                self.send_error(404)

    httpd = ThreadingHTTPServer((host, port), Handler)
    httpd.serve_forever()


# ════════════════════════════════════════════════════════════════════════════
#  Packet producers
# ════════════════════════════════════════════════════════════════════════════

def run_demo_feed(hub, pps):
    from utils.demo import demo_packet_stream
    for pkt in demo_packet_stream(pps=pps):
        hub.ingest(pkt)


def run_live_feed(hub, interface, bpf_filter, count):
    from core.sniffer import PacketSniffer
    sniffer = PacketSniffer(interface=interface, bpf_filter=bpf_filter, packet_count=count)
    sniffer.start(callback=hub.ingest)


def heartbeat_loop(hub, interval=1.0):
    while True:
        time.sleep(interval)
        try:
            hub.heartbeat()
        except Exception:
            pass


# ════════════════════════════════════════════════════════════════════════════
#  Entry point
# ════════════════════════════════════════════════════════════════════════════

def main():
    ap = argparse.ArgumentParser(description="NetScope live dashboard server")
    ap.add_argument("--demo", action="store_true", help="Stream simulated traffic")
    ap.add_argument("-i", "--interface", default=None)
    ap.add_argument("-f", "--filter", default="")
    ap.add_argument("-c", "--count", type=int, default=0)
    ap.add_argument("-t", "--timeout", type=int, default=0)
    ap.add_argument("-o", "--output", default=None)
    ap.add_argument("--http-port", type=int, default=8080, dest="http_port")
    ap.add_argument("--ws-port", type=int, default=8765, dest="ws_port")
    ap.add_argument("--demo-pps", type=int, default=18, dest="demo_pps")
    ap.add_argument("--threshold-syn", type=int, default=100, dest="threshold_syn")
    ap.add_argument("--threshold-port", type=int, default=20, dest="threshold_port")
    args = ap.parse_args()

    hub = Hub(syn_threshold=args.threshold_syn, port_scan_threshold=args.threshold_port)

    # Start network servers
    threading.Thread(target=ws_server, args=(hub, "0.0.0.0", args.ws_port), daemon=True).start()
    threading.Thread(target=http_server, args=("0.0.0.0", args.http_port, args.ws_port), daemon=True).start()
    threading.Thread(target=heartbeat_loop, args=(hub,), daemon=True).start()

    mode = "DEMO" if args.demo else f"LIVE ({args.interface or 'auto'})"
    print(f"[*] NetScope dashboard server — mode: {mode}")
    print(f"[*] HTTP  : http://localhost:{args.http_port}/dashboard.html")
    print(f"[*] WS    : ws://localhost:{args.ws_port}")
    print("[*] Press Ctrl+C to stop.")

    # Start the packet feed (blocking)
    try:
        if args.demo:
            run_demo_feed(hub, args.demo_pps)
        else:
            run_live_feed(hub, args.interface, args.filter, args.count)
    except KeyboardInterrupt:
        print("\n[*] Server stopped.")


if __name__ == "__main__":
    main()
