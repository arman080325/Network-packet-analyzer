"""
tests/test_all.py
-----------------
Unit tests for PacketAnalyzer, AnomalyDetector, and CryptoDetector.
Run with:  python -m pytest tests/ -v
"""

import os
import sys
import math

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.analyzer       import PacketAnalyzer
from core.anomaly        import AnomalyDetector
from core.crypto_detector import CryptoDetector


# ── Helpers ────────────────────────────────────────────────────────────────

def make_pkt(**kwargs):
    defaults = {
        "timestamp": "12:00:00.000",
        "protocol" : "TCP",
        "src_ip"   : "192.168.1.1",
        "dst_ip"   : "192.168.1.2",
        "src_port" : 54321,
        "dst_port" : 80,
        "flags"    : "ACK",
        "info"     : "",
        "payload"  : b"",
        "ttl"      : 64,
        "src_mac"  : "aa:bb:cc:dd:ee:ff",
        "length"   : 100,
    }
    defaults.update(kwargs)
    return defaults


# ── PacketAnalyzer tests ───────────────────────────────────────────────────

class TestPacketAnalyzer:

    def test_counts_packets(self):
        a = PacketAnalyzer()
        for _ in range(10):
            a.process(make_pkt())
        s = a.summary()
        assert s["total_packets"] == 10

    def test_protocol_breakdown(self):
        a = PacketAnalyzer()
        a.process(make_pkt(protocol="TCP"))
        a.process(make_pkt(protocol="UDP"))
        a.process(make_pkt(protocol="UDP"))
        s = a.summary()
        assert s["protocol_counts"]["UDP"] == 2
        assert s["protocol_counts"]["TCP"] == 1

    def test_total_bytes(self):
        a = PacketAnalyzer()
        a.process(make_pkt(length=500))
        a.process(make_pkt(length=300))
        s = a.summary()
        assert s["total_bytes"] == 800

    def test_top_src_ips(self):
        a = PacketAnalyzer()
        for _ in range(5):
            a.process(make_pkt(src_ip="10.0.0.1"))
        a.process(make_pkt(src_ip="10.0.0.2"))
        s = a.summary()
        assert s["top_src_ips"][0][0] == "10.0.0.1"

    def test_dns_queries_tracked(self):
        a = PacketAnalyzer()
        a.process(make_pkt(protocol="UDP", info="DNS query: example.com."))
        s = a.summary()
        assert "example.com." in s["dns_queries"]

    def test_connection_tracking(self):
        a = PacketAnalyzer()
        a.process(make_pkt(protocol="TCP", flags="SYN",     src_ip="1.1.1.1", src_port=1000, dst_port=80))
        a.process(make_pkt(protocol="TCP", flags="SYN|ACK", src_ip="1.1.1.1", src_port=1000, dst_port=80))
        a.process(make_pkt(protocol="TCP", flags="ACK",     src_ip="1.1.1.1", src_port=1000, dst_port=80))
        s = a.summary()
        assert s["connections_total"] >= 1


# ── AnomalyDetector tests ──────────────────────────────────────────────────

class TestAnomalyDetector:

    def test_no_alerts_normal_traffic(self):
        d = AnomalyDetector()
        for _ in range(10):
            d.check(make_pkt(protocol="TCP", flags="ACK"))
        assert len(d.get_new_alerts()) == 0

    def test_port_scan_detected(self):
        d = AnomalyDetector(port_scan_threshold=10)
        for port in range(1, 15):
            d.check(make_pkt(protocol="TCP", flags="SYN", dst_port=port, src_ip="1.2.3.4"))
        report = d.full_report()
        port_scan_alerts = [a for a in report["alerts"] if a["type"] == "PORT SCAN"]
        assert len(port_scan_alerts) >= 1

    def test_syn_flood_detected(self):
        import time
        d = AnomalyDetector(syn_threshold=5)
        for _ in range(10):
            d.check(make_pkt(protocol="TCP", flags="SYN", src_ip="9.9.9.9"))
        all_alerts = d.full_report()["alerts"]
        flood_alerts = [a for a in all_alerts if a["type"] == "SYN FLOOD"]
        assert len(flood_alerts) >= 1

    def test_xmas_scan_detected(self):
        d = AnomalyDetector()
        d.check(make_pkt(protocol="TCP", flags="FIN|PSH|URG", src_ip="5.5.5.5"))
        alerts = d.get_new_alerts()
        assert any(a["type"] == "XMAS SCAN" for a in alerts)

    def test_arp_spoofing_detected(self):
        d = AnomalyDetector()
        d.check(make_pkt(protocol="ARP", src_ip="192.168.1.1", src_mac="aa:bb:cc:dd:ee:01"))
        d.check(make_pkt(protocol="ARP", src_ip="192.168.1.1", src_mac="ff:ee:dd:cc:bb:02"))
        report = d.full_report()
        assert "192.168.1.1" in report["arp_anomalies"]

    def test_low_ttl_flagged(self):
        d = AnomalyDetector()
        d.check(make_pkt(ttl=2))
        alerts = d.get_new_alerts()
        assert any(a["type"] == "LOW TTL" for a in alerts)


# ── CryptoDetector tests ───────────────────────────────────────────────────

