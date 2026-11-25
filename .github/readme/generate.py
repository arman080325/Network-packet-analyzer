#!/usr/bin/env python3
"""Generate the animated, brand-themed SVGs used by NetScope's README."""
import os
import sys
from html import escape

# usage: python .github/readme/generate.py  (writes the SVGs next to this file)
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
os.makedirs(OUT, exist_ok=True)

VOID, SURF, SURF2 = "#060911", "#0F1726", "#0A1120"
SIGNAL, WARN, DANGER, ACCENT = "#31F2A0", "#FFB13C", "#FF3E6C", "#8C6BFF"
TEXT, MUTED, DIM, LINE = "#EAF1FB", "#8493B2", "#5B6884", "#1B2944"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"
SANS = "Inter, system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"

REDUCED = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"


def t(x, y, s, size=14, fill=TEXT, weight=400, cw=None, anchor="start",
      family=MONO, extra=""):
    """Text element; when cw is given, glyph advance is fixed via textLength."""
    tl = f' textLength="{len(s) * cw:.1f}" lengthAdjust="spacingAndGlyphs"' if cw else ""
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" xml:space="preserve"{tl} {extra}>'
            f'{escape(s)}</text>')


def hexpts(cx, cy, r):
    import math
    return " ".join(f"{cx + r * math.cos(math.radians(a)):.2f},{cy + r * math.sin(math.radians(a)):.2f}"
                    for a in (-90, -30, 30, 90, 150, 210))


def logo(cx, cy, s):
    """NetScope hex-aperture mark with orbit ring, pulse and flagged packet dot."""
    import math
    R, r = 47 * s, 21 * s
    vx, vy = cx + R * math.cos(math.radians(-30)), cy + R * math.sin(math.radians(-30))
    return f'''
  <g>
    <circle cx="{cx}" cy="{cy}" r="{R * 1.9:.1f}" fill="url(#glowG)"/>
    <circle cx="{cx}" cy="{cy}" r="{R * 1.32:.1f}" fill="none" stroke="{SIGNAL}" stroke-opacity=".35"
      stroke-width="1.5" stroke-dasharray="3 9">
      <animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="18s" repeatCount="indefinite"/>
    </circle>
    <circle cx="{cx}" cy="{cy}" r="{R * 1.55:.1f}" fill="none" stroke="{ACCENT}" stroke-opacity=".25"
      stroke-width="1" stroke-dasharray="40 14 4 14">
      <animateTransform attributeName="transform" type="rotate" from="360 {cx} {cy}" to="0 {cx} {cy}" dur="26s" repeatCount="indefinite"/>
    </circle>
    <polygon points="{hexpts(cx, cy, R)}" fill="{VOID}" stroke="{SIGNAL}" stroke-width="{6 * s:.1f}"
      stroke-linejoin="round" filter="url(#glow)"/>
    <polygon points="{hexpts(cx, cy, r)}" fill="{SIGNAL}">
      <animate attributeName="opacity" values="1;.55;1" dur="2.4s" repeatCount="indefinite"/>
    </polygon>
    <circle cx="{vx:.2f}" cy="{vy:.2f}" r="{7 * s:.1f}" fill="{ACCENT}" filter="url(#glow)">
      <animate attributeName="r" values="{7 * s:.1f};{9.5 * s:.1f};{7 * s:.1f}" dur="1.6s" repeatCount="indefinite"/>
    </circle>
    <circle cx="{vx:.2f}" cy="{vy:.2f}" r="{7 * s:.1f}" fill="none" stroke="{ACCENT}" stroke-width="2">
      <animate attributeName="r" values="{7 * s:.1f};{24 * s:.1f}" dur="1.6s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values=".9;0" dur="1.6s" repeatCount="indefinite"/>
    </circle>
  </g>'''


def common_defs():
    return f'''
    <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse">
      <path d="M32 0H0V32" fill="none" stroke="#111C30" stroke-width="1"/>
    </pattern>
    <radialGradient id="glowG"><stop offset="0" stop-color="{SIGNAL}" stop-opacity=".28"/><stop offset="1" stop-color="{SIGNAL}" stop-opacity="0"/></radialGradient>
    <radialGradient id="glowA"><stop offset="0" stop-color="{ACCENT}" stop-opacity=".22"/><stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/></radialGradient>
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="3" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>'''


def discrete_typing(n, cw, start, end_type, hide, period):
    """keyTimes/values for a discrete width reveal (one char per step)."""
    kt, vals = [0.0], [0]
    for k in range(1, n + 1):
        kt.append(start + (end_type - start) * k / n)
        vals.append(round(k * cw, 1))
    if hide < period:
        kt.append(hide)
        vals.append(0)
    kts = ";".join(f"{x / period:.4f}" for x in kt)
    return kts, ";".join(str(v) for v in vals)


