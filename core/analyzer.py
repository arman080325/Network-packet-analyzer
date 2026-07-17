"""
core/analyzer.py
----------------
Stateful packet analyzer.

Tracks per-protocol counters, top talkers, port/service usage, TCP
connection states, conversation flows, per-second throughput history,
retransmission estimates and IP-class breakdown.

Call .process(summary) for each packet, then .summary() at end, or
.live_snapshot() at any time for a dashboard-friendly rolling view.
"""

import time
from collections import defaultdict, Counter, deque
from datetime import datetime

from core.netinfo import classify_ip, service_name


class PacketAnalyzer:

    def __init__(self):
        self.total_packets   = 0
        self.total_bytes     = 0
        self.protocol_counts = Counter()
        self.src_ip_counts   = Counter()
        self.dst_ip_counts   = Counter()
        self.port_counts     = Counter()          # dst ports
        self.service_counts  = Counter()          # friendly service names
        self.flag_counts     = Counter()
        self.ipclass_counts  = Counter()          # private/public/...
        self.dns_queries     = []
        self.connections     = {}                 # 5-tuple -> state
        self.bytes_per_proto = defaultdict(int)
        self.payload_sizes   = []
        self.start_time      = datetime.now()
        self._start_perf     = time.time()

        # Conversation flows: (a_ip,b_ip) -> {bytes, packets, protos}
        self.flows           = defaultdict(lambda: {"bytes": 0, "packets": 0, "protos": set()})

        # Per-second throughput history (rolling 120s)
        self._tp_bucket      = None               # current second
        self._tp_bytes       = 0
        self._tp_pkts        = 0
        self.throughput      = deque(maxlen=120)  # [{t, bytes, pkts}]

        # Retransmission estimate: seen (5-tuple, seq) signatures
        self._tcp_seen       = set()
        self.retransmissions = 0

    # ── Public API ─────────────────────────────────────────────────────────

    def process(self, pkt: dict):
        self.total_packets += 1
        length = pkt.get("length", 0)
        self.total_bytes += length

        proto = pkt.get("protocol", "UNKNOWN")
        self.protocol_counts[proto] += 1
        self.bytes_per_proto[proto] += length

        src = pkt.get("src_ip", "")
        dst = pkt.get("dst_ip", "")
        if src:
            self.src_ip_counts[src] += 1
            self.ipclass_counts[classify_ip(src)] += 1
        if dst:
            self.dst_ip_counts[dst] += 1

        dport = pkt.get("dst_port")
        if dport:
            self.port_counts[dport] += 1
            svc = service_name(dport)
            if svc:
                self.service_counts[svc] += 1

        flags = pkt.get("flags", "")
        if flags:
            self.flag_counts[flags] += 1

        # DNS
        info = pkt.get("info", "")
        if info.startswith("DNS query:"):
            self.dns_queries.append(info.replace("DNS query: ", ""))

        # Connection + retransmission tracking (TCP)
        if proto == "TCP" and src and dst and dport:
            key = (src, pkt.get("src_port"), dst, dport)
            if "SYN" in flags and "ACK" not in flags:
                self.connections[key] = "SYN_SENT"
            elif "SYN" in flags and "ACK" in flags:
                self.connections[key] = "SYN_ACK"
            elif "ACK" in flags and "SYN" not in flags:
                if key in self.connections:
                    self.connections[key] = "ESTABLISHED"
            elif "FIN" in flags or "RST" in flags:
                self.connections[key] = "CLOSED"

            seq = pkt.get("seq")
            if seq is not None and length > 0:
                sig = (key, seq, length)
                if sig in self._tcp_seen:
                    self.retransmissions += 1
                else:
                    self._tcp_seen.add(sig)

        # Conversation flow (direction-agnostic pair key)
        if src and dst:
            pair = tuple(sorted((src, dst)))
            f = self.flows[pair]
            f["bytes"] += length
            f["packets"] += 1
            f["protos"].add(proto)

        payload = pkt.get("payload", b"")
        if payload:
            self.payload_sizes.append(len(payload))

        self._record_throughput(length)

    def summary(self) -> dict:
        elapsed = (datetime.now() - self.start_time).total_seconds() or 1
        pps = self.total_packets / elapsed
        established = sum(1 for v in self.connections.values() if v == "ESTABLISHED")
        closed      = sum(1 for v in self.connections.values() if v == "CLOSED")

        return {
            "total_packets":      self.total_packets,
            "total_bytes":        self.total_bytes,
            "total_kb":           round(self.total_bytes / 1024, 2),
            "pps":                round(pps, 2),
            "duration_sec":       round(elapsed, 2),
            "protocol_counts":    dict(self.protocol_counts.most_common()),
            "bytes_per_proto":    dict(self.bytes_per_proto),
            "top_src_ips":        self.src_ip_counts.most_common(10),
            "top_dst_ips":        self.dst_ip_counts.most_common(10),
            "top_ports":          self.port_counts.most_common(10),
            "top_services":       self.service_counts.most_common(10),
            "ipclass_counts":     dict(self.ipclass_counts),
            "flag_distribution":  dict(self.flag_counts),
            "dns_queries":        self.dns_queries[-20:],
            "top_dns_domains":    Counter(self.dns_queries).most_common(10),
            "connections_total":  len(self.connections),
            "connections_est":    established,
            "connections_closed": closed,
            "retransmissions":    self.retransmissions,
            "top_flows":          self.top_flows(10),
            "avg_pkt_size":       round(self.total_bytes / max(self.total_packets, 1), 2),
            "avg_payload_bytes":  round(sum(self.payload_sizes) / len(self.payload_sizes), 2)
                                  if self.payload_sizes else 0,
            "avg_latency_ms":     0,
            "fragments":          0,
        }

    def top_flows(self, n=10):
        rows = []
        for (a, b), f in self.flows.items():
            rows.append({
                "a": a, "b": b,
                "bytes": f["bytes"],
                "packets": f["packets"],
                "protos": sorted(f["protos"]),
            })
        rows.sort(key=lambda r: r["bytes"], reverse=True)
        return rows[:n]

    def live_snapshot(self) -> dict:
        """Lightweight rolling view for the dashboard heartbeat."""
        elapsed = max(time.time() - self._start_perf, 1)
        return {
            "total_packets":   self.total_packets,
            "total_bytes":     self.total_bytes,
            "pps":             round(self.total_packets / elapsed, 1),
            "protocol_counts": dict(self.protocol_counts),
            "ipclass_counts":  dict(self.ipclass_counts),
            "connections_est": sum(1 for v in self.connections.values() if v == "ESTABLISHED"),
            "connections_total": len(self.connections),
            "retransmissions": self.retransmissions,
            "throughput":      list(self.throughput),
            "top_services":    self.service_counts.most_common(6),
            "top_flows":       self.top_flows(8),
        }

    # ── Internal ───────────────────────────────────────────────────────────

    def _record_throughput(self, length):
        sec = int(time.time())
        if self._tp_bucket is None:
            self._tp_bucket = sec
        if sec != self._tp_bucket:
            self.throughput.append({"t": self._tp_bucket, "bytes": self._tp_bytes, "pkts": self._tp_pkts})
            # Fill any silent gap seconds with zeros so the chart scrolls smoothly
            gap = sec - self._tp_bucket - 1
            for i in range(min(gap, 5)):
                self.throughput.append({"t": self._tp_bucket + 1 + i, "bytes": 0, "pkts": 0})
            self._tp_bucket = sec
            self._tp_bytes = 0
            self._tp_pkts = 0
        self._tp_bytes += length
        self._tp_pkts += 1
