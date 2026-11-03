"""tests/test_live_engine.py
Tests for core/live_engine.py and production NDR telemetry features.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.live_engine import LiveNetworkEngine, MITRE_TACTICS, OUI_VENDORS

class TestLiveEngine(unittest.TestCase):
    def setUp(self):
        self.engine = LiveNetworkEngine()

    def test_active_adapter_detection(self):
        adapter = self.engine.active_adapter
        self.assertIsInstance(adapter, dict)
        self.assertIn("name", adapter)
        self.assertIn("ip", adapter)
        self.assertIn("gateway", adapter)
        self.assertIn("cidr", adapter)
        self.assertTrue(len(adapter["ip"]) > 0)

    def test_mitre_tactics_coverage(self):
        self.assertGreaterEqual(len(MITRE_TACTICS), 7)
        ids = list(MITRE_TACTICS.keys())
        self.assertIn("T1046", ids)
        self.assertIn("T1071.001", ids)
        self.assertIn("T1071.004", ids)
        self.assertIn("T1571", ids)
        self.assertIn("T1041", ids)

    def test_oui_vendors(self):
        self.assertEqual(OUI_VENDORS.get("C8:4F:86"), "Cisco / Meraki")
        self.assertEqual(OUI_VENDORS.get("F4:34:F0"), "Apple Inc.")
        self.assertEqual(OUI_VENDORS.get("9C:28:F7"), "Samsung Electronics")

    def test_sample_active_sockets(self):
        conns = self.engine.sample_active_sockets()
        self.assertIsInstance(conns, list)
        if conns:
            first = conns[0]
            self.assertIn("pid", first)
            self.assertIn("name", first)
            self.assertIn("laddr", first)
            self.assertIn("raddr", first)

    def test_live_packet_generation(self):
        pkt = self.engine.generate_live_packet_frame()
        self.assertIsInstance(pkt, dict)
        self.assertIn("src", pkt)
        self.assertIn("dst", pkt)
        self.assertIn("protocol", pkt)
        self.assertIn("process", pkt)
        self.assertIn("length", pkt)
        self.assertGreater(pkt["length"], 0)

    def test_pcap_binary_export(self):
        pcap_data = self.engine.export_libpcap_binary()
        self.assertIsInstance(pcap_data, bytes)
        # Check standard PCAP magic number: 0xa1b2c3d4 (little endian: \xd4\xc3\xb2\xa1)
        self.assertTrue(pcap_data.startswith(b"\xd4\xc3\xb2\xa1"))
        self.assertGreater(len(pcap_data), 24)

    def test_iocs_json_export(self):
        iocs = self.engine.export_iocs_json()
        self.assertIsInstance(iocs, dict)
        self.assertIn("format", iocs)
        self.assertEqual(iocs["format"], "STIX-2.1-like-IOC-Feed")
        self.assertIn("network_context", iocs)
        self.assertIn("indicators", iocs)

if __name__ == "__main__":
    unittest.main()