# ════════════════════════════════════════════════════════════════════════════
# 1 · HERO
# ════════════════════════════════════════════════════════════════════════════
def hero():
    W, H = 1280, 440
    cx, cy, rr = 1075, 196, 138
    phrases = [
        "capture ▸ live packets & .pcap · TCP · UDP · DNS · TLS",
        "detect  ▸ SYN floods · port scans · ARP spoofing",
        "score   ▸ per-host threat risk with time decay",
        "map     ▸ every alert to a MITRE ATT&CK technique",
    ]
    cw, fs, tx, ty = 10.2, 17, 296, 292
    period, slot = 18.0, 4.5
    typing = []
    for i, p in enumerate(phrases):
        s0 = i * slot
        kts, vals = discrete_typing(len(p), cw, s0 + 0.05, s0 + 1.9, s0 + slot, period)
        typing.append(f'''
    <clipPath id="tp{i}"><rect x="{tx}" y="{ty - 18}" height="26" width="0">
      <animate attributeName="width" dur="{period}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{kts}" values="{vals}"/>
    </rect></clipPath>''')
    typing_text = "".join(
        f'<g clip-path="url(#tp{i})">{t(tx, ty, p, fs, TEXT, 500, cw)}</g>' for i, p in enumerate(phrases))
    # cursor x follows typing
    ckt, cvals = [0.0], [tx]
    for i, p in enumerate(phrases):
        s0 = i * slot
        n = len(p)
        for k in range(0, n + 1):
            ckt.append(s0 + 0.05 + (1.85) * k / n if k else s0 + 0.001)
            cvals.append(round(tx + k * cw + 2, 1))
    ckts = ";".join(f"{x / period:.4f}" for x in ckt)
    cvs = ";".join(str(v) for v in cvals)

    blips = [  # angle-ish position, color, label, delay
        (cx + 62, cy - 70, SIGNAL, "10.0.0.12", 0.6),
        (cx - 88, cy - 30, WARN, "198.51.100.7 · 47", 1.6),
        (cx + 40, cy + 92, DANGER, "203.0.113.45 · 82", 2.5),
        (cx - 40, cy + 60, SIGNAL, "10.0.0.1 gw", 3.3),
        (cx + 104, cy + 18, ACCENT, "TLS 1.3", 1.1),
    ]
    blip_svg = ""
    for bx, by, col, lab, d in blips:
        blip_svg += f'''
    <g opacity="0">
      <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.06;.55;1" dur="4s" begin="{d}s" repeatCount="indefinite"/>
      <circle cx="{bx}" cy="{by}" r="4" fill="{col}" filter="url(#glow)"/>
      <circle cx="{bx}" cy="{by}" r="4" fill="none" stroke="{col}" stroke-width="1.5">
        <animate attributeName="r" values="4;16" dur="1.4s" begin="{d}s" repeatCount="indefinite"/>
        <animate attributeName="opacity" values="1;0" dur="1.4s" begin="{d}s" repeatCount="indefinite"/>
      </circle>
      {t(bx + 9, by - 7, lab, 11, col, 600)}
    </g>'''

    plist = [("TCP", SIGNAL), ("DNS", WARN), ("TLS", ACCENT), ("UDP", "#4FD1FF"),
             ("SYN!", DANGER), ("ARP", MUTED), ("ICMP", TEXT), ("HTTP", WARN)]
    packets = [(lab, col, 14, i * 14 / len(plist)) for i, (lab, col) in enumerate(plist)]
    pk_svg = ""
    for lab, col, dur, beg in packets:
        w = 14 + len(lab) * 8.5
        pk_svg += f'''
    <g>
      <animateTransform attributeName="transform" type="translate" from="-90 0" to="{W + 40} 0" dur="{dur}s" begin="-{beg}s" repeatCount="indefinite"/>
      <rect x="0" y="{H - 52}" width="{w:.0f}" height="20" rx="10" fill="{col}" fill-opacity=".14" stroke="{col}" stroke-opacity=".8"/>
      {t(w / 2, H - 37.5, lab, 11, col, 700, anchor="middle")}
      <rect x="{-60}" y="{H - 43}" width="56" height="2" fill="url(#trail)" opacity=".7"/>
    </g>'''

    chips = [("LIVE CAPTURE", SIGNAL), ("PCAP FORENSICS", ACCENT), ("MITRE ATT&CK", DANGER),
             ("WEBSOCKET STREAM", WARN)]
    chip_svg, cxp = "", 296
    for lab, col in chips:
        w = 30 + len(lab) * 8.2
        chip_svg += f'''
    <g>
      <rect x="{cxp}" y="320" width="{w:.0f}" height="28" rx="14" fill="{col}" fill-opacity=".08" stroke="{col}" stroke-opacity=".55"/>
      <circle cx="{cxp + 14}" cy="334" r="3.5" fill="{col}"><animate attributeName="opacity" values="1;.25;1" dur="1.8s" repeatCount="indefinite"/></circle>
      {t(cxp + 24, 338.5, lab, 11.5, col, 700, 7.6)}
    </g>'''
        cxp += w + 12

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="NetScope — network packet analyzer and threat intelligence console">
  <title>NetScope — Network Packet Analyzer &amp; Threat Intelligence Console</title>
  <style>.blink{{animation:b 1s steps(1) infinite}}@keyframes b{{50%{{opacity:0}}}}{REDUCED}</style>
  <defs>{common_defs()}
    <linearGradient id="word" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#FFFFFF" stop-opacity="0"/><stop offset=".42" stop-color="#FFFFFF" stop-opacity="0"/><stop offset=".5" stop-color="#E9FFF5" stop-opacity=".85"/><stop offset=".58" stop-color="#FFFFFF" stop-opacity="0"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/>
      <animateTransform attributeName="gradientTransform" type="translate" values="-1 0;1 0" dur="6s" repeatCount="indefinite"/>
    </linearGradient>
    <linearGradient id="wordBase" x1="0" x2="1"><stop offset="0" stop-color="{SIGNAL}"/><stop offset="1" stop-color="{ACCENT}"/></linearGradient>
    <linearGradient id="trail" x1="0" x2="1"><stop offset="0" stop-color="{TEXT}" stop-opacity="0"/><stop offset="1" stop-color="{TEXT}" stop-opacity=".6"/></linearGradient>
    <linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{SIGNAL}" stop-opacity="0"/><stop offset="1" stop-color="{SIGNAL}" stop-opacity=".45"/>
    </linearGradient>
    <linearGradient id="wire" x1="0" x2="1"><stop offset="0" stop-color="{LINE}" stop-opacity="0"/><stop offset=".5" stop-color="#2A3D63"/><stop offset="1" stop-color="{LINE}" stop-opacity="0"/></linearGradient>
    <clipPath id="card"><rect width="{W}" height="{H}" rx="22"/></clipPath>
    <clipPath id="radar"><circle cx="{cx}" cy="{cy}" r="{rr}"/></clipPath>
    {"".join(typing)}
  </defs>
  <g clip-path="url(#card)">
    <rect width="{W}" height="{H}" fill="{VOID}"/>
    <rect width="{W}" height="{H}" fill="url(#grid)" opacity=".9"/>
    <circle cx="{cx}" cy="{cy}" r="320" fill="url(#glowA)"/>
    <rect y="-40" width="{W}" height="40" fill="{SIGNAL}" opacity=".035">
      <animate attributeName="y" values="-40;{H}" dur="7s" repeatCount="indefinite"/>
    </rect>

    <!-- top bar -->
    {t(36, 38, "netscope://soc-console", 12, DIM, 500, 7.2)}
    <circle cx="{W - 238}" cy="34" r="5" fill="{DANGER}"><animate attributeName="opacity" values="1;.2;1" dur="1.2s" repeatCount="indefinite"/></circle>
    {t(W - 226, 38, "LIVE · 18 pkt/s · ws://8765", 12, MUTED, 600, 7.0)}

    {logo(150, 196, 1.18)}

    <!-- wordmark -->
    {t(292, 186, "NETSCOPE", 82, "url(#wordBase)", 800, 66, extra='letter-spacing="4"')}
    {t(292, 186, "NETSCOPE", 82, "url(#word)", 800, 66, extra='letter-spacing="4"')}
    {t(296, 228, "NETWORK PACKET ANALYZER  //  THREAT INTELLIGENCE CONSOLE", 14.5, MUTED, 600, 9.6)}

    <!-- typing console -->
    {t(tx - 22, ty, "$", fs, SIGNAL, 800)}
    {typing_text}
    <rect class="blink" x="{tx}" y="{ty - 16}" width="9" height="20" fill="{SIGNAL}">
      <animate attributeName="x" dur="{period}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{ckts}" values="{cvs}"/>
    </rect>

    {chip_svg}

    <!-- radar -->
    <g>
      <circle cx="{cx}" cy="{cy}" r="{rr}" fill="{SURF2}" fill-opacity=".85" stroke="#1E3A4F" stroke-width="1.5"/>
      <circle cx="{cx}" cy="{cy}" r="{rr * .66:.0f}" fill="none" stroke="#173246"/>
      <circle cx="{cx}" cy="{cy}" r="{rr * .33:.0f}" fill="none" stroke="#173246"/>
      <path d="M{cx - rr} {cy}H{cx + rr}M{cx} {cy - rr}V{cy + rr}" stroke="#173246"/>
      <g clip-path="url(#radar)">
        <g>
          <animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="4s" repeatCount="indefinite"/>
          <path d="M{cx} {cy} L{cx + rr} {cy} A{rr} {rr} 0 0 0 {cx + rr * 0.5:.1f} {cy - rr * 0.866:.1f} Z" fill="url(#sweep)" opacity=".75"/>
          <line x1="{cx}" y1="{cy}" x2="{cx + rr}" y2="{cy}" stroke="{SIGNAL}" stroke-width="2" filter="url(#glow)"/>
        </g>
      </g>
      <circle cx="{cx}" cy="{cy}" r="4" fill="{SIGNAL}"/>
      {blip_svg}
      {t(cx, cy + rr + 26, "HOST DISCOVERY · ARP / OUI", 11, DIM, 600, 7.1, anchor="middle")}
    </g>

    <!-- packet wire -->
    <rect x="0" y="{H - 43}" width="{W}" height="2" fill="url(#wire)"/>
    {pk_svg}
  </g>
  <rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="21.5" fill="none" stroke="#1C2A45" stroke-width="1.5"/>
