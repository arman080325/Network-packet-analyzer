"""
core/netinfo.py
---------------
Lightweight, dependency-free network intelligence helpers shared across
the analyzer, anomaly engine and dashboard server.

  • classify_ip()     → 'private' | 'public' | 'loopback' | 'multicast' |
                         'reserved' | 'link-local' | 'cgnat' | 'broadcast'
  • service_name()    → friendly name for a well-known port
  • is_internal()     → True for RFC1918 / loopback / link-local space
  • risky_port()      → label if a port is a known backdoor / malware port

No external GeoIP database is required — classification is computed purely
from the address structure, which is exactly what a SOC analyst eyeballs
first when triaging traffic.
"""

import ipaddress


# ── Well-known service ports ────────────────────────────────────────────────
SERVICE_PORTS = {
    20: "FTP-DATA", 21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
    53: "DNS", 67: "DHCP", 68: "DHCP", 69: "TFTP", 80: "HTTP",
    110: "POP3", 119: "NNTP", 123: "NTP", 135: "MS-RPC", 137: "NetBIOS",
    138: "NetBIOS", 139: "NetBIOS", 143: "IMAP", 161: "SNMP", 162: "SNMP",
    389: "LDAP", 443: "HTTPS", 445: "SMB", 465: "SMTPS", 514: "Syslog",
    587: "SMTP", 631: "IPP", 636: "LDAPS", 853: "DNS-over-TLS",
    993: "IMAPS", 995: "POP3S", 1080: "SOCKS", 1194: "OpenVPN",
    1433: "MSSQL", 1521: "Oracle", 1723: "PPTP", 1900: "SSDP",
    2049: "NFS", 3306: "MySQL", 3389: "RDP", 5060: "SIP", 5061: "SIP-TLS",
    5353: "mDNS", 5432: "PostgreSQL", 5900: "VNC", 6379: "Redis",
    8080: "HTTP-alt", 8443: "HTTPS-alt", 8883: "MQTT-TLS", 9200: "Elasticsearch",
    27017: "MongoDB",
}

# ── Ports historically abused by malware / backdoors / C2 ────────────────────
RISKY_PORTS = {
    23:    "Telnet (cleartext)",
    1080:  "SOCKS proxy (common C2 relay)",
    1337:  "Common backdoor port",
    3389:  "RDP (brute-force target)",
    4444:  "Metasploit default handler",
    4445:  "Metasploit / Sliver handler",
    5555:  "Android Debug Bridge",
    6666:  "IRC botnet C2",
    6667:  "IRC botnet C2",
    9001:  "Tor / Cobalt Strike default",
    12345: "NetBus backdoor",
    31337: "Back Orifice / 'eleet'",
    54321: "Back Orifice 2000",
}


def classify_ip(addr: str) -> str:
    """Return a coarse classification of an IPv4/IPv6 address."""
    if not addr:
        return "unknown"
    try:
        ip = ipaddress.ip_address(addr)
    except ValueError:
        return "unknown"

    if ip.is_loopback:
        return "loopback"
    if ip.is_multicast:
        return "multicast"
    if ip.is_link_local:
        return "link-local"
    if ip.version == 4:
        # Carrier-grade NAT 100.64.0.0/10
        if ipaddress.IPv4Address("100.64.0.0") <= ip <= ipaddress.IPv4Address("100.127.255.255"):
            return "cgnat"
        if str(ip) == "255.255.255.255":
            return "broadcast"
    if ip.is_private:
        return "private"
    if ip.is_reserved or ip.is_unspecified:
        return "reserved"
    return "public"


def is_internal(addr: str) -> bool:
    """True for addresses on the local / private side of the network."""
    return classify_ip(addr) in ("private", "loopback", "link-local", "cgnat")


def service_name(port) -> str:
    """Friendly service label for a port number ('' if unknown)."""
    try:
        return SERVICE_PORTS.get(int(port), "")
    except (TypeError, ValueError):
        return ""


def risky_port(port):
    """Return a risk label if the port is a known backdoor/malware port, else None."""
    try:
        return RISKY_PORTS.get(int(port))
    except (TypeError, ValueError):
        return None
