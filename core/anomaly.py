"""
core/anomaly.py
---------------
Real-time anomaly and attack detection engine.

Detects:
  • SYN Flood          — high rate of SYN packets from one source
  • Port Scan          — one source hitting many destination ports
  • ICMP Flood         — excessive ICMP echo requests
  • ARP Spoofing       — same IP announced by multiple MACs
  • Null / Xmas scans  — suspicious TCP flag combinations
  • Large payload spike — abnormally large single packets
  • TTL anomaly        — packets with suspiciously low TTL
  • DNS Tunneling      — long / high-entropy DNS labels (covert channel)
  • Credential Exposure — cleartext logins over HTTP / FTP / Telnet
  • C2 Beaconing       — regular-interval contact to a single external host
  • Suspicious Port    — traffic to known backdoor / malware ports
"""

import re
import time
import math
from collections import defaultdict, deque, Counter
from datetime import datetime

from core.netinfo import risky_port, is_internal


# ── Severity levels ────────────────────────────────────────────────────────
INFO     = "INFO"
WARNING  = "WARNING"
CRITICAL = "CRITICAL"

# Cleartext-credential signatures (well-known, low false-positive)
_CRED_PATTERNS = [
    (re.compile(rb"Authorization:\s*Basic\s+([A-Za-z0-9+/=]+)", re.I), "HTTP Basic auth"),
    (re.compile(rb"(?:^|\r\n)USER\s+(\S+)", re.I),                     "FTP USER"),
    (re.compile(rb"(?:^|\r\n)PASS\s+(\S+)", re.I),                     "FTP PASS"),
    (re.compile(rb"password=([^&\s]+)", re.I),                         "HTTP form password"),
    (re.compile(rb"passwd=([^&\s]+)", re.I),                           "HTTP form password"),
]


def _entropy(s: str) -> float:
    if not s:
        return 0.0
    counts = Counter(s)
    n = len(s)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


