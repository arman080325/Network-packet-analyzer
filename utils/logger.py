"""
utils/logger.py
---------------
Writes packet logs (CSV) and alert logs (plain text) to disk.
"""

import csv
import os
from datetime import datetime


class Logger:

    def __init__(self, log_dir="data/captures"):
        os.makedirs(log_dir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")

        self._pkt_path   = os.path.join(log_dir, f"packets_{ts}.csv")
        self._alert_path = os.path.join(log_dir, f"alerts_{ts}.txt")

        self._pkt_file   = open(self._pkt_path,   "w", newline="", buffering=1)
        self._alert_file = open(self._alert_path,  "w", buffering=1)

        self._writer = csv.DictWriter(
            self._pkt_file,
            fieldnames=["timestamp", "protocol", "src_ip", "src_port",
                        "dst_ip", "dst_port", "length", "flags", "info"],
            extrasaction="ignore"
        )
        self._writer.writeheader()

    def log_packet(self, pkt: dict):
        try:
            self._writer.writerow(pkt)
        except Exception:
            pass

    def log_alert(self, alert: dict):
        line = (
            f"[{alert.get('time','')}] "
            f"[{alert.get('severity','')}] "
            f"{alert.get('type','')} — "
            f"{alert.get('message','')}\n"
        )
        self._alert_file.write(line)

    def close(self):
        self._pkt_file.close()
        self._alert_file.close()
        print(f"\n  Packet log  → {self._pkt_path}")
        print(f"  Alert log   → {self._alert_path}")
