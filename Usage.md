# ▶ How to Run NetScope

A quick, copy-paste guide for running the Network Packet Analyzer on **Windows**, **macOS**, or **Linux**.

---

## 0. The one thing to know about commands

This project's docs are written with `python3` (the macOS/Linux name). **On Windows the command is `python` (or `py`).**

| Docs say | Windows | macOS / Linux |
|---|---|---|
| `python3 …` | `python …`  *(or `py …`)* | `python3 …` |
| `sudo python3 …` | *Run terminal **as Administrator**, then* `python …` | `sudo python3 …` |

> Typing `python3` on Windows opens the Microsoft Store instead of running anything — that's expected. Use `python`.

---

## 1. Install (one time)

```bash
# Windows
pip install -r requirements.txt

# macOS / Linux
pip3 install -r requirements.txt
```

This installs `scapy`, `cryptography`, and `pytest`.
**You only need this for live capture and the tests** — the demo and the dashboard run on Python's standard library alone.

> Requires **Python 3.8+**. Check with `python --version` (Windows) or `python3 --version` (macOS/Linux).

---

## 2. ⭐ Run the live dashboard (start here)

The headline feature — a live browser console with an animated network map, threat board, entropy gauge, and packet stream, fed by **simulated** traffic. No admin rights needed.

```bash
# Windows
python main.py --dashboard --demo

# macOS / Linux
python3 main.py --dashboard --demo
```

Then:
1. Wait for the banner and the line `Dashboard → http://localhost:8080/dashboard.html`.
2. Your browser should open automatically. If it doesn't, open **http://localhost:8080/dashboard.html** yourself.
3. The status dot (top-right) turns **green "live"** once it connects — give it 1–2 seconds.
4. Press **Ctrl + C** in the terminal to stop.

**Alternative — start the server directly** (does the same thing without the wrapper):

```bash
# Windows
python frontend/server.py --demo

# macOS / Linux
python3 frontend/server.py --demo
```

**Change the ports** (if 8080 / 8765 are already in use):

```bash
python main.py --dashboard --demo --http-port 9090 --ws-port 9091
```

---

## 3. Terminal-only demo (no browser)

Same simulated traffic, printed as colour-coded text in the console. Good for a quick check or a CLI screenshot.

```bash
# Windows
python main.py --demo

# macOS / Linux
python3 main.py --demo
```

---

## 4. Run the tests

```bash
# Windows
python -m pytest tests/ -v

# macOS / Linux
python3 -m pytest tests/ -v
```

You should see **32 passed**. Using `-m pytest` avoids the "pytest.exe is not on PATH" warning.

---

## 5. Live capture (real network traffic)

This sniffs your actual network, so it needs elevated privileges and a packet driver.

### Windows
1. Install **[Npcap](https://npcap.com)** — during setup, tick **"Install Npcap in WinPcap API-compatible mode"**.
2. Open **PowerShell / Terminal as Administrator** (right-click → *Run as administrator*).
3. Find your interface name with `python -c "from scapy.all import get_if_list; print(get_if_list())"` — common names are `"Wi-Fi"` and `"Ethernet"`.
4. Run:

```powershell
# Dashboard fed by real traffic
python main.py --dashboard -i "Wi-Fi"

# Terminal capture, HTTPS only
python main.py -i "Wi-Fi" -f "tcp port 443"
```

### macOS / Linux

```bash
# Dashboard fed by real traffic
sudo python3 main.py --dashboard -i eth0

# Terminal capture, HTTPS only
sudo python3 main.py -i eth0 -f "tcp port 443"
```

*(Replace `eth0` with your interface — `ip link` on Linux, `ifconfig` on macOS. Wi-Fi is often `wlan0` / `en0`.)*

---

## 6. Common options

| Option | Meaning | Example |
|---|---|---|
| `--dashboard` | Launch the web dashboard | `--dashboard` |
| `--demo` | Use simulated traffic (no root) | `--demo` |
| `-i, --interface` | Network interface for live capture | `-i "Wi-Fi"` |
| `-f, --filter` | BPF filter — capture only matching packets | `-f "tcp port 443"` |
| `-c, --count` | Stop after N packets | `-c 100` |
| `-t, --timeout` | Stop after N seconds | `-t 30` |
| `-o, --output` | Save captured packets to a `.pcap` file | `-o capture.pcap` |
| `--offline FILE` | Analyse an existing `.pcap` (no root) | `--offline capture.pcap` |
| `--report` | Write an HTML + JSON report afterwards | `--report` |
| `--http-port` | Dashboard web port (default 8080) | `--http-port 9090` |
| `--ws-port` | Dashboard WebSocket port (default 8765) | `--ws-port 9091` |
| `--demo-pps` | Demo packets per second (default 18) | `--demo-pps 30` |

**A few handy combinations:**

```bash
# Faster, busier demo dashboard
python main.py --dashboard --demo --demo-pps 30

# Analyse a saved capture and produce a report (no admin needed)
python main.py --offline capture.pcap --report

# Live capture: 30 seconds, then auto-generate a report  (macOS/Linux)
sudo python3 main.py -i eth0 -t 30 --report
```

---

## 7. Troubleshooting

| Symptom | Fix |
|---|---|
| `Python was not found…` / Store opens | You typed `python3` on Windows — use `python` or `py`. |
| `pytest.exe is not on PATH` warning | Harmless. Run tests with `python -m pytest tests/ -v`. |
| Browser doesn't open | Open **http://localhost:8080/dashboard.html** manually. |
| Dot stays red / "connecting…" | Wait a moment; if it persists, a firewall may be blocking the WebSocket port — try other ports with `--http-port` / `--ws-port`. |
| `Address already in use` | Another process holds the port — pick new ones with `--http-port 9090 --ws-port 9091`. |
| Live capture finds nothing / errors on Windows | Install **Npcap** (WinPcap-compatible mode) and run the terminal **as Administrator**. |
| `Operation not permitted` on live capture (macOS/Linux) | Prefix the command with `sudo`. |

---

## TL;DR (Windows)

```powershell
pip install -r requirements.txt        # once
python main.py --dashboard --demo      # show the live dashboard
python -m pytest tests/ -v             # confirm everything passes
```

## TL;DR (macOS / Linux)

```bash
pip3 install -r requirements.txt
python3 main.py --dashboard --demo
python3 -m pytest tests/ -v
```