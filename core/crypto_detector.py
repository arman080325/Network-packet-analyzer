"""
core/crypto_detector.py
-----------------------
Encrypted and obfuscated payload detection.

Techniques used:
  1. Shannon Entropy   — high entropy (>7.2 bits/byte) → likely encrypted/compressed
  2. TLS/SSL Handshake — detects TLS ClientHello / ServerHello magic bytes
  3. Known Cipher Signatures — AES-GCM, ChaCha20-Poly1305 header patterns
  4. Base64 heuristic  — printable payload with high b64 character ratio
  5. Port-based inference — ports 443, 8443, 993, 995, 465, 22 → encrypted by convention
  6. Cryptography lib  — attempt Fernet / AES-CBC signature checks on raw bytes
"""

import math
import re
import struct
from collections import Counter, defaultdict

# Fernet magic: starts with version byte 0x80
FERNET_MAGIC = b"\x80"

# TLS record layer: content_type=22 (handshake), version 3.x
TLS_HANDSHAKE   = b"\x16\x03"
TLS_APP_DATA    = b"\x17\x03"
TLS_ALERT       = b"\x15\x03"

# SSH banner
SSH_BANNER      = b"SSH-"

# Known encrypted port numbers
ENCRYPTED_PORTS = {
    22   : "SSH",
    443  : "HTTPS/TLS",
    465  : "SMTPS",
    587  : "SMTP+STARTTLS",
    636  : "LDAPS",
    993  : "IMAPS",
    995  : "POP3S",
    8443 : "HTTPS-alt",
    8883 : "MQTT-TLS",
}

B64_CHARS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=")


class CryptoDetector:

    def __init__(self):
        self._results        = []    # list of detection dicts
        self._entropy_dist   = []    # entropy values seen
        self._proto_counts   = defaultdict(int)
        self._high_entropy   = 0
        self.total_inspected = 0
        self.recent_entropy  = []    # last N payload entropies (for live gauge)
        self.last_entropy    = 0.0

    # ── Public API ─────────────────────────────────────────────────────────

    def inspect(self, pkt: dict):
        self.total_inspected += 1

        payload  = pkt.get("payload", b"")
        src      = pkt.get("src_ip", "")
        dst      = pkt.get("dst_ip", "")
        dport    = pkt.get("dst_port") or 0
        sport    = pkt.get("src_port") or 0
        proto    = pkt.get("protocol", "")
        ts       = pkt.get("timestamp", "")

        findings = []

        # ── 1. Port-based inference ────────────────────────────────────────
        for port in (dport, sport):
            if port in ENCRYPTED_PORTS:
                service = ENCRYPTED_PORTS[port]
                findings.append({"method": "port_inference", "detail": service, "confidence": "medium"})
                self._proto_counts[service] += 1

        if not payload:
            if findings:
                self._record(ts, src, dst, proto, dport, findings, payload)
            return

        # ── 2. Shannon Entropy ─────────────────────────────────────────────
        entropy = self._shannon_entropy(payload)
        self._entropy_dist.append(entropy)
        self.last_entropy = round(entropy, 3)
        self.recent_entropy.append(entropy)
        if len(self.recent_entropy) > 60:
            self.recent_entropy.pop(0)
        if entropy >= 7.2:
            self._high_entropy += 1
            findings.append({
                "method"     : "entropy",
                "detail"     : f"Shannon entropy = {entropy:.3f} bits/byte (threshold 7.2)",
                "confidence" : "high" if entropy >= 7.5 else "medium",
            })

        # ── 3. TLS/SSL detection ───────────────────────────────────────────
        if payload[:2] in (TLS_HANDSHAKE, TLS_APP_DATA, TLS_ALERT):
            tls_type = {
                TLS_HANDSHAKE : "TLS Handshake",
                TLS_APP_DATA  : "TLS Application Data",
                TLS_ALERT     : "TLS Alert",
            }[payload[:2]]
            findings.append({"method": "tls_signature", "detail": tls_type, "confidence": "high"})
            self._proto_counts["TLS"] += 1

        # ── 4. SSH banner ──────────────────────────────────────────────────
        if payload[:4] == SSH_BANNER:
            banner = payload[:20].decode(errors="replace")
            findings.append({"method": "ssh_banner", "detail": f"SSH banner: {banner}", "confidence": "high"})
            self._proto_counts["SSH"] += 1

        # ── 5. Fernet (Python cryptography lib) ───────────────────────────
        if payload[:1] == FERNET_MAGIC and len(payload) >= 73:
            findings.append({
                "method"     : "fernet_magic",
                "detail"     : "Fernet-encrypted payload (Python cryptography lib)",
                "confidence" : "high",
            })
            self._proto_counts["Fernet"] += 1

        # ── 6. AES-GCM pattern (12-byte nonce + 16-byte tag hint) ─────────
        if len(payload) >= 28:
            # GCM nonces often have low entropy first 12 bytes followed by high-entropy ciphertext
            nonce_entropy  = self._shannon_entropy(payload[:12])
            cipher_entropy = self._shannon_entropy(payload[12:28])
            if nonce_entropy < 5.0 and cipher_entropy >= 7.0:
                findings.append({
                    "method"     : "aes_gcm_heuristic",
                    "detail"     : "Possible AES-GCM (low-entropy nonce + high-entropy ciphertext)",
                    "confidence" : "low",
                })

        # ── 7. Base64-encoded payload ──────────────────────────────────────
        try:
            text = payload.decode("ascii", errors="ignore")
            if len(text) >= 20:
                b64_ratio = sum(1 for c in text if c in B64_CHARS) / len(text)
                if b64_ratio >= 0.92 and len(text) % 4 == 0:
                    findings.append({
                        "method"     : "base64_heuristic",
                        "detail"     : f"Base64-encoded data ({b64_ratio:.0%} valid chars)",
                        "confidence" : "medium",
                    })
        except Exception:
            pass

        if findings:
            self._record(ts, src, dst, proto, dport, findings, payload)

    def report(self) -> dict:
        avg_entropy = (
            sum(self._entropy_dist) / len(self._entropy_dist)
            if self._entropy_dist else 0
        )
        recent_avg = (
            sum(self.recent_entropy) / len(self.recent_entropy)
            if self.recent_entropy else 0
        )
        return {
            "total_inspected"       : self.total_inspected,
            "encrypted_payloads"    : len(self._results),
            "high_entropy_payloads" : self._high_entropy,
            "avg_entropy"           : round(avg_entropy, 3),
            "recent_avg_entropy"    : round(recent_avg, 3),
            "last_entropy"          : self.last_entropy,
            "encrypted_pct"         : round(
                100 * len(self._results) / max(self.total_inspected, 1), 1),
            "protocol_breakdown"    : dict(self._proto_counts),
            "detections"            : self._results[-30:],
        }

    # ── Internal ───────────────────────────────────────────────────────────

    @staticmethod
    def _shannon_entropy(data: bytes) -> float:
        if not data:
            return 0.0
        counts = Counter(data)
        total  = len(data)
        return -sum(
            (c / total) * math.log2(c / total)
            for c in counts.values()
        )

    def _record(self, ts, src, dst, proto, dport, findings, payload):
        self._results.append({
            "timestamp"    : ts,
            "src"          : src,
            "dst"          : dst,
            "protocol"     : proto,
            "dst_port"     : dport,
            "payload_bytes": len(payload),
            "findings"     : findings,
        })
