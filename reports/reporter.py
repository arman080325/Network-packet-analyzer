"""
reports/reporter.py
-------------------
Generates self-contained HTML report + JSON export.
V2: richer layout with chart placeholders, conversation matrix,
    DNS query table, crypto breakdown.
"""

import json
import os
from datetime import datetime


class Reporter:

    def __init__(self, output_dir="reports/output"):
        os.makedirs(output_dir, exist_ok=True)
        self.output_dir = output_dir

    def generate(self, summary: dict, anomalies: dict, crypto: dict, elapsed: float, threat: dict = None) -> str:
        ts        = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_path = os.path.join(self.output_dir, f"report_{ts}.html")
        json_path = os.path.join(self.output_dir, f"report_{ts}.json")

        threat = threat or {"top": [], "hosts_tracked": 0}
        data = {
            "generated_at": datetime.now().isoformat(),
            "elapsed_sec":  elapsed,
            "summary":      summary,
            "anomalies":    anomalies,
            "crypto":       crypto,
            "threat":       threat,
        }
        with open(json_path, "w") as f:
            json.dump(data, f, indent=2, default=str)

        html = self._build_html(summary, anomalies, crypto, elapsed, ts, threat)
        with open(html_path, "w") as f:
            f.write(html)

        return html_path

    def _build_html(self, summary, anomalies, crypto, elapsed, ts, threat=None):
        threat = threat or {"top": []}
        # ── Threat board rows ─────────────────────────────────────────────
        lvl_color = {"malicious": "#ff4444", "suspicious": "#ffd740", "clean": "#00e676"}
        threat_rows = ""
        for r in threat.get("top", [])[:12]:
            c = lvl_color.get(r["level"], "#888")
            triggers = ", ".join(r["types"][:4])
            threat_rows += (
                f"<tr><td><b>{r['ip']}</b></td>"
                f"<td style='color:{c};font-weight:700'>{r['score']:.0f}</td>"
                f"<td><span style='color:{c};font-weight:700'>{r['level'].upper()}</span></td>"
                f"<td>{r['hits']}</td>"
                f"<td style='font-size:.8rem;color:var(--text2)'>{triggers}</td></tr>"
            )

        # ── Protocol table ────────────────────────────────────────────────
        proto_rows = "".join(
            f"<tr><td>{p}</td><td>{c:,}</td>"
            f"<td>{summary['bytes_per_proto'].get(p, 0) // 1024} KB</td>"
            f"<td>{c / max(summary['total_packets'], 1) * 100:.1f}%</td></tr>"
            for p, c in sorted(summary["protocol_counts"].items(), key=lambda x: -x[1])
        )

        # ── Alert rows ────────────────────────────────────────────────────
        alert_rows = ""
        for a in anomalies.get("alerts", []):
            sev = a.get("severity", "")
            c = {"CRITICAL": "#e74c3c", "WARNING": "#f39c12", "INFO": "#3498db"}.get(sev, "#888")
            alert_rows += (
                f"<tr><td>{a.get('time','')}</td>"
                f"<td><span style='color:{c};font-weight:700'>{sev}</span></td>"
                f"<td style='color:{c}'>{a.get('type','')}</td>"
                f"<td>{a.get('message','')}</td>"
                f"<td>{a.get('src','')}</td></tr>"
            )

        # ── Crypto rows ───────────────────────────────────────────────────
        crypto_rows = ""
        for d in crypto.get("detections", []):
            methods = " · ".join(f["method"] for f in d.get("findings", []))
            crypto_rows += (
                f"<tr><td>{d.get('timestamp','')}</td>"
                f"<td>{d.get('src','')}</td>"
                f"<td>{d.get('dst','')}:{d.get('dst_port','')}</td>"
                f"<td>{d.get('protocol','')}</td>"
                f"<td>{methods}</td>"
                f"<td>{d.get('payload_bytes',0)} B</td></tr>"
            )

        # ── Top talkers ───────────────────────────────────────────────────
        src_rows = "".join(
            f"<tr><td>{ip}</td><td>{cnt:,}</td></tr>"
            for ip, cnt in summary.get("top_src_ips", [])[:10]
        )
        dst_rows = "".join(
            f"<tr><td>{ip}</td><td>{cnt:,}</td></tr>"
            for ip, cnt in summary.get("top_dst_ips", [])[:10]
        )

        # ── DNS queries ───────────────────────────────────────────────────
        dns_rows = "".join(
            f"<tr><td>{d}</td><td>{c}</td></tr>"
            for d, c in summary.get("top_dns_domains", [])[:15]
        )

        # ── Port table ────────────────────────────────────────────────────
        port_rows = "".join(
            f"<tr><td>{p}</td><td>{c:,}</td></tr>"
            for p, c in summary.get("top_ports", [])[:10]
        )

        # ── Conversations ─────────────────────────────────────────────────
        conv_rows = "".join(
            f"<tr><td>{pair[0]}</td><td>⇄</td><td>{pair[1]}</td><td>{cnt:,}</td></tr>"
            for pair, cnt in summary.get("top_conversations", [])[:8]
        )

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Build Chart.js data
        proto_labels = list(summary["protocol_counts"].keys())[:8]
        proto_data   = [summary["protocol_counts"][p] for p in proto_labels]
        proto_colors = ['#64b5f6','#81c784','#ffb74d','#f48fb1',
                        '#80deea','#ce93d8','#80cbc4','#ff8a65']

        tl_labels = summary.get("timeline_labels", [])
        tl_bytes  = summary.get("timeline_bytes", [])

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>NetScope — Session Report {ts}</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
  :root {{
    --bg:#080c10; --surface:#0e1420; --surface2:#141c28;
    --border:#1e2d40; --accent:#00d4ff;
    --text:#cdd6e8; --text2:#6b7f99; --red:#ff4444;
    --yellow:#ffd740; --green:#00e676; --purple:#bb86fc;
  }}
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ font-family:'Segoe UI',system-ui,sans-serif; background:var(--bg); color:var(--text); padding:0; }}
  .page {{ max-width:1100px; margin:0 auto; padding:2rem; }}
  h1 {{ color:var(--accent); font-size:1.8rem; font-weight:800; letter-spacing:-0.5px; }}
  .subtitle {{ color:var(--text2); margin-top:.25rem; margin-bottom:2rem; font-size:.85rem; }}
  .grid4 {{ display:grid; grid-template-columns:repeat(4,1fr); gap:1rem; margin-bottom:2rem; }}
  .grid2 {{ display:grid; grid-template-columns:1fr 1fr; gap:1rem; margin-bottom:1.5rem; }}
  .card {{ background:var(--surface); border:1px solid var(--border); border-radius:10px; padding:1.25rem; }}
  .card .lbl {{ font-size:.7rem; text-transform:uppercase; letter-spacing:.06em; color:var(--text2); }}
  .card .val {{ font-size:1.8rem; font-weight:700; color:var(--accent); margin-top:.2rem; font-variant-numeric:tabular-nums; }}
  .card .sub {{ font-size:.75rem; color:var(--text2); margin-top:.15rem; }}
  h2 {{ color:var(--accent); font-size:1rem; font-weight:700; margin:1.5rem 0 .75rem;
        padding-bottom:.5rem; border-bottom:1px solid var(--border); letter-spacing:.02em; }}
  table {{ width:100%; border-collapse:collapse; font-size:.8rem; }}
  th {{ background:var(--surface2); color:var(--text2); font-weight:600; padding:.5rem .9rem;
        text-align:left; border-bottom:1px solid var(--border); font-size:.72rem;
        text-transform:uppercase; letter-spacing:.04em; }}
  td {{ padding:.4rem .9rem; border-bottom:1px solid rgba(30,45,64,0.8); }}
  tr:hover td {{ background:var(--surface2); }}
  .badge {{ display:inline-block; padding:.15rem .5rem; border-radius:4px; font-size:.7rem; font-weight:700; }}
  .br {{ background:rgba(255,68,68,.15); color:var(--red); }}
  .by {{ background:rgba(255,215,64,.15); color:var(--yellow); }}
  .bb {{ background:rgba(0,212,255,.12); color:var(--accent); }}
  .bg {{ background:rgba(0,230,118,.12); color:var(--green); }}
  .bp {{ background:rgba(187,134,252,.15); color:var(--purple); }}
  .chart-card {{ background:var(--surface); border:1px solid var(--border); border-radius:10px; padding:1rem; }}
  .chart-title {{ font-size:.7rem; text-transform:uppercase; letter-spacing:.06em; color:var(--text2); margin-bottom:.75rem; }}
  .two-col {{ display:grid; grid-template-columns:1fr 1fr; gap:1rem; margin-bottom:1rem; }}
  footer {{ margin-top:3rem; color:var(--text2); font-size:.75rem; border-top:1px solid var(--border); padding-top:1rem; }}
  @media(max-width:700px) {{ .grid4,.grid2,.two-col {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<div class="page">

<h1>🛡 NetScope — Session Report</h1>
<p class="subtitle">Generated {now_str} · Duration {elapsed:.1f}s · {summary['total_packets']:,} packets captured</p>

<div class="grid4">
  <div class="card"><div class="lbl">Total Packets</div><div class="val">{summary['total_packets']:,}</div><div class="sub">{summary['pps']} pkt/s</div></div>
  <div class="card"><div class="lbl">Data Transferred</div><div class="val">{summary['total_kb']} KB</div><div class="sub">{summary.get('avg_pkt_size',0):.0f} B avg</div></div>
  <div class="card"><div class="lbl">Anomaly Alerts</div><div class="val" style="color:var(--red)">{anomalies['total_alerts']}</div><div class="sub">{len(anomalies.get('by_type',{}))} attack types</div></div>
  <div class="card"><div class="lbl">Encrypted Payloads</div><div class="val" style="color:var(--purple)">{crypto['encrypted_payloads']}</div><div class="sub">avg entropy {crypto['avg_entropy']:.3f}</div></div>
  <div class="card"><div class="lbl">TCP Connections</div><div class="val" style="color:var(--green)">{summary.get('connections_est',0)}</div><div class="sub">{summary.get('connections_total',0)} total tracked</div></div>
  <div class="card"><div class="lbl">Retransmissions</div><div class="val" style="color:var(--yellow)">{summary.get('retransmissions',0)}</div><div class="sub">TCP retrans detected</div></div>
  <div class="card"><div class="lbl">Avg Latency</div><div class="val">{summary.get('avg_latency_ms',0):.1f}<span style="font-size:1rem"> ms</span></div><div class="sub">TCP handshake RTT</div></div>
  <div class="card"><div class="lbl">Fragments</div><div class="val" style="color:var(--orange,#ff9800)">{summary.get('fragments',0)}</div><div class="sub">Fragmented packets</div></div>
</div>

<!-- Charts -->
<div class="two-col">
  <div class="chart-card">
    <div class="chart-title">Traffic Timeline (bytes/sec)</div>
    <canvas id="ch-tl" height="120"></canvas>
  </div>
  <div class="chart-card">
    <div class="chart-title">Protocol Distribution</div>
    <canvas id="ch-proto" height="120"></canvas>
  </div>
</div>

<h2>Protocol Breakdown</h2>
<table>
  <thead><tr><th>Protocol</th><th>Packets</th><th>Data</th><th>Share</th></tr></thead>
  <tbody>{proto_rows}</tbody>
</table>

<div class="two-col" style="margin-top:1.5rem">
  <div>
    <h2>Top Source IPs</h2>
    <table><thead><tr><th>IP</th><th>Packets</th></tr></thead><tbody>{src_rows}</tbody></table>
  </div>
  <div>
    <h2>Top Destination IPs</h2>
    <table><thead><tr><th>IP</th><th>Packets</th></tr></thead><tbody>{dst_rows}</tbody></table>
  </div>
</div>

<div class="two-col">
  <div>
    <h2>Top Ports</h2>
    <table><thead><tr><th>Port</th><th>Hits</th></tr></thead><tbody>{port_rows}</tbody></table>
  </div>
  <div>
    <h2>DNS Queries</h2>
    {"<table><thead><tr><th>Domain</th><th>Count</th></tr></thead><tbody>" + dns_rows + "</tbody></table>" if dns_rows else "<p style='color:var(--text2);font-size:.85rem'>None observed</p>"}
  </div>
</div>

<h2>Conversations</h2>
{"<table><thead><tr><th>Host A</th><th></th><th>Host B</th><th>Packets</th></tr></thead><tbody>" + conv_rows + "</tbody></table>" if conv_rows else "<p style='color:var(--green);font-size:.85rem'>None tracked</p>"}

<h2>Threat Board — Highest-Risk Hosts</h2>
{"<p style='color:var(--green)'>✓ No high-risk hosts identified.</p>" if not threat_rows else
"<table><thead><tr><th>Host</th><th>Score</th><th>Level</th><th>Alerts</th><th>Triggers</th></tr></thead><tbody>" + threat_rows + "</tbody></table>"}

<h2>Anomaly Alerts</h2>
{"<p style='color:var(--green)'>✓ No anomalies detected.</p>" if not alert_rows else
"<table><thead><tr><th>Time</th><th>Severity</th><th>Type</th><th>Message</th><th>Source</th></tr></thead><tbody>" + alert_rows + "</tbody></table>"}

<h2>Encrypted Payload Detections</h2>
{"<p style='color:var(--green)'>✓ No encrypted payloads detected.</p>" if not crypto_rows else
"<table><thead><tr><th>Time</th><th>Source</th><th>Destination</th><th>Proto</th><th>Method</th><th>Size</th></tr></thead><tbody>" + crypto_rows + "</tbody></table>"}

<footer>
  NetScope v2.0 · Author: Arman Ahemad Khan · github.com/arman080325<br>
  JSON export: report_{ts}.json
</footer>
</div>

<script>
const PROTO_COLORS = {{'TCP':'#64b5f6','UDP':'#81c784','ICMP':'#ffb74d','ARP':'#f48fb1',
  'DNS':'#80cbc4','HTTPS':'#80deea','SSH':'#ce93d8','HTTP':'#a5d6a7','ICMPv6':'#ff8a65'}};

// Timeline chart
const tlCtx = document.getElementById('ch-tl').getContext('2d');
const grad = tlCtx.createLinearGradient(0,0,0,120);
grad.addColorStop(0,'rgba(0,212,255,0.3)');
grad.addColorStop(1,'rgba(0,212,255,0)');
new Chart(tlCtx, {{
  type: 'line',
  data: {{
    labels: {json.dumps(tl_labels[-30:])},
    datasets: [{{
      data: {json.dumps(tl_bytes[-30:])},
      borderColor:'#00d4ff', backgroundColor: grad,
      borderWidth:1.5, pointRadius:0, fill:true, tension:0.3
    }}]
  }},
  options: {{
    responsive:true, maintainAspectRatio:false, animation:false,
    plugins:{{legend:{{display:false}}}},
    scales:{{
      x:{{display:false}},
      y:{{ticks:{{color:'#6b7f99',font:{{size:9}}}},grid:{{color:'rgba(30,45,64,0.5)'}}}}
    }}
  }}
}});

// Protocol donut
const prLabels = {json.dumps(proto_labels)};
const prData   = {json.dumps(proto_data)};
const prColors = prLabels.map(p => PROTO_COLORS[p] || '#6b7f99');
new Chart(document.getElementById('ch-proto').getContext('2d'), {{
  type: 'doughnut',
  data: {{ labels: prLabels, datasets: [{{ data: prData, backgroundColor: prColors, borderWidth:0, hoverOffset:4 }}] }},
  options: {{
    responsive:true, maintainAspectRatio:false, animation:false, cutout:'60%',
    plugins:{{ legend:{{ display:true, position:'right',
      labels:{{ color:'#6b7f99', font:{{size:9}}, boxWidth:8, padding:6 }}
    }}}}
  }}
}});
</script>
</body>
</html>"""