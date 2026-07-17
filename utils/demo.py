"""
utils/demo.py
-------------
Simulated traffic generator — no root, no live interface required.

Two entry points:
  • run_demo(...)            one-shot scripted demo for the CLI summary
  • demo_packet_stream()     infinite generator of realistic packets with
                             periodic attack bursts, used by the live
                             dashboard server so the UI always has motion.

Exercises every code path: TCP/UDP/ICMP/ARP/DNS, TLS detection,
high-entropy payloads, port scans, SYN floods, ARP spoofing, Xmas/Null
scans, DNS tunneling, cleartext credential exposure and C2 beaconing.
"""

import os
import time
import random
import base64
from datetime import datetime


# ── Realistic host inventory ────────────────────────────────────────────────
LAN_HOSTS = ["192.168.1.10", "192.168.1.11", "192.168.1.23", "192.168.1.50"]
SERVERS = {
    "142.250.80.46":  443,   # google
    "93.184.216.34":  80,    # example.com
    "151.101.1.69":   443,   # fastly
    "140.82.121.4":   443,   # github
    "8.8.8.8":        53,     # dns
}
DNS_DOMAINS = ["google.com.", "github.com.", "stackoverflow.com.",
               "youtube.com.", "cloudflare.com.", "wikipedia.org.",
               "amazonaws.com.", "microsoft.com."]


def _make_pkt(protocol, src_ip, dst_ip, src_port=None, dst_port=None,
              flags="", info="", payload=b"", ttl=64, src_mac="", length=None, seq=None):
    return {
        "timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3],
        "protocol":  protocol,
        "src_ip":    src_ip,
        "dst_ip":    dst_ip,
        "src_port":  src_port,
        "dst_port":  dst_port,
        "flags":     flags,
        "info":      info,
        "payload":   payload,
        "ttl":       ttl,
        "seq":       seq,
        "src_mac":   src_mac,
        "layers":    [],
        "length":    length or (random.randint(60, 1500) if not payload else 40 + len(payload)),
    }


def _random_ip():
    return f"{random.randint(1,254)}.{random.randint(0,254)}.{random.randint(0,254)}.{random.randint(1,254)}"


def _tls_hello():
    return b"\x16\x03\x01" + b"\x00\x00" + os.urandom(32)


def _tls_appdata(n=256):
    return b"\x17\x03\x03" + os.urandom(n)


def _fernet_like():
    return b"\x80" + os.urandom(72)


# ════════════════════════════════════════════════════════════════════════════
#  Normal-traffic packet factories (used by both demo + stream)
# ════════════════════════════════════════════════════════════════════════════

def _normal_packet():
    """Produce one believable 'normal' packet."""
    roll = random.random()
    src = random.choice(LAN_HOSTS)

    if roll < 0.35:  # HTTPS / TLS
        dst = random.choice([ip for ip, p in SERVERS.items() if p == 443])
        return _make_pkt("TCP", src, dst,
                         src_port=random.randint(49152, 65535), dst_port=443,
                         flags=random.choice(["ACK", "ACK|PSH", "SYN", "SYN|ACK"]),
                         info="HTTPS/TLS", payload=_tls_appdata(random.randint(80, 600)),
                         seq=random.randint(0, 2**32 - 1))
    if roll < 0.5:  # HTTP
        return _make_pkt("TCP", src, "93.184.216.34",
                         src_port=random.randint(49152, 65535), dst_port=80,
                         flags="ACK|PSH", info="HTTP",
                         payload=b"GET /index.html HTTP/1.1\r\nHost: example.com\r\n\r\n",
                         seq=random.randint(0, 2**32 - 1))
    if roll < 0.7:  # DNS
        return _make_pkt("UDP", src, "8.8.8.8",
                         src_port=random.randint(1024, 65535), dst_port=53,
                         info=f"DNS query: {random.choice(DNS_DOMAINS)}")
    if roll < 0.82:  # ICMP
        return _make_pkt("ICMP", src, "192.168.1.1", info="Echo Request", ttl=64)
    if roll < 0.92:  # SSH
        return _make_pkt("TCP", src, "192.168.1.5",
                         src_port=random.randint(49152, 65535), dst_port=22,
                         flags="ACK|PSH", info="SSH",
                         payload=b"SSH-2.0-OpenSSH_8.9\r\n" + os.urandom(32),
                         seq=random.randint(0, 2**32 - 1))
    # misc UDP
    return _make_pkt("UDP", src, _random_ip(),
                     src_port=random.randint(1024, 65535),
                     dst_port=random.choice([123, 1900, 5353, 5060]))


