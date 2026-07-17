"""
utils/display.py
----------------
All terminal output — coloured, aligned, structured.
Uses ANSI escape codes (no external dependencies beyond stdlib).
"""

import os
import sys

# ── ANSI colour codes ──────────────────────────────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
CYAN   = "\033[96m"
WHITE  = "\033[97m"
GRAY   = "\033[90m"

BG_RED  = "\033[41m"
BG_YELL = "\033[43m"

# Protocol → colour
PROTO_COLORS = {
    "TCP"    : CYAN,
    "UDP"    : GREEN,
    "ICMP"   : YELLOW,
    "ICMPv6" : YELLOW,
    "ARP"    : BLUE,
    "DNS"    : GREEN,
    "HTTPS"  : GREEN,
    "TLS"    : GREEN,
    "UNKNOWN": GRAY,
}

SEVERITY_COLORS = {
    "INFO"    : BLUE,
    "WARNING" : YELLOW,
    "CRITICAL": RED,
}


class Display:

    @staticmethod
    def banner():
        print(f"""
{CYAN}{BOLD}
 ███╗   ██╗███████╗████████╗    ███████╗███╗   ██╗██╗███████╗███████╗███████╗██████╗
 ████╗  ██║██╔════╝╚══██╔══╝    ██╔════╝████╗  ██║██║██╔════╝██╔════╝██╔════╝██╔══██╗
 ██╔██╗ ██║█████╗     ██║       ███████╗██╔██╗ ██║██║█████╗  █████╗  █████╗  ██████╔╝
 ██║╚██╗██║██╔══╝     ██║       ╚════██║██║╚██╗██║██║██╔══╝  ██╔══╝  ██╔══╝  ██╔══██╗
 ██║ ╚████║███████╗   ██║       ███████║██║ ╚████║██║██║     ██║     ███████╗██║  ██║
 ╚═╝  ╚═══╝╚══════╝   ╚═╝       ╚══════╝╚═╝  ╚═══╝╚═╝╚═╝     ╚═╝     ╚══════╝╚═╝  ╚═╝
{RESET}{DIM}  Network Packet Analyzer v1.0  |  Protocol Dissection · Anomaly Detection · Crypto Detection
  Author: Arman Ahemad Khan  |  github.com/arman080325{RESET}
""")

    @staticmethod
    def section(title: str):
        width = 70
        print(f"\n{BOLD}{CYAN}{'─' * width}{RESET}")
        print(f"{BOLD}{WHITE}  {title}{RESET}")
        print(f"{BOLD}{CYAN}{'─' * width}{RESET}")

    @staticmethod
    def info(msg: str):
        print(f"  {BLUE}[*]{RESET} {msg}")

    @staticmethod
    def warning(msg: str):
        print(f"  {YELLOW}[!]{RESET} {msg}", file=sys.stderr)

    @staticmethod
    def error(msg: str):
        print(f"  {RED}[✗]{RESET} {msg}", file=sys.stderr)

    @staticmethod
    def packet_line(pkt: dict):
        proto  = pkt.get("protocol", "???")
        color  = PROTO_COLORS.get(proto, GRAY)
        ts     = pkt.get("timestamp", "")
        src    = pkt.get("src_ip", "")
        dst    = pkt.get("dst_ip", "")
        sport  = pkt.get("src_port")
        dport  = pkt.get("dst_port")
        length = pkt.get("length", 0)
        flags  = pkt.get("flags", "")
        info   = pkt.get("info", "")

        src_str = f"{src}:{sport}" if sport else src
        dst_str = f"{dst}:{dport}" if dport else dst

        flag_str = f" [{YELLOW}{flags}{RESET}]" if flags else ""
        info_str = f" {DIM}{info}{RESET}"        if info  else ""

        print(
            f"  {DIM}{ts}{RESET}  "
            f"{color}{BOLD}{proto:<6}{RESET}  "
            f"{src_str:<22} → {dst_str:<22}  "
            f"{DIM}{length:>5}B{RESET}"
            f"{flag_str}{info_str}"
        )

    @staticmethod
    def alert(alert: dict):
        sev    = alert.get("severity", "INFO")
        atype  = alert.get("type", "")
        msg    = alert.get("message", "")
        ts     = alert.get("time", "")
        color  = SEVERITY_COLORS.get(sev, WHITE)
        icon   = {"INFO": "ℹ", "WARNING": "⚠", "CRITICAL": "🚨"}.get(sev, "?")
        print(f"\n  {color}{BOLD}[{icon} {sev}] {atype}{RESET}  {DIM}{ts}{RESET}")
        print(f"    {color}{msg}{RESET}\n")

    @staticmethod
    def summary_table(summary: dict, elapsed: float):
        rows = [
            ("Total Packets",       str(summary["total_packets"])),
            ("Total Data",          f"{summary['total_kb']} KB"),
            ("Duration",            f"{summary['duration_sec']}s"),
            ("Avg Throughput",      f"{summary['pps']} pkts/sec"),
            ("TCP Connections",     str(summary["connections_total"])),
            ("  Established",       str(summary["connections_est"])),
            ("  Closed",            str(summary["connections_closed"])),
            ("Avg Payload",         f"{summary['avg_payload_bytes']} bytes"),
        ]
        print()
        for label, value in rows:
            print(f"  {WHITE}{label:<22}{RESET} {CYAN}{value}{RESET}")

        print(f"\n  {BOLD}Protocol Breakdown:{RESET}")
        for proto, count in sorted(summary["protocol_counts"].items(), key=lambda x: -x[1]):
            pct   = count / max(summary["total_packets"], 1) * 100
            bar   = "█" * int(pct / 5)
            color = PROTO_COLORS.get(proto, GRAY)
            print(f"    {color}{proto:<8}{RESET}  {bar:<20}  {count:>6} pkts  ({pct:.1f}%)")

        if summary["top_src_ips"]:
            print(f"\n  {BOLD}Top Source IPs:{RESET}")
            for ip, count in summary["top_src_ips"][:5]:
                print(f"    {CYAN}{ip:<20}{RESET}  {count} packets")

        if summary["dns_queries"]:
            print(f"\n  {BOLD}Recent DNS Queries:{RESET}")
            for q in summary["dns_queries"][-5:]:
                print(f"    {DIM}{q}{RESET}")

    @staticmethod
    def anomaly_report(report: dict):
        total = report.get("total_alerts", 0)
        if total == 0:
            print(f"  {GREEN}✓ No anomalies detected.{RESET}")
            return

        print(f"  {YELLOW}Total alerts fired: {BOLD}{total}{RESET}")
        by_type = report.get("by_type", {})
        for atype, count in sorted(by_type.items(), key=lambda x: -x[1]):
            print(f"    {YELLOW}{atype:<20}{RESET}  {count}")

        scanners = report.get("unique_scanners", [])
        if scanners:
            print(f"\n  {BOLD}Suspected port scanners:{RESET}")
            for ip in scanners[:5]:
                print(f"    {RED}{ip}{RESET}")

        arp = report.get("arp_anomalies", {})
        if arp:
            print(f"\n  {BOLD}ARP anomalies:{RESET}")
            for ip, macs in arp.items():
                print(f"    {RED}{ip}{RESET} → {', '.join(macs)}")

    @staticmethod
    def threat_report(report: dict):
        top = report.get("top", [])
        if not top:
            print(f"  {GREEN}No high-risk hosts.{RESET}")
            return
        level_color = {"malicious": RED, "suspicious": YELLOW, "clean": GREEN}
        print(f"  {WHITE}{'HOST':<18}{'SCORE':>7}  {'LEVEL':<11}  TRIGGERS{RESET}")
        for r in top[:10]:
            c = level_color.get(r["level"], WHITE)
            triggers = ", ".join(r["types"][:3])
            print(f"  {c}{r['ip']:<18}{r['score']:>7.0f}  {r['level']:<11}{RESET}  {DIM}{triggers}{RESET}")

    @staticmethod
    def crypto_report(report: dict):
        enc   = report.get("encrypted_payloads", 0)
        total = report.get("total_inspected", 0)
        avg_e = report.get("avg_entropy", 0)
        high  = report.get("high_entropy_payloads", 0)

        print(f"  Packets inspected      : {total}")
        print(f"  Encrypted/encoded found: {YELLOW}{enc}{RESET}")
        print(f"  High-entropy payloads  : {YELLOW}{high}{RESET}")
        print(f"  Average entropy        : {avg_e:.3f} bits/byte")

        breakdown = report.get("protocol_breakdown", {})
        if breakdown:
            print(f"\n  {BOLD}Encrypted Protocol Breakdown:{RESET}")
            for proto, count in sorted(breakdown.items(), key=lambda x: -x[1]):
                print(f"    {GREEN}{proto:<20}{RESET}  {count}")

        detections = report.get("detections", [])
        if detections:
            print(f"\n  {BOLD}Sample Detections:{RESET}")
            for d in detections[-5:]:
                ts     = d.get("timestamp", "")
                src    = d.get("src", "")
                dst    = d.get("dst", "")
                port   = d.get("dst_port", "")
                size   = d.get("payload_bytes", 0)
                finds  = d.get("findings", [])
                methods = ", ".join(f["method"] for f in finds)
                print(f"    {DIM}{ts}{RESET}  {src} → {dst}:{port}  {CYAN}{methods}{RESET}  ({size}B)")