class TestCryptoDetector:

    def test_tls_detected(self):
        c = CryptoDetector()
        c.inspect(make_pkt(payload=b"\x16\x03\x01" + b"\x00" * 50, dst_port=443))
        r = c.report()
        assert r["encrypted_payloads"] >= 1

    def test_high_entropy_detected(self):
        c = CryptoDetector()
        c.inspect(make_pkt(payload=os.urandom(1024), dst_port=9999))
        r = c.report()
        assert r["high_entropy_payloads"] >= 1

    def test_ssh_banner_detected(self):
        c = CryptoDetector()
        c.inspect(make_pkt(payload=b"SSH-2.0-OpenSSH_8.9\r\n" + os.urandom(30), dst_port=22))
        r = c.report()
        assert "SSH" in r["protocol_breakdown"]

    def test_fernet_detected(self):
        c = CryptoDetector()
        c.inspect(make_pkt(payload=b"\x80" + os.urandom(72), dst_port=8080))
        r = c.report()
        assert "Fernet" in r["protocol_breakdown"]

    def test_port_inference(self):
        c = CryptoDetector()
        c.inspect(make_pkt(payload=b"", dst_port=443))
        r = c.report()
        assert r["encrypted_payloads"] >= 1

    def test_entropy_calculation(self):
        """All-zero bytes → entropy = 0; random bytes → entropy ≈ 8."""
        c = CryptoDetector()
        zero_entropy = c._shannon_entropy(b"\x00" * 100)
        rand_entropy = c._shannon_entropy(os.urandom(1000))
        assert zero_entropy == 0.0
        assert rand_entropy > 7.0

    def test_no_false_positives_on_empty(self):
        c = CryptoDetector()
        c.inspect(make_pkt(payload=b"", dst_port=12345))
        r = c.report()
        # No payload, no known port → should not register encrypted payload
        assert r["encrypted_payloads"] == 0


# ── netinfo tests ──────────────────────────────────────────────────────────

class TestNetInfo:
    def test_classify_private(self):
        from core.netinfo import classify_ip
        assert classify_ip("192.168.1.1") == "private"
        assert classify_ip("10.0.0.5") == "private"

    def test_classify_public(self):
        from core.netinfo import classify_ip
        assert classify_ip("8.8.8.8") == "public"

    def test_classify_loopback_multicast(self):
        from core.netinfo import classify_ip
        assert classify_ip("127.0.0.1") == "loopback"
        assert classify_ip("224.0.0.1") == "multicast"

    def test_service_and_risky(self):
        from core.netinfo import service_name, risky_port, is_internal
        assert service_name(443) == "HTTPS"
        assert service_name(99999) == ""
        assert risky_port(4444) is not None
        assert risky_port(443) is None
        assert is_internal("192.168.1.1") is True
        assert is_internal("8.8.8.8") is False


# ── ThreatScorer tests ─────────────────────────────────────────────────────

class TestThreatScorer:
    def test_register_and_rank(self):
        from core.threat import ThreatScorer
        t = ThreatScorer()
        t.register({"type": "SYN FLOOD", "src": "10.0.0.99"})
        t.register({"type": "PORT SCAN", "src": "10.0.0.99"})
        top = t.top()
        assert top and top[0]["ip"] == "10.0.0.99"
        assert top[0]["score"] > 0

    def test_classification_bands(self):
        from core.threat import ThreatScorer
        t = ThreatScorer()
        assert t.classify(5) == "clean"
        assert t.classify(40) == "suspicious"
        assert t.classify(100) == "malicious"

    def test_ignores_unknown_src(self):
        from core.threat import ThreatScorer
        t = ThreatScorer()
        t.register({"type": "PORT SCAN", "src": ""})
        assert t.top() == []


# ── New anomaly detectors ──────────────────────────────────────────────────

class TestNewDetectors:
    def test_credential_exposure(self):
        d = AnomalyDetector()
        d.check(make_pkt(protocol="TCP", dst_port=80, flags="ACK|PSH",
                         payload=b"POST /login HTTP/1.1\r\npassword=hunter2"))
        alerts = d.get_new_alerts()
        assert any(a["type"] == "CREDENTIAL EXPOSURE" for a in alerts)

    def test_dns_tunneling(self):
        d = AnomalyDetector()
        long_label = "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8.exfil.evil.com"
        d.check(make_pkt(protocol="UDP", dst_port=53,
                         info=f"DNS query: {long_label}"))
        alerts = d.get_new_alerts()
        assert any(a["type"] == "DNS TUNNELING" for a in alerts)

    def test_suspicious_dst_port(self):
        d = AnomalyDetector()
        d.check(make_pkt(protocol="TCP", dst_port=4444, src_port=51000, flags="ACK"))
        alerts = d.get_new_alerts()
        assert any(a["type"] == "SUSPICIOUS PORT" for a in alerts)

    def test_ephemeral_src_port_not_flagged(self):
        # 54321 as an ephemeral SOURCE port must not raise SUSPICIOUS PORT
        d = AnomalyDetector()
        d.check(make_pkt(protocol="TCP", src_port=54321, dst_port=443, flags="ACK"))
        alerts = d.get_new_alerts()
        assert not any(a["type"] == "SUSPICIOUS PORT" for a in alerts)


# ── Analyzer enrichment ────────────────────────────────────────────────────

class TestAnalyzerEnrichment:
    def test_flows_and_services(self):
        a = PacketAnalyzer()
        for _ in range(3):
            a.process(make_pkt(protocol="TCP", src_ip="192.168.1.10",
                               dst_ip="8.8.8.8", dst_port=443, length=200))
        s = a.summary()
        assert s["top_flows"]
        assert any(svc == "HTTPS" for svc, _ in s["top_services"])
        assert "private" in s["ipclass_counts"]

    def test_retransmission_detection(self):
        a = PacketAnalyzer()
        pkt = make_pkt(protocol="TCP", src_ip="1.1.1.1", dst_ip="2.2.2.2",
                       dst_port=80, seq=1000, length=100, payload=b"x" * 100)
        a.process(dict(pkt))
        a.process(dict(pkt))  # identical seq+len => retransmission
        assert a.summary()["retransmissions"] >= 1


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])