# ════════════════════════════════════════════════════════════════════════════
#  Attack scenario generators (yield lists of packets)
# ════════════════════════════════════════════════════════════════════════════

def _attack_port_scan():
    attacker = random.choice(["10.0.0.99", "45.33.12.7", "185.220.101.5"])
    target = random.choice(LAN_HOSTS)
    pkts = []
    for port in random.sample(range(1, 1024), 30):
        pkts.append(_make_pkt("TCP", attacker, target,
                              src_port=54321, dst_port=port, flags="SYN", ttl=64))
    return pkts


def _attack_syn_flood():
    flood_ip = random.choice(["172.16.0.88", "203.0.113.66"])
    target = random.choice(LAN_HOSTS)
    return [_make_pkt("TCP", flood_ip, target,
                      src_port=random.randint(1024, 65535), dst_port=80,
                      flags="SYN", ttl=128) for _ in range(110)]


def _attack_arp_spoof():
    pkts = []
    for mac in ["aa:bb:cc:dd:ee:01", "ff:ee:dd:cc:bb:02"]:
        pkts.append(_make_pkt("ARP", "192.168.1.1", "192.168.1.255",
                              src_mac=mac, info="op=2 (1=req,2=reply)"))
    return pkts


def _attack_xmas():
    return [_make_pkt("TCP", "10.5.5.5", random.choice(LAN_HOSTS),
                      src_port=12345, dst_port=443, flags="FIN|PSH|URG")]


def _attack_null():
    return [_make_pkt("TCP", "10.5.5.6", random.choice(LAN_HOSTS),
                      src_port=12346, dst_port=445, flags="")]


def _attack_dns_tunnel():
    blob = base64.b32encode(os.urandom(40)).decode().lower().rstrip("=")
    qname = f"{blob}.exfil.evil-c2.com."
    return [_make_pkt("UDP", random.choice(LAN_HOSTS), "8.8.8.8",
                      src_port=random.randint(1024, 65535), dst_port=53,
                      info=f"DNS query: {qname}")]


def _attack_cleartext_creds():
    victim = random.choice(LAN_HOSTS)
    creds = base64.b64encode(b"admin:hunter2").decode()
    http = (b"POST /login HTTP/1.1\r\nHost: intranet.local\r\n"
            b"Authorization: Basic " + creds.encode() +
            b"\r\n\r\nuser=admin&password=hunter2")
    return [_make_pkt("TCP", victim, "93.184.216.34",
                      src_port=random.randint(49152, 65535), dst_port=80,
                      flags="ACK|PSH", info="HTTP", payload=http,
                      seq=random.randint(0, 2**32 - 1))]


def _attack_suspicious_port():
    return [_make_pkt("TCP", random.choice(LAN_HOSTS), "185.220.101.5",
                      src_port=random.randint(49152, 65535), dst_port=4444,
                      flags="ACK|PSH", info="unknown", payload=os.urandom(120),
                      seq=random.randint(0, 2**32 - 1))]


ATTACKS = [
    _attack_port_scan, _attack_syn_flood, _attack_arp_spoof,
    _attack_xmas, _attack_null, _attack_dns_tunnel,
    _attack_cleartext_creds, _attack_suspicious_port,
]


# ════════════════════════════════════════════════════════════════════════════
#  Live stream generator (used by the dashboard server)
# ════════════════════════════════════════════════════════════════════════════

