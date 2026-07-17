"""
core/sniffer.py
---------------
Live capture and offline pcap reading using Scapy.
Wraps scapy.sniff() with a clean callback interface.
"""

import socket
from datetime import datetime

from scapy.all import (
    sniff, get_if_list, conf,
    IP, IPv6, TCP, UDP, ICMP, ICMPv6EchoRequest,
    ARP, DNS, Raw, Ether
)
from scapy.error import Scapy_Exception


class PacketSniffer:
    """
    Captures packets live or reads from a .pcap file.
    Parses each packet into a plain dict (PacketSummary) and
    fires the user-supplied callback.
    """

    def __init__(
        self,
        interface=None,
        bpf_filter="",
        packet_count=0,
        output_file=None,
        offline=None
    ):
        self.interface   = interface or self._auto_interface()
        self.bpf_filter  = bpf_filter
        self.packet_count = packet_count
        self.output_file = output_file
        self.offline     = offline
        self._stop       = False
        self._packets    = []

    # ── Public API ─────────────────────────────────────────────────────────

    def start(self, callback):
        """Begin sniffing; call callback(summary_dict) for each packet."""
        self._callback = callback
        kwargs = dict(
            prn=self._handle,
            store=bool(self.output_file),
            count=self.packet_count or 0,
        )
        if self.offline:
            kwargs["offline"] = self.offline
        else:
            kwargs["iface"]   = self.interface
            if self.bpf_filter:
                kwargs["filter"] = self.bpf_filter

        try:
            captured = sniff(**kwargs)
            if self.output_file and captured:
                from scapy.utils import wrpcap
                wrpcap(self.output_file, captured)
        except Scapy_Exception as e:
            raise RuntimeError(f"Scapy error: {e}")

    def stop(self):
        self._stop = True

    # ── Internal ───────────────────────────────────────────────────────────

    def _handle(self, pkt):
        if self._stop:
            return
        summary = self._parse(pkt)
        if summary:
            self._callback(summary)

    def _parse(self, pkt):
        """Convert a Scapy packet into a flat dict."""
        s = {
            "timestamp"  : datetime.now().strftime("%H:%M:%S.%f")[:-3],
            "protocol"   : "UNKNOWN",
            "src_ip"     : "",
            "dst_ip"     : "",
            "src_port"   : None,
            "dst_port"   : None,
            "length"     : len(pkt),
            "flags"      : "",
            "payload"    : b"",
            "ttl"        : None,
            "seq"        : None,
            "info"       : "",
            "layers"     : [],
        }

        # Layer 2
        if pkt.haslayer(Ether):
            s["src_mac"] = pkt[Ether].src
            s["dst_mac"] = pkt[Ether].dst
            s["layers"].append("Ethernet")

        # Layer 3
        if pkt.haslayer(IP):
            s["src_ip"]   = pkt[IP].src
            s["dst_ip"]   = pkt[IP].dst
            s["ttl"]      = pkt[IP].ttl
            s["layers"].append("IPv4")
        elif pkt.haslayer(IPv6):
            s["src_ip"]   = pkt[IPv6].src
            s["dst_ip"]   = pkt[IPv6].dst
            s["layers"].append("IPv6")

        # ARP
        if pkt.haslayer(ARP):
            arp = pkt[ARP]
            s["protocol"] = "ARP"
            s["src_ip"]   = arp.psrc
            s["dst_ip"]   = arp.pdst
            s["info"]     = f"op={arp.op} (1=req,2=reply)"
            s["layers"].append("ARP")
            return s

        # Layer 4
        if pkt.haslayer(TCP):
            tcp = pkt[TCP]
            s["protocol"] = "TCP"
            s["src_port"] = tcp.sport
            s["dst_port"] = tcp.dport
            s["flags"]    = self._tcp_flags(tcp.flags)
            s["seq"]      = int(tcp.seq)
            s["window"]   = int(tcp.window)
            s["layers"].append("TCP")

            # Application hints
            if tcp.dport == 443 or tcp.sport == 443:
                s["info"] = "HTTPS/TLS"
            elif tcp.dport == 80 or tcp.sport == 80:
                s["info"] = "HTTP"
            elif tcp.dport == 22 or tcp.sport == 22:
                s["info"] = "SSH"
            elif tcp.dport == 21 or tcp.sport == 21:
                s["info"] = "FTP"

        elif pkt.haslayer(UDP):
            udp = pkt[UDP]
            s["protocol"] = "UDP"
            s["src_port"] = udp.sport
            s["dst_port"] = udp.dport
            s["layers"].append("UDP")

            if udp.dport == 53 or udp.sport == 53:
                s["info"] = "DNS"
                if pkt.haslayer(DNS):
                    dns = pkt[DNS]
                    if dns.qd:
                        try:
                            s["info"] = f"DNS query: {dns.qd.qname.decode()}"
                        except Exception:
                            pass
            elif udp.dport == 67 or udp.dport == 68:
                s["info"] = "DHCP"

        elif pkt.haslayer(ICMP):
            icmp = pkt[ICMP]
            s["protocol"] = "ICMP"
            s["layers"].append("ICMP")
            type_map = {0: "Echo Reply", 3: "Dest Unreachable",
                        8: "Echo Request", 11: "TTL Exceeded"}
            s["info"] = type_map.get(icmp.type, f"type={icmp.type}")

        elif pkt.haslayer(ICMPv6EchoRequest):
            s["protocol"] = "ICMPv6"
            s["layers"].append("ICMPv6")

        # Raw payload
        if pkt.haslayer(Raw):
            s["payload"] = bytes(pkt[Raw].load)

        return s

    @staticmethod
    def _tcp_flags(flags):
        flag_map = {
            "F": "FIN", "S": "SYN", "R": "RST",
            "P": "PSH", "A": "ACK", "U": "URG",
            "E": "ECE", "C": "CWR",
        }
        active = []
        flags_str = str(flags)
        for k, v in flag_map.items():
            if k in flags_str:
                active.append(v)
        return "|".join(active) if active else str(flags)

    @staticmethod
    def _auto_interface():
        try:
            ifaces = get_if_list()
            for iface in ifaces:
                if iface not in ("lo", "any") and not iface.startswith("docker"):
                    return iface
            return conf.iface
        except Exception:
            return "eth0"