</svg>'''
    return svg


# ════════════════════════════════════════════════════════════════════════════
# 2 · TERMINAL
# ════════════════════════════════════════════════════════════════════════════
def terminal():
    W, H = 1000, 470
    cw, fs, lh, x0, y0 = 8.4, 14, 27, 34, 92
    period = 16.0
    cmd = "python main.py --dashboard --demo"
    t_cmd_s, t_cmd_e = 0.4, 2.4
    lines = [  # list of (segments, colour per segment), reveal time
        ([("[*] ", ACCENT), ("NetScope engine online · demo traffic generator armed", TEXT)], 2.9),
        ([("[*] ", ACCENT), ("Dashboard  → ", MUTED), ("http://localhost:8080/dashboard.html", SIGNAL)], 3.3),
        ([("[*] ", ACCENT), ("WebSocket  → ", MUTED), ("ws://localhost:8765", SIGNAL)], 3.7),
        ([("[~] ", "#4FD1FF"), ("18 pkt/s   TCP 58%   UDP 21%   DNS 13%   ICMP 8%", MUTED)], 4.5),
        ([("[!] ", DANGER), ("SYN_FLOOD   ", DANGER), ("203.0.113.45 → 10.0.0.12:80    ", TEXT), ("score 82 ", MUTED), ("MALICIOUS", DANGER)], 5.6),
        ([("[!] ", WARN), ("PORT_SCAN   ", WARN), ("198.51.100.7 → 10.0.0.0/24     ", TEXT), ("score 47 ", MUTED), ("SUSPICIOUS", WARN)], 6.6),
        ([("[!] ", WARN), ("DNS_TUNNEL  ", WARN), ("10.0.0.23 → 8.8.8.8:53         ", TEXT), ("T1071.004 ", ACCENT), ("H=4.6", MUTED)], 7.6),
        ([("[+] ", SIGNAL), ("TLS 1.3     ", SIGNAL), ("10.0.0.12 → 142.250.0.10:443  ", TEXT), ("entropy 7.94 ", MUTED), ("ENCRYPTED", SIGNAL)], 8.5),
        ([("[+] ", SIGNAL), ("ARP sweep   6 assets resolved · gateway 10.0.0.1 verified", MUTED)], 9.4),
    ]
    body = ""
    # command typing
    kts, vals = discrete_typing(len(cmd), cw, t_cmd_s, t_cmd_e, period, period)
    body += f'''<clipPath id="cmdclip"><rect x="{x0 + 18}" y="{y0 - 18}" height="26" width="0">
      <animate attributeName="width" dur="{period}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{kts}" values="{vals}"/></rect></clipPath>'''
    defs = body
    body = t(x0, y0, "$", fs, SIGNAL, 800)
    body += f'<g clip-path="url(#cmdclip)">{t(x0 + 18, y0, cmd, fs, TEXT, 600, cw)}</g>'
    # cursor on cmd line
    ckt = [0] + [t_cmd_s + (t_cmd_e - t_cmd_s) * k / len(cmd) for k in range(1, len(cmd) + 1)] + [2.75]
    cvals = [x0 + 18] + [round(x0 + 18 + k * cw + 1, 1) for k in range(1, len(cmd) + 1)] + [-50]
    body += f'''<rect class="blink" x="{x0 + 18}" y="{y0 - 14}" width="8" height="18" fill="{SIGNAL}">
      <animate attributeName="x" dur="{period}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{';'.join(f'{k / period:.4f}' for k in ckt)}" values="{';'.join(map(str, cvals))}"/></rect>'''
    for i, (segs, at) in enumerate(lines):
        y = y0 + lh * (i + 1) + 6
        x = x0
        spans = ""
        for s, col in segs:
            spans += t(x, y, s, fs, col, 700 if col in (DANGER, WARN) and s.strip().isupper() else 500, cw)
            x += len(s) * cw
        k1 = at / period
        hl = ""
        if segs[0][1] == DANGER:
            hl = f'<rect x="{x0 - 12}" y="{y - 18}" width="{W - 2 * x0 + 24}" height="25" rx="5" fill="{DANGER}" fill-opacity=".09"><animate attributeName="fill-opacity" values=".2;.06;.2" dur="1.2s" repeatCount="indefinite"/></rect>'
        body += f'''
    <g opacity="0">
      <animate attributeName="opacity" dur="{period}s" repeatCount="indefinite" values="0;0;1;1;0" keyTimes="0;{k1:.4f};{k1 + 0.012:.4f};.975;1"/>
      <animateTransform attributeName="transform" type="translate" dur="{period}s" repeatCount="indefinite" values="0 6;0 6;0 0;0 0" keyTimes="0;{k1:.4f};{k1 + 0.02:.4f};1"/>
      {hl}{spans}
    </g>'''
    yl = y0 + lh * (len(lines) + 1) + 12
    k1 = 10.2 / period
    body += f'''
    <g opacity="0">
      <animate attributeName="opacity" dur="{period}s" repeatCount="indefinite" values="0;0;1;1;0" keyTimes="0;{k1:.4f};{k1 + .01:.4f};.975;1"/>
      {t(x0, yl, "$", fs, SIGNAL, 800)}
      <rect class="blink" x="{x0 + 18}" y="{yl - 14}" width="8" height="18" fill="{SIGNAL}"/>
    </g>'''

    # mini live gauge on the title bar right
    bars = ""
    for i in range(14):
        h = [6, 10, 7, 14, 9, 12, 5, 13, 8, 11, 6, 14, 9, 7][i]
        bars += f'<rect x="{W - 150 + i * 7}" y="{30 - h}" width="4" height="{h}" rx="1" fill="{SIGNAL}" opacity=".8"><animate attributeName="height" values="{h};{max(3, 16 - h)};{h}" dur="{0.9 + (i % 5) * 0.17:.2f}s" repeatCount="indefinite"/><animate attributeName="y" values="{30 - h};{30 - max(3, 16 - h)};{30 - h}" dur="{0.9 + (i % 5) * 0.17:.2f}s" repeatCount="indefinite"/></rect>'

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Terminal running python main.py --dashboard --demo and showing live detections">
  <title>NetScope demo session in the terminal</title>
  <style>.blink{{animation:b 1s steps(1) infinite}}@keyframes b{{50%{{opacity:0}}}}{REDUCED}</style>
  <defs>{common_defs()}{defs}
    <clipPath id="card"><rect width="{W}" height="{H}" rx="16"/></clipPath>
  </defs>
  <g clip-path="url(#card)">
    <rect width="{W}" height="{H}" fill="{SURF2}"/>
    <rect width="{W}" height="{H}" fill="url(#grid)" opacity=".5"/>
    <rect width="{W}" height="46" fill="{SURF}"/>
    <rect y="46" width="{W}" height="1" fill="{LINE}"/>
    <circle cx="26" cy="23" r="6.5" fill="{DANGER}"/><circle cx="48" cy="23" r="6.5" fill="{WARN}"/><circle cx="70" cy="23" r="6.5" fill="{SIGNAL}"/>
    {t(W / 2, 28, "netscope — demo session — 100×24", 12.5, MUTED, 600, 7.4, anchor="middle")}
    {bars}
    {body}
  </g>
  <rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="15.5" fill="none" stroke="#1C2A45" stroke-width="1.5"/>
</svg>'''


