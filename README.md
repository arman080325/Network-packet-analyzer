<div align="center">

# 🛡️ NetScope

### Network Packet Analyzer & Threat Intelligence Dashboard

**See the traffic. Understand the protocol. Spot suspicious behaviour.**

A Python-powered network analysis platform for live packet capture, protocol inspection, anomaly detection, encrypted-traffic heuristics, and real-time security monitoring — with both a terminal workflow and a browser-based SOC console.

<br/>

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Scapy](https://img.shields.io/badge/Packet_Capture-Scapy-2E8B57?style=for-the-badge)](https://scapy.net/)
[![WebSocket](https://img.shields.io/badge/Streaming-WebSocket-6C63FF?style=for-the-badge)](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)
[![Render](https://img.shields.io/badge/Backend-Render-46E3B7?style=for-the-badge&logo=render&logoColor=111)](https://render.com/)
[![Vercel](https://img.shields.io/badge/Frontend-Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://vercel.com/)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)

<br/>

**[Repository](https://github.com/arman080325/Network-packet-analyzer)**
&nbsp; • &nbsp;
**[Usage Guide](Usage.md)**
&nbsp; • &nbsp;
**[Report an Issue](https://github.com/arman080325/Network-packet-analyzer/issues)**

</div>

---

## ✨ What is NetScope?

NetScope turns raw network traffic into information that is easier to inspect and investigate. It captures packets, dissects protocol fields, tracks conversations, highlights unusual activity, and presents the results through a live dashboard or terminal summary.

Use it to explore network behaviour, learn how common protocols work, inspect saved PCAP captures, and experiment with security detection scenarios.

> **Two ways to explore:** run a no-privilege simulated demo to explore the dashboard, or use Scapy with the required permissions to inspect real traffic on a supported machine.

## 🖥️ The dashboard

The browser console brings packet activity and security signals into one workspace.

<div align="center">
  <img src="https://github.com/user-attachments/assets/d4c7d079-1dd0-44a1-a637-85a9cd3d9af3" alt="NetScope live network security dashboard" width="100%" />
  <sub>NetScope — live network monitoring and analysis interface</sub>
</div>

### Dashboard at a glance

| Workspace | What you can inspect |
|---|---|
| **Network map** | Hosts, traffic relationships, and threat-level visualisation |
| **Live packet stream** | Incoming packets with searchable filters and packet inspection |
| **Threat board** | Hosts ranked by weighted, time-decaying risk scores |
| **Anomaly feed** | Detection events and suspicious network patterns |
| **Traffic analytics** | Throughput, protocol distribution, and session statistics |
| **Crypto analysis** | Payload entropy and encryption-related signatures |
| **Host intelligence** | Address classification, services, and risky-port indicators |

## 🚀 Capabilities

### Packet capture & protocol analysis

- Live packet capture through **Scapy** on supported network interfaces.
- Offline analysis of existing `.pcap` captures.
- BPF capture filters, packet-count limits, timeouts, and optional PCAP output.
- Dissection and analysis across TCP, UDP, ICMP, ARP, DNS, DHCP, HTTP, HTTPS, SSH, and FTP traffic.
- Session statistics, top talkers, conversation flows, retransmission detection, and throughput history.

### Threat and anomaly detection

| Detection | Signal |
|---|---|
| SYN flood | High-rate SYN activity from a source |
| Port scan | A source probing many destination ports |
| Xmas / Null scan | Unusual TCP flag combinations |
| ARP spoofing | Conflicting MAC announcements for an IP |
| ICMP flood | Excessive ICMP echo activity |
| DNS tunnelling | Unusually long or high-entropy DNS labels |
| Cleartext credentials | Recognisable credentials in supported plaintext protocols |
| C2 beaconing | Repeated, regular outbound contact patterns |
| Risky-port contact | Traffic involving configured suspicious ports |
| Low TTL / large packet | Heuristic indicators worth investigating |

### Per-host threat scoring

Alerts contribute weighted points to a host's risk score. Scores decay over time so older activity gradually loses influence.

| Classification | Score | Interpretation |
|---|---:|---|
| 🟢 Clean | Below 25 | No elevated score |
| 🟡 Suspicious | 25–69 | Activity deserves review |
| 🔴 Malicious | 70 or higher | High-risk activity detected |

These are project heuristics, not a replacement for a dedicated IDS, endpoint protection, or analyst verification.

### Encrypted-traffic heuristics

NetScope looks for signals that may indicate encrypted or encoded payloads:

- Shannon entropy analysis.
- TLS/SSL record signatures.
- SSH banner recognition.
- Fernet marker recognition.
- AES-GCM pattern heuristic.
- Base64-like payload detection.
- Common encrypted-service port inference.

**Important:** payload entropy and signatures are indicators, not proof that a payload is encrypted. NetScope does not decrypt TLS traffic.

## ⚡ Quick start

### 1. Clone the repository

```bash
git clone https://github.com/arman080325/Network-packet-analyzer.git
cd Network-packet-analyzer
```

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

Use `python3` instead of `python` on systems where that is the configured Python command.

### 3. Launch the dashboard demo

```bash
python main.py --dashboard --demo
```

Open **http://localhost:8080/dashboard.html** if your browser does not open automatically.

The demo generates simulated packets and attack scenarios. It does **not** capture traffic from your network and does not require administrator/root privileges.

### 4. Try the terminal demo

```bash
python main.py --demo
```

### 5. Run the test suite

```bash
python -m pytest tests/ -v
```

For Windows-specific commands, Npcap setup, and troubleshooting, see the **[complete Usage Guide](Usage.md)**.

## 🎯 Working with real traffic

Live capture requires Scapy, a supported packet-capture driver, and sufficient operating-system permissions.

**Linux / macOS**
```bash
sudo python3 main.py -i eth0
sudo python3 main.py -i eth0 -f "tcp port 443"
sudo python3 main.py -i eth0 -t 30 --report
```

**Windows**

1. Install [Npcap](https://npcap.com/).
2. Open PowerShell or Terminal as Administrator.
3. Check available interfaces:
   ```powershell
   python -c "from scapy.all import get_if_list; print(get_if_list())"
   ```
4. Start capture using the interface name shown:
   ```powershell
   python main.py -i "Wi-Fi"
   ```

### Analyze an existing capture

```bash
python main.py --offline capture.pcap --report
```

### Useful CLI options

| Option | Description |
|---|---|
| `-i, --interface` | Network interface to capture from |
| `-c, --count` | Stop after a packet count (`0` means unlimited) |
| `-f, --filter` | BPF capture filter, e.g. `"tcp port 443"` |
| `-t, --timeout` | Stop capture after a number of seconds |
| `-o, --output` | Save captured packets to a PCAP file |
| `--offline FILE` | Analyze an existing PCAP file |
| `--demo` | Generate simulated traffic |
| `--dashboard` | Launch the local browser dashboard |
| `--report` | Generate HTML and JSON reports |
| `--http-port N` | Set the dashboard HTTP port (default: `8080`) |
| `--ws-port N` | Set the dashboard WebSocket port (default: `8765`) |
| `--threshold-syn N` | Configure the SYN-flood threshold |
| `--threshold-port N` | Configure the port-scan threshold |

## ☁️ Deployment architecture

NetScope can be explored locally or deployed as a split frontend/backend application.

<div align="center">

```text
                 ┌──────────────────────────────┐
                 │       Browser / User         │
                 └──────────────┬───────────────┘
                                │
                                ▼
                 ┌──────────────────────────────┐
                 │       Vercel · webapp/      │
                 │    Static dashboard UI      │
                 └──────────────┬───────────────┘
                                │ WebSocket
                                ▼
                 ┌──────────────────────────────┐
                 │      Render · backend/     │
                 │   HTTP + WebSocket service  │
                 └──────────────┬───────────────┘
                                │
                                ▼
                 ┌──────────────────────────────┐
                 │       Core analysis         │
                 │  Packets · Threats · Stats  │
                 └──────────────────────────────┘
```

</div>

| Component | Location | Hosting | Responsibility |
|---|---|---|---|
| Web console | `webapp/` | Vercel | Static dashboard interface |
| Backend service | `backend/` | Render | HTTP endpoints and WebSocket stream |
| Analysis engine | `core/` | Used by backend/local app | Packet analysis, anomaly detection, crypto heuristics, threat scoring |
| Local dashboard server | `frontend/` | Local machine | Local HTTP/WebSocket dashboard and capture workflow |

### Deploy the backend to Render

1. Import this repository into Render.
2. Create a **Blueprint** deployment using the root `render.yaml`.
3. Render uses `backend/` as the service root and `/health` as its health-check endpoint.
4. After deployment, copy the service URL. The WebSocket endpoint is:
   ```text
   wss://YOUR-RENDER-SERVICE.onrender.com/ws
   ```

### Deploy the frontend to Vercel

1. Import the same repository into Vercel.
2. Set the project **Root Directory** to `webapp`.
3. Use the **Other** framework preset; the static console does not need a build step.
4. Deploy, open the site, and configure its connection settings with the Render WebSocket URL.

**Hosted demo note:** standard Render hosting does not provide the raw-socket access needed for ordinary live interface sniffing. The hosted service is designed around simulated/demo traffic; use the local capture workflow on a machine with the required permissions for real network capture.

## 🗂️ Project structure

```text
Network-packet-analyzer/
├── backend/
│   ├── app.py                  # Hosted HTTP + WebSocket service
│   └── requirements.txt
├── core/
│   ├── sniffer.py              # Scapy capture and PCAP reader
│   ├── analyzer.py             # Packet/session statistics and flows
│   ├── anomaly.py              # Anomaly and attack heuristics
│   ├── crypto_detector.py      # Encrypted-payload heuristics
│   ├── threat.py               # Per-host threat scoring
│   ├── netinfo.py              # IP and service intelligence
│   └── live_engine.py          # Live host/network intelligence
├── frontend/
│   └── server.py               # Local HTTP + WebSocket server
├── webapp/
│   ├── index.html               # Browser dashboard
│   ├── style.css                # Dashboard design system
│   ├── app.js                   # Dashboard behaviour and streaming
│   └── vercel.json
├── reports/
│   └── reporter.py              # HTML and JSON report generation
├── utils/
│   ├── demo.py                  # Simulated traffic scenarios
│   ├── display.py               # Terminal presentation
│   └── logger.py                # Packet and alert logging
├── tests/
│   └── test_all.py              # Automated tests
├── main.py                      # CLI entry point
├── requirements.txt
├── render.yaml                  # Render Blueprint
├── Usage.md                     # Cross-platform usage guide
└── README.md
```

## 🧰 Built with

| Technology | Role |
|---|---|
| **Python** | Core application and analysis engine |
| **Scapy** | Live packet capture and PCAP parsing |
| **Sockets / WebSocket** | Local and hosted real-time communication |
| **HTML, CSS, JavaScript** | Browser dashboard |
| **Cryptography** | Optional cryptographic payload heuristics |
| **Render** | Hosted backend |
| **Vercel** | Static frontend hosting |
| **Pytest** | Automated tests |

## 🔐 Responsible use

NetScope is intended for learning, defensive analysis, and authorized network troubleshooting.

- Capture traffic only on networks and devices you own or are explicitly authorized to monitor.
- Packet captures may contain sensitive information. Store and share them carefully.
- Detection rules are heuristic and can produce false positives or miss threats.
- Do not treat a dashboard alert as proof of compromise without further investigation.

## 🛣️ Further improvements

Ideas for future development include expanded protocol coverage, configurable detection rules, richer PCAP investigation workflows, and additional test scenarios.

## 👨‍💻 Author

<div align="center">

**Arman Ahemad Khan**

Computer Science & Engineering · Network Security · Software Development

[![GitHub](https://img.shields.io/badge/GitHub-arman080325-181717?style=for-the-badge&logo=github)](https://github.com/arman080325)

</div>

## 📄 License

This project is distributed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

<div align="center">

**NetScope — Turn network packets into actionable visibility.**

<sub>Built with curiosity and care by Arman Ahemad Khan.</sub>

</div>
