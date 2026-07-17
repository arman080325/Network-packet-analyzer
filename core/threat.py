"""
core/threat.py
--------------
Per-host threat scoring engine.

Every anomaly the AnomalyDetector raises is fed here and converted into a
weighted, decaying threat score per source IP. This turns a flat stream of
alerts into a ranked "who is the biggest problem on my network right now"
leaderboard — the single most useful view for a SOC analyst, and the data
behind the dashboard's threat board and colour-coded network graph.

Scoring model
-------------
  • Each alert type carries a base weight (see WEIGHTS).
  • Repeated alerts of the same type from the same host add with mild
    diminishing returns, so one noisy detector can't dominate.
  • Scores decay over time (half-life ~90s) so a host that misbehaved once
    and went quiet slowly drops back down — recent behaviour matters most.
  • A score maps to a classification band: clean / suspicious / malicious.
"""

import time
import math
from collections import defaultdict


# Base points per alert type
WEIGHTS = {
    "SYN FLOOD":            40,
    "PORT SCAN":           25,
    "ARP SPOOFING":        45,
    "XMAS SCAN":           20,
    "NULL SCAN":           20,
    "ICMP FLOOD":          18,
    "DNS TUNNELING":       30,
    "CREDENTIAL EXPOSURE": 35,
    "C2 BEACONING":        38,
    "SUSPICIOUS PORT":     22,
    "LARGE PACKET":        10,
    "LOW TTL":              5,
}

DEFAULT_WEIGHT = 12
HALF_LIFE_SEC  = 90.0          # score halves every 90 seconds of silence

# Classification thresholds (post-decay score)
SUSPICIOUS_AT = 25
MALICIOUS_AT  = 70


class ThreatScorer:

    def __init__(self):
        # ip -> {"score": float, "last": ts, "hits": {type: count}, "types": set}
        self._hosts = defaultdict(
            lambda: {"score": 0.0, "last": time.time(), "hits": defaultdict(int), "types": set()}
        )

    # ── Public API ─────────────────────────────────────────────────────────

    def register(self, alert: dict):
        """Fold an anomaly alert into the offending host's score."""
        ip = alert.get("src") or "unknown"
        if not ip or ip == "unknown":
            return
        atype = alert.get("type", "")
        now   = time.time()

        host = self._hosts[ip]
        self._decay(host, now)

        host["hits"][atype] += 1
        host["types"].add(atype)

        base = WEIGHTS.get(atype, DEFAULT_WEIGHT)
        # Diminishing returns on repeats of the same alert type
        n = host["hits"][atype]
        host["score"] += base / math.sqrt(n)
        host["last"] = now

    def classify(self, score: float) -> str:
        if score >= MALICIOUS_AT:
            return "malicious"
        if score >= SUSPICIOUS_AT:
            return "suspicious"
        return "clean"

    def score_for(self, ip: str) -> float:
        host = self._hosts.get(ip)
        if not host:
            return 0.0
        self._decay(host, time.time())
        return round(host["score"], 1)

    def top(self, n=10) -> list:
        """Return the top-n hosts ranked by current (decayed) score."""
        now = time.time()
        rows = []
        for ip, host in self._hosts.items():
            self._decay(host, now)
            if host["score"] < 1:
                continue
            rows.append({
                "ip":       ip,
                "score":    round(host["score"], 1),
                "level":    self.classify(host["score"]),
                "types":    sorted(host["types"]),
                "hits":     sum(host["hits"].values()),
            })
        rows.sort(key=lambda r: r["score"], reverse=True)
        return rows[:n]

    def report(self) -> dict:
        rows = self.top(50)
        return {
            "hosts_tracked": len(self._hosts),
            "malicious":     sum(1 for r in rows if r["level"] == "malicious"),
            "suspicious":    sum(1 for r in rows if r["level"] == "suspicious"),
            "top":           rows,
        }

    # ── Internal ───────────────────────────────────────────────────────────

    def _decay(self, host, now):
        dt = now - host["last"]
        if dt <= 0:
            return
        host["score"] *= 0.5 ** (dt / HALF_LIFE_SEC)
        host["last"] = now