# ════════════════════════════════════════════════════════════════════════════
# 3 · ARCHITECTURE
# ════════════════════════════════════════════════════════════════════════════
def architecture():
    W, H = 1200, 540
    bw, bh = 190, 92
    xs = [40, 318, 596]
    ya, yc = 92, 360
    core_x, core_y, core_w, core_h = 884, 70, 280, 404

    def box(x, y, title, sub, tag, col):
        return f'''
    <g>
      <rect x="{x}" y="{y}" width="{bw}" height="{bh}" rx="12" fill="{SURF}" stroke="{LINE}" stroke-width="1.5"/>
      <rect x="{x}" y="{y}" width="{bw}" height="3" rx="1.5" fill="{col}"/>
      {t(x + 16, y + 32, title, 15, TEXT, 700, 8.6)}
      {t(x + 16, y + 54, sub, 11.5, MUTED, 500, 6.7)}
      <rect x="{x + 16}" y="{y + 64}" width="{len(tag) * 6.6 + 16:.0f}" height="18" rx="9" fill="{col}" fill-opacity=".12"/>
      {t(x + 24, y + 77, tag, 10.5, col, 700, 6.6)}
    </g>'''

    def link(x1, y1, x2, y2, col, label, dur, both=False, delay=0):
        pid = f"p{x1}{y1}{x2}{y2}"
        out = f'''
    <path id="{pid}" d="M{x1} {y1}H{x2}" stroke="{col}" stroke-opacity=".35" stroke-width="2" stroke-dasharray="6 6" fill="none">
      <animate attributeName="stroke-dashoffset" from="24" to="0" dur="1s" repeatCount="indefinite"/>
    </path>
    {t((x1 + x2) / 2, y1 - 10, label, 10.5, col, 700, 6.4, anchor="middle")}'''
        for k in range(3):
            out += f'''
    <circle r="4" fill="{col}" filter="url(#glow)"><animateMotion dur="{dur}s" begin="{delay + k * dur / 3:.2f}s" repeatCount="indefinite"><mpath href="#{pid}"/></animateMotion></circle>'''
        if both:
            out += f'''
    <circle r="3" fill="{TEXT}" opacity=".8"><animateMotion dur="{dur * 1.3:.1f}s" repeatCount="indefinite" keyPoints="1;0" keyTimes="0;1" calcMode="linear"><mpath href="#{pid}"/></animateMotion></circle>'''
        return out

    s = ""
    # lane labels
    s += t(40, 64, "HOSTED MODE", 12, SIGNAL, 800, 8) + t(140, 64, "· Vercel + Render · simulated traffic", 12, DIM, 500, 7.1)
    s += t(40, 332, "LOCAL MODE", 12, ACCENT, 800, 8) + t(132, 332, "· your machine · real interfaces & .pcap", 12, DIM, 500, 7.1)
    # row A
    s += box(xs[0], ya, "Browser", "analyst · any device", "HTTPS", "#4FD1FF")
    s += box(xs[1], ya, "webapp/", "static SOC console", "VERCEL", TEXT)
    s += box(xs[2], ya, "backend/app.py", "HTTP API · /ws stream", "RENDER", SIGNAL)
    # row C
    s += box(xs[0], yc, "NIC · .pcap", "eth0 · Wi-Fi · captures", "SCAPY", WARN)
    s += box(xs[1], yc, "main.py", "CLI · filters · reports", "PYTHON", ACCENT)
    s += box(xs[2], yc, "frontend/server.py", ":8080 HTTP · :8765 WS", "LOCALHOST", ACCENT)
    # links
    s += link(xs[0] + bw, ya + bh / 2, xs[1], ya + bh / 2, "#4FD1FF", "load UI", 2.2)
    s += link(xs[1] + bw, ya + bh / 2, xs[2], ya + bh / 2, SIGNAL, "WSS frames", 1.8, both=True)
    s += link(xs[2] + bw, ya + bh / 2, core_x, ya + bh / 2, SIGNAL, "analyse", 2.0, delay=.4)
    s += link(xs[0] + bw, yc + bh / 2, xs[1], yc + bh / 2, WARN, "raw packets", 1.6)
    s += link(xs[1] + bw, yc + bh / 2, xs[2], yc + bh / 2, ACCENT, "--dashboard", 2.0)
    s += link(xs[2] + bw, yc + bh / 2, core_x, yc + bh / 2, ACCENT, "analyse", 2.0, delay=.3)

    # event ticker between the lanes
    events = "packet ▸ alert ▸ stats ▸ threat ▸ host ▸ flow ▸ mitre ▸ ioc ▸ " * 4
    s += f'''
    <rect x="40" y="222" width="{xs[2] + bw - 40}" height="52" rx="10" fill="{VOID}" stroke="{LINE}"/>
    {t(56, 243, "REAL-TIME EVENT BUS", 10.5, DIM, 800, 7)}
    <clipPath id="tick"><rect x="52" y="246" width="{xs[2] + bw - 64}" height="24"/></clipPath>
    <g clip-path="url(#tick)">
      <g><animateTransform attributeName="transform" type="translate" from="0 0" to="-{len(events) / 4 * 7.4:.1f} 0" dur="9s" repeatCount="indefinite"/>
        {t(56, 263, events, 12.5, MUTED, 600, 7.4)}
      </g>
    </g>'''

    # core box
    mods = [("sniffer.py", "capture · pcap reader", WARN), ("analyzer.py", "sessions · flows · talkers", "#4FD1FF"),
            ("anomaly.py", "floods · scans · spoofing", DANGER), ("crypto_detector.py", "entropy · TLS · SSH", ACCENT),
            ("threat.py", "decaying host scores", DANGER), ("netinfo.py", "IP class · services", MUTED),
            ("live_engine.py", "NDR · MITRE · IOC export", SIGNAL)]
    s += f'''
    <rect x="{core_x}" y="{core_y}" width="{core_w}" height="{core_h}" rx="16" fill="{SURF}" stroke="{SIGNAL}" stroke-opacity=".45" stroke-width="1.5"/>
    <rect x="{core_x}" y="{core_y}" width="{core_w}" height="{core_h}" rx="16" fill="none" stroke="{SIGNAL}" stroke-width="2" filter="url(#glow)">
      <animate attributeName="stroke-opacity" values=".05;.5;.05" dur="3s" repeatCount="indefinite"/></rect>
    {t(core_x + 22, core_y + 36, "core/", 20, SIGNAL, 800, 12)}
    {t(core_x + 92, core_y + 36, "analysis engine", 12, MUTED, 600, 7.2)}'''
    for i, (m, d, col) in enumerate(mods):
        yy = core_y + 62 + i * 47
        s += f'''
    <g>
      <rect x="{core_x + 16}" y="{yy}" width="{core_w - 32}" height="38" rx="8" fill="{SURF2}" stroke="{LINE}"/>
      <rect x="{core_x + 16}" y="{yy}" width="{core_w - 32}" height="38" rx="8" fill="{col}" opacity="0">
        <animate attributeName="opacity" values="0;.16;0;0" keyTimes="0;.06;.16;1" dur="5.6s" begin="{i * 0.8:.1f}s" repeatCount="indefinite"/></rect>
      <circle cx="{core_x + 34}" cy="{yy + 19}" r="4.5" fill="{col}"><animate attributeName="opacity" values="1;.3;1" dur="{1.4 + i * .13:.2f}s" repeatCount="indefinite"/></circle>
      {t(core_x + 48, yy + 17, m, 12.5, TEXT, 700, 7.5)}
      {t(core_x + 48, yy + 31, d, 10.5, MUTED, 500, 6.1)}
    </g>'''

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="NetScope architecture: hosted and local modes feeding the core analysis engine">
  <title>NetScope architecture</title>
  <style>{REDUCED}</style>
  <defs>{common_defs()}<clipPath id="card"><rect width="{W}" height="{H}" rx="20"/></clipPath></defs>
  <g clip-path="url(#card)">
    <rect width="{W}" height="{H}" fill="{VOID}"/>
    <rect width="{W}" height="{H}" fill="url(#grid)"/>
    {t(40, 36, "// SIGNAL PATH", 12, DIM, 800, 8)}
    {s}
    {t(W / 2, H - 22, "same core/ engine powers both modes — the hosted backend streams simulated traffic, local mode sniffs real interfaces", 11.5, DIM, 500, 6.6, anchor="middle")}
  </g>
  <rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="19.5" fill="none" stroke="#1C2A45" stroke-width="1.5"/>
