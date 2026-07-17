#!/usr/bin/env python3
"""
NetScope — Network Packet Analyzer v2.0
========================================
Live network traffic capture with protocol dissection,
anomaly detection, encrypted payload analysis, and a
real-time web dashboard.

Author : Arman Ahemad Khan
GitHub : https://github.com/arman080325
"""

import argparse
import sys
import os
import time
from datetime import datetime

from core.analyzer import PacketAnalyzer
from core.anomaly import AnomalyDetector
from core.crypto_detector import CryptoDetector
from core.threat import ThreatScorer
from utils.display import Display
from utils.logger import Logger
from reports.reporter import Reporter
# NOTE: core.sniffer (and its scapy dependency) is imported lazily inside the
# live/offline branches so that --demo and --dashboard work with no root and
# without scapy installed.


def parse_args():
    parser = argparse.ArgumentParser(
        description="NetScope — Protocol dissection, anomaly detection & crypto detection",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Examples:
  python3 main.py --demo                     # Simulated traffic (no root)
  python3 main.py --dashboard                # Launch live web dashboard
  python3 main.py --dashboard --demo         # Dashboard + demo data
  sudo python3 main.py -i eth0               # Live capture
  sudo python3 main.py -i eth0 -t 30 --report
  python3 main.py --offline capture.pcap --report
        """
    )
    parser.add_argument("-i", "--interface",  default=None,
                        help="Network interface (default: auto-detect)")
    parser.add_argument("-c", "--count",      type=int, default=0,
                        help="Packet count limit (0 = unlimited)")
    parser.add_argument("-f", "--filter",     default="",
                        help='BPF filter (e.g. "tcp port 80")')
    parser.add_argument("-t", "--timeout",    type=int, default=0,
                        help="Auto-stop after N seconds")
    parser.add_argument("-o", "--output",     default=None,
                        help="Save capture to .pcap file")
    parser.add_argument("--report",           action="store_true",
                        help="Generate HTML + JSON report after capture")
    parser.add_argument("--offline",          default=None, metavar="FILE",
                        help="Analyze existing .pcap file")
    parser.add_argument("--demo",             action="store_true",
                        help="Simulated traffic demo (no root needed)")
    parser.add_argument("--dashboard",        action="store_true",
                        help="Launch live web dashboard (opens browser)")
    parser.add_argument("--http-port",        type=int, default=8080, dest="http_port",
                        help="HTTP port for dashboard (default: 8080)")
    parser.add_argument("--ws-port",          type=int, default=8765, dest="ws_port",
                        help="WebSocket port (default: 8765)")
    parser.add_argument("--threshold-syn",    type=int, default=100, dest="threshold_syn",
                        help="SYN flood threshold (pkts/sec). Default: 100")
    parser.add_argument("--threshold-port",   type=int, default=20, dest="threshold_port",
                        help="Port scan threshold (unique ports). Default: 20")
    return parser.parse_args()


def main():
    args = parse_args()
    Display.banner()

    # ── Dashboard mode — delegates to frontend/server.py ──────────────────
    if args.dashboard:
        Display.info("Launching live dashboard…")
        import subprocess, webbrowser
        cmd = [sys.executable, "frontend/server.py"]
        if args.demo:         cmd.append("--demo")
        if args.interface:    cmd += ["-i", args.interface]
        if args.filter:       cmd += ["-f", args.filter]
        if args.count:        cmd += ["-c", str(args.count)]
        if args.timeout:      cmd += ["-t", str(args.timeout)]
        if args.output:       cmd += ["-o", args.output]
        cmd += ["--http-port", str(args.http_port)]
        cmd += ["--ws-port",   str(args.ws_port)]
        cmd += ["--threshold-syn",  str(args.threshold_syn)]
        cmd += ["--threshold-port", str(args.threshold_port)]

        Display.info(f"Dashboard → http://localhost:{args.http_port}/dashboard.html")
        Display.info("Press Ctrl+C to stop.")
        import threading, time as _t
        def open_browser():
            _t.sleep(1.5)
            webbrowser.open(f"http://localhost:{args.http_port}/dashboard.html")
        threading.Thread(target=open_browser, daemon=True).start()

        try:
            subprocess.run(cmd)
        except KeyboardInterrupt:
            Display.info("\nDashboard stopped.")
        return

    # ── CLI mode ───────────────────────────────────────────────────────────
    logger   = Logger()
    analyzer = PacketAnalyzer()
    anomaly  = AnomalyDetector(
        syn_threshold=args.threshold_syn,
        port_scan_threshold=args.threshold_port,
    )
    crypto   = CryptoDetector()
    threat   = ThreatScorer()
    reporter = Reporter()

    # Demo mode
    if args.demo:
        Display.info("Running in DEMO mode — generating simulated packets…")
        from utils.demo import run_demo
        run_demo(analyzer, anomaly, crypto, reporter, logger, threat)
        _print_summary(analyzer, anomaly, crypto, reporter, args, time.time(), threat)
        return

    # Offline mode
    if args.offline:
        if not os.path.exists(args.offline):
            Display.error(f"File not found: {args.offline}")
            sys.exit(1)
        Display.info(f"Analyzing pcap: {args.offline}")
        from core.sniffer import PacketSniffer
        sniffer = PacketSniffer(interface=None, bpf_filter=args.filter,
                                packet_count=args.count, offline=args.offline)
    else:
        if os.geteuid() != 0:
            Display.warning("Live capture requires root. Try: sudo python3 main.py")
            Display.info("Or use --demo / --dashboard --demo for demo mode.")
            sys.exit(1)
        from core.sniffer import PacketSniffer
        sniffer = PacketSniffer(interface=args.interface, bpf_filter=args.filter,
                                packet_count=args.count, output_file=args.output)

    Display.section("Starting Capture")
    Display.info(f"Interface : {sniffer.interface or args.offline}")
    Display.info(f"Filter    : {args.filter or 'none (all traffic)'}")
    Display.info(f"Count     : {args.count or 'unlimited'}")
    Display.info(f"Timeout   : {args.timeout or 'none'}s")
    print()

    start_time = time.time()

    def on_packet(pkt):
        analyzer.process(pkt)
        anomaly.check(pkt)
        crypto.inspect(pkt)
        logger.log_packet(pkt)
        Display.packet_line(pkt)
        for alert in anomaly.get_new_alerts():
            threat.register(alert)
            Display.alert(alert)
            logger.log_alert(alert)
        if args.timeout and (time.time() - start_time) >= args.timeout:
            Display.info("Timeout reached — stopping capture.")
            sniffer.stop()

    try:
        sniffer.start(callback=on_packet)
    except KeyboardInterrupt:
        Display.info("\nCapture interrupted by user.")

    _print_summary(analyzer, anomaly, crypto, reporter, args, start_time, threat)
    logger.close()


def _print_summary(analyzer, anomaly, crypto, reporter, args, start_time, threat=None):
    elapsed = time.time() - start_time
    Display.section("Session Summary")
    summary = analyzer.summary()
    Display.summary_table(summary, elapsed)

    Display.section("Anomaly Report")
    Display.anomaly_report(anomaly.full_report())

    Display.section("Encryption Detection")
    Display.crypto_report(crypto.report())

    threat_report = threat.report() if threat else {"top": []}
    if threat_report.get("top"):
        Display.section("Threat Board — Highest-Risk Hosts")
        Display.threat_report(threat_report)

    # Extra stats
    Display.section("Advanced Stats")
    print(f"  TCP Retransmissions : {summary.get('retransmissions', 0)}")
    print(f"  Avg packet size     : {summary.get('avg_pkt_size', 0):.0f} B")
    if summary.get('top_services'):
        print(f"\n  Top services:")
        for svc, cnt in summary['top_services'][:5]:
            print(f"    {cnt:5d}  {svc}")
    if summary.get('top_dns_domains'):
        print(f"\n  Top DNS domains:")
        for dom, cnt in summary['top_dns_domains'][:5]:
            print(f"    {cnt:4d}  {dom}")

    if hasattr(args, 'report') and args.report:
        path = reporter.generate(
            summary=summary,
            anomalies=anomaly.full_report(),
            crypto=crypto.report(),
            elapsed=elapsed,
            threat=threat_report,
        )
        Display.info(f"Report saved → {path}")


if __name__ == "__main__":
    main()