def demo_packet_stream(pps=18, attack_every=(6.0, 12.0)):
    """
    Infinite generator yielding packets at roughly `pps` packets/sec.
    Periodically injects a random attack scenario so the dashboard always
    has something interesting to surface.
    """
    delay = 1.0 / max(pps, 1)
    next_attack = time.time() + random.uniform(*attack_every)

    # A persistent beacon to trip the C2 detector
    beacon_src = random.choice(LAN_HOSTS)
    beacon_dst = "185.220.101.5"
    next_beacon = time.time() + 2.0

    while True:
        now = time.time()

        if now >= next_attack:
            for p in random.choice(ATTACKS)():
                yield p
            next_attack = now + random.uniform(*attack_every)

        if now >= next_beacon:
            yield _make_pkt("TCP", beacon_src, beacon_dst,
                            src_port=44321, dst_port=8443, flags="ACK|PSH",
                            info="HTTPS/TLS", payload=_tls_appdata(64),
                            seq=random.randint(0, 2**32 - 1))
            next_beacon = now + 1.5  # regular cadence -> beacon detection

        yield _normal_packet()
        time.sleep(delay * random.uniform(0.6, 1.4))


# ════════════════════════════════════════════════════════════════════════════
#  One-shot scripted demo (CLI)
# ════════════════════════════════════════════════════════════════════════════

def _consume(pkt, analyzer, anomaly, crypto, logger, threat, show=True):
    from utils.display import Display
    analyzer.process(pkt)
    anomaly.check(pkt)
    crypto.inspect(pkt)
    logger.log_packet(pkt)
    if show:
        Display.packet_line(pkt)
    for a in anomaly.get_new_alerts():
        if threat:
            threat.register(a)
        Display.alert(a)
        logger.log_alert(a)


def run_demo(analyzer, anomaly, crypto, reporter, logger, threat=None):
    from utils.display import Display

    Display.section("Demo — Phase 1: Normal Traffic")
    for _ in range(45):
        _consume(_normal_packet(), analyzer, anomaly, crypto, logger, threat)
        time.sleep(0.02)

    Display.section("Demo — Phase 2: Encrypted Traffic Detection")
    enc = [
        _make_pkt("TCP", "192.168.1.55", "10.0.0.1", 54321, 443,
                  "ACK|PSH", "TLS Application Data", _tls_appdata(256), seq=1),
        _make_pkt("TCP", "192.168.1.55", "10.0.0.2", 22222, 22,
                  "ACK|PSH", "SSH", b"SSH-2.0-OpenSSH_8.9\r\n" + os.urandom(48), seq=2),
        _make_pkt("TCP", "192.168.1.20", "172.16.0.5", 33333, 9999,
                  "ACK|PSH", "Custom encrypted", _fernet_like(), seq=3),
        _make_pkt("TCP", "10.10.10.10", "10.10.10.20", 44444, 8443,
                  "ACK|PSH", "", os.urandom(512), seq=4),
    ]
    for pkt in enc:
        _consume(pkt, analyzer, anomaly, crypto, logger, threat)
        time.sleep(0.05)

    Display.section("Demo — Phase 3: Attack Scenarios")
    scenarios = [
        ("Port scan",            _attack_port_scan),
        ("SYN flood burst",      _attack_syn_flood),
        ("ARP spoofing",         _attack_arp_spoof),
        ("Xmas scan",            _attack_xmas),
        ("Null scan",            _attack_null),
        ("DNS tunneling",        _attack_dns_tunnel),
        ("Cleartext credentials", _attack_cleartext_creds),
        ("Backdoor port (4444)", _attack_suspicious_port),
    ]
    for name, fn in scenarios:
        print(f"\n  Simulating {name}…")
        pkts = fn()
        for i, pkt in enumerate(pkts):
            # Only render a few lines for noisy bursts
            _consume(pkt, analyzer, anomaly, crypto, logger, threat,
                     show=(len(pkts) <= 5 or i >= len(pkts) - 2))
        time.sleep(0.05)