</svg>'''


# ════════════════════════════════════════════════════════════════════════════
# 4 · THREAT BOARD
# ════════════════════════════════════════════════════════════════════════════
def threat_board():
    W, H = 1000, 330
    x0, tw = 250, 560
    hosts = [("203.0.113.45", "SYN flood · port 80", 82, DANGER, "MALICIOUS"),
             ("198.51.100.7", "port scan · 312 ports", 47, WARN, "SUSPICIOUS"),
             ("10.0.0.23", "DNS high-entropy labels", 31, WARN, "SUSPICIOUS"),
             ("10.0.0.12", "TLS 1.3 · normal", 8, SIGNAL, "CLEAN")]
    s = ""
    for i, (ip, why, sc, col, cls) in enumerate(hosts):
        y = 92 + i * 52
        full = tw * sc / 100
        decay = full * 0.78
        s += f'''
    <g>
      {t(40, y + 15, ip, 14.5, TEXT, 700, 8.6)}
      {t(40, y + 33, why, 11, MUTED, 500, 6.4)}
      <rect x="{x0}" y="{y + 4}" width="{tw}" height="16" rx="8" fill="{SURF}" stroke="{LINE}"/>
      <rect x="{x0}" y="{y + 4}" width="0" height="16" rx="8" fill="url(#bar{i})" filter="url(#glow)">
        <animate attributeName="width" values="0;0;{full:.1f};{full:.1f};{decay:.1f};0" keyTimes="0;{i * .04:.2f};{.25 + i * .04:.2f};.55;.9;1" dur="10s" repeatCount="indefinite"/>
      </rect>
      {t(x0 + tw + 20, y + 17, f"{sc:>3}", 16, col, 800, 10)}
      <rect x="{x0 + tw + 62}" y="{y + 1}" width="{len(cls) * 7.6 + 18:.0f}" height="22" rx="11" fill="{col}" fill-opacity=".13" stroke="{col}" stroke-opacity=".6"/>
      {t(x0 + tw + 71, y + 16.5, cls, 11, col, 800, 7.6)}
    </g>'''
    defs = "".join(
        f'<linearGradient id="bar{i}" x1="0" x2="1"><stop offset="0" stop-color="{c}" stop-opacity=".35"/><stop offset="1" stop-color="{c}"/></linearGradient>'
        for i, (_, _, _, c, _) in enumerate(hosts))
    m25, m70 = x0 + tw * .25, x0 + tw * .70
    marks = f'''
    <line x1="{m25}" y1="80" x2="{m25}" y2="296" stroke="{WARN}" stroke-opacity=".45" stroke-dasharray="3 5"/>
    <line x1="{m70}" y1="80" x2="{m70}" y2="296" stroke="{DANGER}" stroke-opacity=".45" stroke-dasharray="3 5"/>
    {t(m25, 312, "25 · suspicious", 10.5, WARN, 700, 6.4, anchor="middle")}
    {t(m70, 312, "70 · malicious", 10.5, DANGER, 700, 6.4, anchor="middle")}
    {t(x0, 312, "0", 10.5, DIM, 700)}{t(x0 + tw, 312, "100", 10.5, DIM, 700, anchor="end")}'''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Threat board: hosts ranked by weighted, time-decaying risk scores">
  <title>NetScope threat board</title>
  <style>{REDUCED}</style>
  <defs>{common_defs()}{defs}<clipPath id="card"><rect width="{W}" height="{H}" rx="18"/></clipPath></defs>
  <g clip-path="url(#card)">
    <rect width="{W}" height="{H}" fill="{VOID}"/>
    <rect width="{W}" height="{H}" fill="url(#grid)" opacity=".7"/>
    {t(40, 42, "THREAT BOARD", 15, TEXT, 800, 9.5)}
    {t(170, 42, "weighted alerts → per-host risk · scores decay over time", 12, MUTED, 500, 7)}
    <circle cx="{W - 150}" cy="38" r="5" fill="{DANGER}"><animate attributeName="opacity" values="1;.2;1" dur="1s" repeatCount="indefinite"/></circle>
    {t(W - 138, 42, "4 hosts tracked", 11.5, MUTED, 600, 6.8)}
    <rect x="40" y="60" width="{W - 80}" height="1" fill="{LINE}"/>
    {marks}
    {s}
  </g>
  <rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="17.5" fill="none" stroke="#1C2A45" stroke-width="1.5"/>
</svg>'''