class AnomalyDetector:

    def __init__(self, syn_threshold=100, port_scan_threshold=20):
        self.syn_threshold       = syn_threshold
        self.port_scan_threshold = port_scan_threshold

        self._syn_counts   = defaultdict(list)   # src_ip -> [timestamps]
        self._port_targets = defaultdict(set)    # src_ip -> {dst_ports}
        self._icmp_counts  = defaultdict(list)
        self._arp_table    = defaultdict(set)    # ip -> {macs}
        self._dns_names    = defaultdict(int)    # domain -> query count

        # C2 beaconing: (src,dst) -> deque of contact timestamps
        self._beacon       = defaultdict(lambda: deque(maxlen=12))
        self._beacon_fired = set()

        self._all_alerts = []
        self._new_alerts = deque()
        self.total_checked = 0

    # ── Public API ─────────────────────────────────────────────────────────

    def check(self, pkt: dict):
        self.total_checked += 1
        proto   = pkt.get("protocol", "")
        src     = pkt.get("src_ip", "")
        dst     = pkt.get("dst_ip", "")
        flags   = pkt.get("flags", "")
        dport   = pkt.get("dst_port")
        length  = pkt.get("length", 0)
        ttl     = pkt.get("ttl")
        info    = pkt.get("info", "")
        payload = pkt.get("payload", b"") or b""
        now     = time.time()

        # 1. SYN Flood
        if proto == "TCP" and "SYN" in flags and "ACK" not in flags:
            self._syn_counts[src].append(now)
            self._syn_counts[src] = [t for t in self._syn_counts[src] if now - t <= 1.0]
            count = len(self._syn_counts[src])
            if count >= self.syn_threshold:
                self._raise(CRITICAL, "SYN FLOOD",
                            f"{src} sent {count} SYN packets in 1s -> possible DDoS", src, dst)

        # 2. Port Scan
        if proto in ("TCP", "UDP") and src and dport:
            self._port_targets[src].add(dport)
            unique = len(self._port_targets[src])
            if unique == self.port_scan_threshold:
                self._raise(WARNING, "PORT SCAN",
                            f"{src} probed {unique} unique ports -> possible reconnaissance", src, dst)
            elif unique > self.port_scan_threshold and unique % 10 == 0:
                self._raise(CRITICAL, "PORT SCAN", f"{src} now probed {unique} ports", src, dst)

        # 3. Null Scan
        if proto == "TCP" and flags == "":
            self._raise(WARNING, "NULL SCAN",
                        f"TCP packet with no flags from {src} -> stealth scan", src, dst)

        # 4. Xmas Scan
        if proto == "TCP" and all(f in flags for f in ("FIN", "PSH", "URG")):
            self._raise(WARNING, "XMAS SCAN", f"Xmas scan detected from {src}", src, dst)

        # 5. ICMP Flood
        if proto == "ICMP":
            self._icmp_counts[src].append(now)
            self._icmp_counts[src] = [t for t in self._icmp_counts[src] if now - t <= 1.0]
            if len(self._icmp_counts[src]) >= 50:
                self._raise(WARNING, "ICMP FLOOD",
                            f"{src} sent {len(self._icmp_counts[src])} ICMP packets/s", src, dst)

        # 6. ARP Spoofing
        if proto == "ARP":
            mac = pkt.get("src_mac", "")
            if src and mac:
                self._arp_table[src].add(mac)
                if len(self._arp_table[src]) > 1:
                    macs = ", ".join(self._arp_table[src])
                    self._raise(CRITICAL, "ARP SPOOFING",
                                f"IP {src} seen from multiple MACs: {macs}", src, dst)

        # 7. Large Packet Anomaly
        if length > 8192 and proto not in ("TCP",):
            self._raise(INFO, "LARGE PACKET",
                        f"{proto} packet {length} bytes from {src} -> possible exfil/amplification", src, dst)

        # 8. TTL Anomaly
        if ttl is not None and ttl <= 5:
            self._raise(INFO, "LOW TTL",
                        f"Packet from {src} has TTL={ttl} -> possible traceroute or loop", src, dst)

        # 9. DNS Tunneling — long, high-entropy query labels
        if info.startswith("DNS query:"):
            qname = info.replace("DNS query:", "").strip().rstrip(".")
            self._dns_names[qname] += 1
            labels = qname.split(".")
            longest = max((len(l) for l in labels), default=0)
            ent = _entropy(qname)
            if longest >= 30 and ent >= 3.8:
                self._raise(WARNING, "DNS TUNNELING",
                            f"Suspicious DNS label from {src} (len={longest}, entropy={ent:.1f}) -> covert channel?",
                            src, dst)

        # 10. Cleartext Credential Exposure (HTTP/FTP/Telnet)
        if payload and proto == "TCP":
            for pat, label in _CRED_PATTERNS:
                if pat.search(payload):
                    self._raise(CRITICAL, "CREDENTIAL EXPOSURE",
                                f"Cleartext credentials ({label}) {src} -> {dst} -> sniffable secret", src, dst)
                    break

        # 11. C2 Beaconing — regular-interval contact to one external host
        if proto in ("TCP", "UDP") and src and dst and is_internal(src) and not is_internal(dst):
            key = (src, dst)
            dq = self._beacon[key]
            dq.append(now)
            if len(dq) >= 6 and key not in self._beacon_fired:
                gaps = [dq[i + 1] - dq[i] for i in range(len(dq) - 1)]
                mean = sum(gaps) / len(gaps)
                if mean > 0.05:  # ignore floods; beacons are spaced out
                    var = sum((g - mean) ** 2 for g in gaps) / len(gaps)
                    jitter = (var ** 0.5) / mean if mean else 1
                    if jitter < 0.15:  # very regular cadence
                        self._beacon_fired.add(key)
                        self._raise(WARNING, "C2 BEACONING",
                                    f"{src} contacts {dst} every ~{mean:.1f}s (jitter {jitter:.0%}) -> beacon-like", src, dst)

        # 12. Suspicious / backdoor port — only the destination (the service
        # being contacted); ephemeral source ports would be false positives.
        label = risky_port(dport)
        if label:
            self._raise(WARNING, "SUSPICIOUS PORT",
                        f"{src} -> {dst}:{dport} -> {label}", src, dst)

    def get_new_alerts(self):
        alerts = list(self._new_alerts)
        self._new_alerts.clear()
        return alerts

    def full_report(self) -> dict:
        counts = defaultdict(int)
        for a in self._all_alerts:
            counts[a["type"]] += 1
        return {
            "total_alerts":    len(self._all_alerts),
            "by_type":         dict(counts),
            "alerts":          self._all_alerts[-50:],
            "unique_scanners": list(self._port_targets.keys()),
            "arp_anomalies":   {k: list(v) for k, v in self._arp_table.items() if len(v) > 1},
        }

    # ── Internal ───────────────────────────────────────────────────────────

    def _raise(self, severity, atype, message, src="", dst=""):
        now = time.time()
        key = f"{atype}:{src}"
        for existing in self._all_alerts[-12:]:
            if existing.get("_key") == key and (now - existing.get("_ts", 0)) < 2:
                return
        alert = {
            "_key": key, "_ts": now,
            "severity": severity, "type": atype, "message": message,
            "src": src, "dst": dst,
            "time": datetime.now().strftime("%H:%M:%S"),
        }
        self._all_alerts.append(alert)
        self._new_alerts.append(alert)
