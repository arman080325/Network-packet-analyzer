#!/usr/bin/env python3
"""
backend/app.py
---------------
Production web backend for NetScope — single-port HTTP + WebSocket server
built entirely on the Python standard library (socket, threading, hashlib,
base64). This mirrors the exact approach the original frontend/server.py
already used successfully, just combined onto ONE port so it works behind
Render's single public $PORT.

No Flask, no flask-sock, no gunicorn/eventlet — nothing that depends on a
specific WSGI server's WebSocket support. If it worked with
`frontend/server.py` locally, it works here.

Endpoints:
  GET  /health          -> liveness probe (JSON)
  GET  /api/status      -> current stats snapshot (JSON)
  GET  /                -> service info (JSON)
  WS   /ws               -> live packet/alert/stat stream

Run:
    pip install -r backend/requirements.txt   # only cryptography + optional scapy
    python backend/app.py                     # reads $PORT, default 8080
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
from collections import deque

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.analyzer import PacketAnalyzer
from core.anomaly import AnomalyDetector
from core.crypto_detector import CryptoDetector
from core.threat import ThreatScorer
from core.netinfo import classify_ip, service_name

WS_MAGIC = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

DEMO_PPS = int(os.environ.get("DEMO_PPS", "18"))
SYN_THRESHOLD = int(os.environ.get("SYN_THRESHOLD", "100"))
PORT_SCAN_THRESHOLD = int(os.environ.get("PORT_SCAN_THRESHOLD", "20"))


# ════════════════════════════════════════════════════════════════════════════
#  Hub — owns the analysis engines + ring buffers, fans out to WS clients
# ════════════════════════════════════════════════════════════════════════════
class Hub:
    def __init__(self, syn_threshold=100, port_scan_threshold=20):
        self.analyzer = PacketAnalyzer()
        self.anomaly = AnomalyDetector(syn_threshold=syn_threshold,
                                        port_scan_threshold=port_scan_threshold)
        self.crypto = CryptoDetector()
        self.threat = ThreatScorer()

        self.recent_packets = deque(maxlen=400)
        self.recent_alerts = deque(maxlen=120)

        self._subscribers = []
        self._lock = threading.Lock()
        self._seq = 0
        self.started_at = time.time()

    def subscribe(self, client):
        with self._lock:
            self._subscribers.append(client)

    def unsubscribe(self, client):
        with self._lock:
            if client in self._subscribers:
                self._subscribers.remove(client)

    def snapshot_init(self):
        return {
            "type": "init",
            "packets": list(self.recent_packets),
            "alerts": list(self.recent_alerts),
            "stats": self.stats(),
        }

    def ingest(self, pkt: dict):
        self.analyzer.process(pkt)
        self.anomaly.check(pkt)
        self.crypto.inspect(pkt)

        new_alerts = self.anomaly.get_new_alerts()
        for a in new_alerts:
            self.threat.register(a)
            self.recent_alerts.append(self._clean_alert(a))

        wire_pkt = self._wire_packet(pkt)
        crypto_hit = self._last_crypto_for(pkt)
        if crypto_hit:
            wire_pkt["enc"] = True
            wire_pkt["enc_methods"] = crypto_hit

        self.recent_packets.append(wire_pkt)

        msg = {
            "type": "packet",
            "packet": wire_pkt,
            "alerts": [self._clean_alert(a) for a in new_alerts],
            "stats": self.stats(),
        }
        self._broadcast(msg)

    def heartbeat(self):
        self._broadcast({"type": "heartbeat", "stats": self.stats()})

    def stats(self):
        snap = self.analyzer.live_snapshot()
        crep = self.crypto.report()
        trep = self.threat.report()
        proto = snap["protocol_counts"]
        return {
            "uptime_s": round(time.time() - self.started_at, 1),
            "total_packets": snap["total_packets"],
            "total_bytes": snap["total_bytes"],
            "pps": snap["pps"],
            "tcp": proto.get("TCP", 0),
            "udp": proto.get("UDP", 0),
            "icmp": proto.get("ICMP", 0),
            "arp": proto.get("ARP", 0),
            "protocol_counts": proto,
            "ipclass_counts": snap["ipclass_counts"],
            "connections_est": snap["connections_est"],
            "connections_total": snap["connections_total"],
            "retransmissions": snap["retransmissions"],
            "throughput": snap["throughput"],
            "top_services": snap["top_services"],
            "top_flows": snap["top_flows"],
            "alerts_total": len(self.anomaly._all_alerts),
            "alerts_by_type": self.anomaly.full_report()["by_type"],
            "crypto": {
                "encrypted": crep["encrypted_payloads"],
                "encrypted_pct": crep["encrypted_pct"],
                "high_entropy": crep["high_entropy_payloads"],
                "avg_entropy": crep["avg_entropy"],
                "recent_entropy": crep["recent_avg_entropy"],
                "last_entropy": crep["last_entropy"],
                "breakdown": crep["protocol_breakdown"],
            },
            "threat": {
                "hosts_tracked": trep["hosts_tracked"],
                "malicious": trep["malicious"],
                "suspicious": trep["suspicious"],
                "top": trep["top"][:12],
            },
        }

    def _wire_packet(self, pkt):
        self._seq += 1
        src = pkt.get("src_ip", "")
        dst = pkt.get("dst_ip", "")
        dport = pkt.get("dst_port")
        return {
            "id": self._seq,
            "timestamp": pkt.get("timestamp", ""),
            "protocol": pkt.get("protocol", "UNKNOWN"),
            "src_ip": src,
            "dst_ip": dst,
            "src_port": pkt.get("src_port"),
            "dst_port": dport,
            "length": pkt.get("length", 0),
            "flags": pkt.get("flags", ""),
            "info": pkt.get("info", ""),
            "ttl": pkt.get("ttl"),
            "src_class": classify_ip(src),
            "dst_class": classify_ip(dst),
            "service": service_name(dport),
            "enc": False,
        }

    def _last_crypto_for(self, pkt):
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


hub = Hub(syn_threshold=SYN_THRESHOLD, port_scan_threshold=PORT_SCAN_THRESHOLD)


# ════════════════════════════════════════════════════════════════════════════
#  Minimal WebSocket client wrapper (stdlib only)
# ════════════════════════════════════════════════════════════════════════════
class WSClient:
    def __init__(self, conn):
        self.conn = conn
        self._lock = threading.Lock()

    def handshake(self, headers):
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
        header = bytearray([0x81])
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
        """Drain client frames (content ignored); returns when the client closes."""
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
                if masked:
                    self._recv_exact(4)
                if length:
                    self._recv_exact(length)
                if opcode == 0x8:
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


# ════════════════════════════════════════════════════════════════════════════
#  Single-port dispatcher — plain HTTP for REST, upgrade path for WebSocket
# ════════════════════════════════════════════════════════════════════════════
def _read_headers(conn):
    conn.settimeout(10)
    data = b""
    while b"\r\n\r\n" not in data:
        chunk = conn.recv(4096)
        if not chunk:
            return None, None
        data += chunk
        if len(data) > 16384:  # guard against runaway headers
            return None, None
    conn.settimeout(None)
    head, _, _rest = data.partition(b"\r\n\r\n")
    lines = head.decode("latin1").split("\r\n")
    request_line = lines[0]
    headers = {}
    for line in lines[1:]:
        if ":" in line:
            k, v = line.split(":", 1)
            headers[k.strip().lower()] = v.strip()
    return request_line, headers


def _json_response(obj, status="200 OK"):
    body = json.dumps(obj, default=str).encode("utf-8")
    return (
        f"HTTP/1.1 {status}\r\n"
        "Content-Type: application/json\r\n"
        "Access-Control-Allow-Origin: *\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n\r\n"
    ).encode("utf-8") + body


def _handle_connection(conn):
    try:
        request_line, headers = _read_headers(conn)
        if not request_line:
            conn.close()
            return
        try:
            method, path, _ = request_line.split(" ")
        except ValueError:
            conn.close()
            return
        path = path.split("?")[0]

        if headers.get("upgrade", "").lower() == "websocket":
            client = WSClient(conn)
            if not client.handshake(headers):
                conn.close()
                return
            hub.subscribe(client)
            try:
                client.send(json.dumps(hub.snapshot_init(), default=str))
                client.read_loop()
            finally:
                hub.unsubscribe(client)
                client.close()
            return

        # Plain HTTP REST endpoints
        if path == "/health":
            resp = _json_response({"status": "ok", "uptime_s": round(time.time() - hub.started_at, 1)})
        elif path == "/api/status":
            resp = _json_response(hub.stats())
        elif path == "/":
            resp = _json_response({
                "name": "NetScope API",
                "description": "Live network traffic analysis backend",
                "endpoints": ["/health", "/api/status", "/ws (WebSocket)"],
            })
        else:
            resp = _json_response({"error": "not found"}, status="404 Not Found")

        conn.sendall(resp)
        conn.close()
    except Exception:
        try:
            conn.close()
        except Exception:
            pass


def serve(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(64)
    print(f"[*] NetScope backend listening on http://{host}:{port}  (WS at /ws)")
    while True:
        conn, _addr = s.accept()
        threading.Thread(target=_handle_connection, args=(conn,), daemon=True).start()


# ════════════════════════════════════════════════════════════════════════════
#  Packet producers
# ════════════════════════════════════════════════════════════════════════════
def run_demo_feed():
    from utils.demo import demo_packet_stream
    for pkt in demo_packet_stream(pps=DEMO_PPS):
        hub.ingest(pkt)


def run_live_feed():
    from core.sniffer import PacketSniffer
    interface = os.environ.get("CAPTURE_INTERFACE")
    bpf_filter = os.environ.get("CAPTURE_FILTER", "")
    sniffer = PacketSniffer(interface=interface, bpf_filter=bpf_filter, packet_count=0)
    sniffer.start(callback=hub.ingest)


def heartbeat_loop(interval=1.0):
    while True:
        time.sleep(interval)
        try:
            hub.heartbeat()
        except Exception:
            pass


def main():
    port = int(os.environ.get("PORT", "8080"))

    threading.Thread(target=heartbeat_loop, daemon=True).start()
    if os.environ.get("ALLOW_LIVE_CAPTURE") == "1":
        threading.Thread(target=run_live_feed, daemon=True).start()
        print("[*] Mode: LIVE capture")
    else:
        threading.Thread(target=run_demo_feed, daemon=True).start()
        print("[*] Mode: DEMO (simulated traffic)")

    try:
        serve("0.0.0.0", port)
    except KeyboardInterrupt:
        print("\n[*] Server stopped.")


if __name__ == "__main__":
    main()