# ════════════════════════════════════════════════════════════════════════════
# 5 · MITRE ATT&CK
# ════════════════════════════════════════════════════════════════════════════
def mitre():
    W, H = 1200, 300
    tiles = [("T1046", "Network Service", "Discovery", "Discovery", WARN),
             ("T1071.001", "Web Protocols", "(cleartext)", "Command & Control", WARN),
             ("T1071.004", "DNS Tunneling", "high entropy", "Command & Control", DANGER),
             ("T1571", "Non-Standard", "Port", "Command & Control", WARN),
             ("T1041", "Exfiltration", "over C2", "Exfiltration", DANGER),
             ("T1059", "Command &", "Scripting", "Execution", DANGER),
             ("T1557.002", "ARP Spoofing", "/ Poisoning", "Credential Access", DANGER)]
    tw, th, gap, x0, y0 = 152, 178, 12, 40, 78
    s, period = "", 8.4
    for i, (tid, n1, n2, tac, col) in enumerate(tiles):
        x = x0 + i * (tw + gap)
        b = i * period / len(tiles)
        s += f'''
    <g>
      <rect x="{x}" y="{y0}" width="{tw}" height="{th}" rx="12" fill="{SURF}" stroke="{LINE}" stroke-width="1.5"/>
      <rect x="{x}" y="{y0}" width="{tw}" height="{th}" rx="12" fill="{col}" fill-opacity=".07" stroke="{col}" stroke-width="2" opacity="0">
        <animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;.01;.12;.14;1" dur="{period}s" begin="{b:.2f}s" repeatCount="indefinite"/>
      </rect>
      <rect x="{x + 14}" y="{y0 + 16}" width="{len(tac) * 6 + 14:.0f}" height="18" rx="9" fill="{ACCENT}" fill-opacity=".14"/>
      {t(x + 21, y0 + 29, tac.upper(), 9.5, ACCENT, 800, 6)}
      {t(x + 14, y0 + 70, tid, 19, TEXT, 800, 11.2 if len(tid) > 6 else 13)}
      {t(x + 14, y0 + 98, n1, 12.5, TEXT, 600)}
      {t(x + 14, y0 + 116, n2, 12.5, MUTED, 500)}
      <circle cx="{x + 20}" cy="{y0 + th - 24}" r="4" fill="{col}"/>
      <g opacity="0">
        <animate attributeName="opacity" values="0;1;0" keyTimes="0;.005;.14" calcMode="discrete" dur="{period}s" begin="{b:.2f}s" repeatCount="indefinite"/>
        {t(x + 30, y0 + th - 20, "DETECTED", 10, col, 800, 6.6)}
      </g>
      <g opacity="1">
        <animate attributeName="opacity" values="1;0;1" keyTimes="0;.005;.14" calcMode="discrete" dur="{period}s" begin="{b:.2f}s" repeatCount="indefinite"/>
        {t(x + 30, y0 + th - 20, "MONITORING", 10, DIM, 700, 6.6)}
      </g>
    </g>'''
    total = len(tiles) * (tw + gap) - gap
    s += f'''
    <rect x="{x0}" y="{y0 + th + 14}" width="{total}" height="3" rx="1.5" fill="{SURF}"/>
    <rect x="{x0}" y="{y0 + th + 14}" width="{tw}" height="3" rx="1.5" fill="{SIGNAL}" filter="url(#glow)">
      <animate attributeName="x" values="{';'.join(str(x0 + i * (tw + gap)) for i in range(len(tiles)))};{x0}" dur="{period}s" calcMode="discrete" repeatCount="indefinite"/>
    </rect>'''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="MITRE ATT&amp;CK techniques mapped by NetScope">
  <title>MITRE ATT&amp;CK techniques mapped by NetScope</title>
  <style>{REDUCED}</style>
  <defs>{common_defs()}<clipPath id="card"><rect width="{W}" height="{H}" rx="18"/></clipPath></defs>
  <g clip-path="url(#card)">
    <rect width="{W}" height="{H}" fill="{VOID}"/>
    <rect width="{W}" height="{H}" fill="url(#grid)" opacity=".7"/>
    {t(40, 46, "MITRE ATT&CK", 15, TEXT, 800, 9.5)}
    {t(170, 46, "every alert is tagged with a technique ID, tactic and severity", 12, MUTED, 500, 7)}
    {t(W - 40, 46, "7 techniques · 5 tactics", 11.5, SIGNAL, 700, 6.8, anchor="end")}
    {s}
  </g>
  <rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="17.5" fill="none" stroke="#1C2A45" stroke-width="1.5"/>
