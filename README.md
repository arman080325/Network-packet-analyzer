# 🛡 NetScope — Network Packet Analyzer

> Live network traffic capture, analysis & threat detection — with a real-time browser dashboard.
> Protocol dissection · Anomaly & attack detection · Encrypted-payload analysis · Per-host threat scoring.

Built with **Python · Scapy · Socket · Cryptography** — the dashboard uses **zero extra dependencies** (pure-stdlib WebSocket + HTTP server).
Author: **Arman Ahemad Khan** · [github.com/arman080325](https://github.com/arman080325)

---

## ✦ Features

| Module | What it does |
|---|---|
| **Live Web Dashboard** | Real-time SOC-style console in the browser — animated network map, threat board, entropy gauge, throughput & protocol charts, live packet stream with filters |
| **Packet Sniffer** | Live capture via Scapy on any interface; offline `.pcap` analysis |
| **Protocol Dissector** | Full dissection of TCP, UDP, ICMP, ARP, DNS, DHCP, HTTP, HTTPS, SSH, FTP |
| **Anomaly Detector** | SYN flood, port scan, Xmas/Null scan, ARP spoofing, ICMP flood, low-TTL, large packets — **plus DNS tunneling, cleartext credential exposure, C2 beaconing & risky-port contact** |
| **Threat Scoring Engine** | Per-IP weighted threat score with time-decay; ranks hosts as clean / suspicious / malicious |
| **IP Intelligence** | Classifies every address (private, public, CGNAT, loopback, multicast, link-local…), resolves service names & flags known backdoor/malware ports |
| **Crypto Detector** | TLS/SSL signatures, SSH banners, Shannon entropy, Fernet magic bytes, AES-GCM heuristic, Base64 detection + live encrypted-traffic % |
| **Session Analyzer** | Protocol breakdown, top talkers, **conversation flows**, **retransmission detection**, per-second throughput history, connection tracking |
| **Reporter** | Self-contained HTML report + JSON export (now includes the threat board) |
| **Demo Mode** | Fully simulated traffic with realistic attack bursts — **no root, no live interface, no scapy needed** |

---

## 📁 Project Structure

```
Network-packet-analyzer/
│
├── main.py                    ← Entry point, CLI argument parser
├── dashboard.html             ← Original single-file local dashboard (unchanged, still works)
│
├── core/
│   ├── sniffer.py             ← Scapy-based live capture & pcap reader
│   ├── analyzer.py            ← Stateful stats, flows, throughput, retransmissions
│   ├── anomaly.py             ← Real-time anomaly & attack detection engine
│   ├── crypto_detector.py     ← Encrypted-payload detection (entropy + signatures)
│   ├── threat.py              ← Per-host weighted threat-scoring engine
│   └── netinfo.py             ← IP classification, service & risky-port lookup
│
├── frontend/
│   └── server.py              ← Pure-stdlib HTTP + WebSocket server (local/offline use)
│
├── backend/                   ★ new — production API, deploy this to Render
│   ├── app.py                 ← Flask + WebSocket service, single $PORT, reuses core/ as-is
│   └── requirements.txt
│
├── webapp/                    ★ new — production web console, deploy this to Vercel
│   ├── index.html             ← Redesigned SOC-style live console
│   ├── style.css              ← Design system (radar map, gauges, threat board)
│   ├── app.js                 ← WebSocket client + rendering (same wire protocol)
│   └── vercel.json
│
├── render.yaml                ★ new — one-click Render blueprint for backend/
│
├── utils/
│   ├── display.py             ← ANSI-coloured terminal output
│   ├── logger.py              ← CSV packet log + alert log writer
│   └── demo.py                ← Simulated traffic + attack scenarios
│
├── reports/
│   └── reporter.py            ← HTML + JSON report generator
│
├── tests/
│   └── test_all.py            ← Unit tests (pytest) — 32 tests
│
├── requirements.txt            ← CLI/local deps
└── README.md
```

---

## 🚀 Getting Started

### 1. Install dependencies
```bash
pip install -r requirements.txt
```
> The dashboard itself needs **nothing beyond the standard library**. `scapy` is only required for *live* capture; demo mode and the dashboard run on a stock Python 3.8+.

### 2. ⭐ Launch the Live Dashboard (recommended — no root needed)
```bash
python3 main.py --dashboard --demo
```
This starts the server **and opens your browser** to the live console. Or run the server directly:
```bash
python3 frontend/server.py --demo            # then open the URL it prints
# → http://localhost:8080/dashboard.html
```
You'll see a force-directed **network map** (hosts coloured by threat level), a **threat leaderboard**, a live **entropy gauge**, **throughput** & **protocol** charts, and a filterable **packet stream** — all updating in real time as simulated normal traffic, port scans, SYN floods, ARP spoofing, DNS tunneling, C2 beacons and cleartext-credential leaks stream through.

**Live capture on the dashboard** (requires root):
```bash
sudo python3 main.py --dashboard -i eth0
sudo python3 frontend/server.py -i eth0 -f "tcp or udp"
```

Dashboard ports are configurable:
```bash
python3 main.py --dashboard --demo --http-port 8080 --ws-port 8765 --demo-pps 25
```

### 3. Terminal Demo Mode (no root needed)
```bash
python3 main.py --demo
```

### 4. Live Capture in the terminal (requires root)
```bash
sudo python3 main.py                          # auto-detect interface
sudo python3 main.py -i eth0                   # specific interface
sudo python3 main.py -i eth0 -c 100            # capture 100 packets then stop
sudo python3 main.py -i eth0 -f "tcp port 443" # BPF filter: HTTPS only
sudo python3 main.py -i wlan0 -t 30 --report   # 30s capture + HTML report
```

### 5. Analyze an existing pcap
```bash
python3 main.py --offline capture.pcap --report
```

### 6. Run the tests
```bash
pip install pytest
python -m pytest tests/ -v
```

---

## ☁️ Live Deployment (Vercel + Render)

The project ships in two independently-deployable pieces that talk to each other over WebSocket:

| Piece | Folder | Deploy to | What it is |
|---|---|---|---|
| **Backend / API** | `backend/` | **Render** | Single-port stdlib HTTP + WebSocket server (no Flask/gunicorn — same hand-rolled approach as `frontend/server.py`, just merged onto one port). Reuses `core/` untouched. Runs realistic simulated traffic (demo mode) since Render containers can't do raw-socket live capture — the same reason any hosted demo of a packet sniffer runs simulated traffic. |
| **Frontend console** | `webapp/` | **Vercel** | Static SOC-style dashboard (no build step). Connects to the backend over WebSocket and renders the live feed. |

### 1. Deploy the backend to Render
1. Push this repo to GitHub.
2. In Render: **New → Blueprint**, point it at the repo — `render.yaml` at the root configures everything automatically (root dir `backend/`, build + start commands, health check).
   - Or manually: **New → Web Service**, root directory `backend`, build command `pip install -r requirements.txt`, start command `python app.py`, health check path `/health`.
3. Once deployed, note the URL, e.g. `https://netscope-backend.onrender.com`.
4. Your WebSocket endpoint is `wss://netscope-backend.onrender.com/ws`.

### 2. Deploy the frontend to Vercel
1. In Vercel: **New Project**, import the repo, set **Root Directory** to `webapp`.
2. Framework preset: **Other** (static site) — no build command needed.
3. Deploy. You'll get a URL like `https://netscope.vercel.app`.
4. Open it, click the connection pill (top right), paste your Render WebSocket URL (`wss://netscope-backend.onrender.com/ws`) and hit **Connect**. It's saved in the browser for next time.

### Notes on Render's free tier
Free-tier Render services spin down after inactivity — the first WebSocket connection after idle can take ~30–50s to wake up (the console will show "Connecting…" and auto-retry). Upgrade to a paid instance for an always-on demo.

### Environment variables (backend)
| Var | Default | Purpose |
|---|---|---|
| `PORT` | (set by Render) | HTTP/WS port |
| `DEMO_PPS` | `18` | Simulated packets/sec |
| `SYN_THRESHOLD` | `100` | SYN-flood alert threshold |
| `PORT_SCAN_THRESHOLD` | `20` | Port-scan alert threshold |
| `ALLOW_LIVE_CAPTURE` | unset | Set to `1` to attempt real Scapy capture instead of demo (only works on hosts with raw-socket access, not Render) |

---

## 🖥 Dashboard Panels

<img width="1918" height="997" alt="image" src="https://github.com/user-attachments/assets/d4c7d079-1dd0-44a1-a637-85a9cd3d9af3" />


| Panel | Shows |
|---|---|
| **Live Network Map** | Force-directed graph of hosts & flows; nodes coloured by threat level (green/amber/red) and address class (local cyan / external orange); animated packet pulses; malicious hosts glow |
| **Payload Entropy** | Live Shannon-entropy gauge with the 7.2 bits/byte "likely encrypted" threshold marked |
| **Threat Posture** | Count of hosts tracked & how many are flagged, split clean / suspicious / malicious |
| **Throughput** | Bytes/sec over time | 
| **Protocol Mix** | TCP / UDP / ICMP / ARP distribution |
| **Sidebar** | Protocol counts, address-type breakdown, top services |
| **Packet Stream** | Live table — filter with `ip:`, `proto:`, `port:`, `enc:true`; click a row to inspect |
| **Threats / Alerts / Crypto / Detail / Stats** | Tabbed right panel: ranked threat board, anomaly feed, encrypted-payload feed, packet detail, and full session stats incl. top conversations |

---

## 🔍 Detection Capabilities

### Anomaly & Attack Detection
| Attack | Detection Method |
|---|---|
| SYN Flood | ≥N SYN packets/sec from a single IP |
| Port Scan | Single IP probing ≥N unique destination ports |
| Xmas Scan | TCP FIN+PSH+URG flag combination |
| Null Scan | TCP packet with zero flags |
| ARP Spoofing | Same IP announced from multiple MAC addresses |
| ICMP Flood | ≥50 ICMP echo requests/sec from a single source |
| **DNS Tunneling** ★ | Abnormally long / high-entropy DNS query labels |
| **Credential Exposure** ★ | Cleartext HTTP Basic auth, FTP USER/PASS, or form passwords |
| **C2 Beaconing** ★ | Regular-interval, low-jitter internal→external contact |
| **Suspicious Port** ★ | Contact to known backdoor/malware ports (4444, 6667, 31337, …) |
| Low TTL | TTL ≤ 5 (traceroute / routing-loop indicator) |
| Large Packet | Non-TCP packets > 8 KB (possible amplification) |

### Per-Host Threat Scoring ★
Each alert contributes a weighted score to its source host. Scores **decay over time** (90 s half-life) so stale activity fades, and hosts are banded:

| Band | Score | Meaning |
|---|---|---|
| 🟢 Clean | < 25 | Normal |
| 🟡 Suspicious | 25 – 70 | Worth watching |
| 🔴 Malicious | ≥ 70 | Active threat |

### Encryption Detection
| Method | Signal |
|---|---|
| Shannon Entropy | > 7.2 bits/byte → likely encrypted or compressed |
| TLS/SSL Signature | Record-layer magic bytes `\x16\x03` / `\x17\x03` |
| SSH Banner | `SSH-2.0-…` banner in payload |
| Fernet Magic | `\x80` version byte (Python `cryptography` lib) |
| AES-GCM Heuristic | Low-entropy nonce prefix + high-entropy ciphertext |
| Base64 Heuristic | ≥92% valid base64 chars + length divisible by 4 |
| Port Inference | 443, 22, 993, 995, 465, 8443, … |

---

## 🛠 CLI Reference

```
usage: main.py [-h] [-i INTERFACE] [-c COUNT] [-f FILTER] [-t TIMEOUT]
               [-o OUTPUT] [--report] [--offline PCAP] [--demo]
               [--dashboard] [--http-port N] [--ws-port N] [--demo-pps N]
               [--threshold-syn N] [--threshold-port N]

Options:
  -i, --interface     Network interface (default: auto-detect)
  -c, --count         Packet count limit (0 = unlimited)
  -f, --filter        BPF filter string (e.g. "tcp port 80")
  -t, --timeout       Stop after N seconds
  -o, --output        Save packets to a .pcap file
  --report            Generate HTML + JSON report after the session
  --offline FILE      Analyze a .pcap file (no root needed)
  --demo              Simulated traffic demo (no root needed)
  --dashboard         Launch the live web dashboard (opens browser)
  --http-port N       Dashboard HTTP port (default: 8080)
  --ws-port N         Dashboard WebSocket port (default: 8765)
  --demo-pps N        Demo packets-per-second (default: 18)
  --threshold-syn N   SYN-flood alert threshold (default: 100/sec)
  --threshold-port N  Port-scan alert threshold (default: 20 ports)
```

---

## 📄 Resume framing

Suggested bullet points:

- Built **NetScope**, a full-stack network security console (Python/Flask backend on Render, static JS frontend on Vercel) performing real-time protocol dissection, anomaly detection (SYN floods, port scans, ARP spoofing, DNS tunneling, C2 beaconing) and per-host threat scoring over a WebSocket stream.
- Designed a from-scratch anomaly-detection and threat-scoring engine with time-decayed risk bands (clean / suspicious / malicious) and encrypted-traffic classification via Shannon entropy + protocol-signature heuristics.
- Deployed a decoupled architecture (Render API + Vercel static console) with health checks, CORS configuration, and environment-based configuration for a always-reachable public demo.

---

## 📝 License

MIT License — free to use, fork, and learn from.

---

*Made with care by Arman Ahemad Khan — armankhan082020@gmail.com*