</svg>'''


# ════════════════════════════════════════════════════════════════════════════
# 6 · DIVIDER + FOOTER
# ════════════════════════════════════════════════════════════════════════════
def divider():
    W, H = 1200, 28
    nodes = "".join(
        f'<polygon points="{hexpts(x, 14, 5)}" fill="{VOID}" stroke="{SIGNAL}" stroke-opacity=".6" stroke-width="1.5"/>'
        for x in (300, 600, 900))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="presentation" aria-hidden="true">
  <style>{REDUCED}</style>
  <defs>
    <linearGradient id="ln" x1="0" x2="1"><stop offset="0" stop-color="{SIGNAL}" stop-opacity="0"/><stop offset=".5" stop-color="{SIGNAL}" stop-opacity=".55"/><stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/></linearGradient>
    <radialGradient id="pk"><stop offset="0" stop-color="{SIGNAL}"/><stop offset="1" stop-color="{SIGNAL}" stop-opacity="0"/></radialGradient>
  </defs>
  <rect y="13" width="{W}" height="2" fill="url(#ln)"/>
  {nodes}
  <g><animateTransform attributeName="transform" type="translate" from="-40 0" to="{W + 40} 0" dur="5s" repeatCount="indefinite"/>
    <ellipse cx="0" cy="14" rx="34" ry="6" fill="url(#pk)"/><circle cx="0" cy="14" r="3" fill="{TEXT}"/></g>
  <g><animateTransform attributeName="transform" type="translate" from="{W + 40} 0" to="-40 0" dur="7s" repeatCount="indefinite"/>
    <circle cx="0" cy="14" r="2.5" fill="{ACCENT}"/></g>
</svg>'''


def footer():
    W, H = 1200, 150
    pat = [(8, SIGNAL), (18, SIGNAL), (12, ACCENT), (26, SIGNAL), (10, WARN), (22, SIGNAL), (6, SIGNAL),
           (30, DANGER), (14, SIGNAL), (20, ACCENT), (9, SIGNAL), (24, SIGNAL), (12, WARN), (16, SIGNAL)]
    WAVE = "".join(f'<rect x="{680 + i * 24}" y="{75 - h}" width="10" height="{h * 2}" rx="3" fill="{c}" opacity=".55"/>'
                   for i, (h, c) in enumerate(pat * 3))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="End of capture">
  <title>NetScope — end of capture</title>
  <style>.blink{{animation:b 1s steps(1) infinite}}@keyframes b{{50%{{opacity:0}}}}{REDUCED}</style>
  <defs>{common_defs()}
    <linearGradient id="fade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{VOID}" stop-opacity="0"/><stop offset="1" stop-color="{VOID}"/></linearGradient>
    <clipPath id="card"><rect width="{W}" height="{H}" rx="18"/></clipPath>
  </defs>
  <g clip-path="url(#card)">
    <rect width="{W}" height="{H}" fill="{VOID}"/>
    <rect width="{W}" height="{H}" fill="url(#grid)" opacity=".8"/>
    {logo(92, 75, .55)}
    {t(160, 66, "EOF", 26, SIGNAL, 800, 17)}
    {t(222, 66, "capture closed · 0 packets dropped · stay curious", 15, TEXT, 600, 9)}
    {t(160, 96, "$ netscope --watch --forever", 13, MUTED, 600, 7.9)}
    <rect class="blink" x="{160 + 28 * 7.9 + 6:.1f}" y="84" width="8" height="15" fill="{SIGNAL}"/>
    <clipPath id="wave"><rect x="680" y="0" width="480" height="{H}"/></clipPath>
    <g clip-path="url(#wave)">
      <g>
        <animateTransform attributeName="transform" type="translate" values="0 0;-336 0" dur="9s" repeatCount="indefinite"/>
        {WAVE}
      </g>
      <rect x="680" width="60" height="{H}" fill="url(#fadeL)"/>
      <rect x="1100" width="60" height="{H}" fill="url(#fadeR)"/>
    </g>
  </g>
  <defs><linearGradient id="fadeL" x1="0" x2="1"><stop offset="0" stop-color="{VOID}"/><stop offset="1" stop-color="{VOID}" stop-opacity="0"/></linearGradient>
  <linearGradient id="fadeR" x1="0" x2="1"><stop offset="0" stop-color="{VOID}" stop-opacity="0"/><stop offset="1" stop-color="{VOID}"/></linearGradient></defs>
  <rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="17.5" fill="none" stroke="#1C2A45" stroke-width="1.5"/>
</svg>'''


for name, fn in [("hero", hero), ("terminal", terminal), ("architecture", architecture),
                 ("threat-board", threat_board), ("mitre-attack", mitre), ("divider", divider),
                 ("footer", footer)]:
    with open(os.path.join(OUT, f"{name}.svg"), "w") as f:
        f.write(fn())
    print("wrote", name)
