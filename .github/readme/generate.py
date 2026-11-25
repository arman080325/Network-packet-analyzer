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
# 1 · HERO — "scope lock": a 12-second story told on a live sensor mesh
#     monitor → anomaly → port scan → target lock → contained → reset
# ════════════════════════════════════════════════════════════════════════════
def vis(a, b, period, fade=0.12, peak=1, discrete=False):
    """Opacity animation: visible between a and b seconds of a looping period."""
    a, b = max(a, 0.001), min(b, period - 0.001)
    if discrete:
        return (f'<animate attributeName="opacity" dur="{period}s" repeatCount="indefinite" calcMode="discrete" '
                f'values="0;{peak};0" keyTimes="0;{a / period:.4f};{b / period:.4f}"/>')
    f = min(fade, (b - a) / 3)
    kts = [0, a, a + f, b - f, b, period]
    return (f'<animate attributeName="opacity" dur="{period}s" repeatCount="indefinite" '
            f'values="0;0;{peak};{peak};0;0" keyTimes="{";".join(f"{k / period:.4f}" for k in kts)}"/>')


def windows_anim(attr, windows, period, on, off):
    """Discrete attribute flips: `on` inside each (a, b) window, `off` elsewhere."""
    kt, vals = [0.0], [off]
    for a, b in windows:
        kt += [a, b]
        vals += [on, off]
    return (f'<animate attributeName="{attr}" dur="{period}s" repeatCount="indefinite" calcMode="discrete" '
            f'keyTimes="{";".join(f"{k / period:.4f}" for k in kt)}" values="{";".join(map(str, vals))}"/>')


def hero():
    import math
    W, H = 1280, 560
    P = 12.0                      # story period
    CYAN = "#4FD1FF"

    # ── left column: wordmark, typing console, packet anatomy ───────────────
    glitch_w = [(2.90, 2.98), (3.04, 3.16), (7.40, 7.47), (7.52, 7.60), (10.9, 11.0)]
    GP = 12.0
    wx, wy = 62, 214
    word = lambda fill, extra="": t(wx, wy, "NETSCOPE", 106, fill, 800, 74, extra=f'letter-spacing="2" {extra}')
    wordmark = f'''
    {word("url(#wordBase)")}
    {word("url(#shine)")}
    <g opacity="0" style="mix-blend-mode:screen">{windows_anim("opacity", glitch_w, GP, 1, 0)}
      <g transform="translate(-6 0)">{word(CYAN, 'opacity=".85"')}</g>
      <g transform="translate(6 0)">{word(DANGER, 'opacity=".85"')}</g>
    </g>
    <g opacity="0">{windows_anim("opacity", glitch_w, GP, 1, 0)}
      <g clip-path="url(#slice1)"><g transform="translate(22 0)">{word(TEXT)}</g></g>
      <g clip-path="url(#slice2)"><g transform="translate(-16 0)">{word(SIGNAL)}</g></g>
      <rect x="{wx - 10}" y="{wy - 44}" width="640" height="3" fill="{CYAN}" opacity=".7"/>
    </g>'''

    phrases = [
        "capture ▸ live NIC & .pcap · TCP · UDP · DNS · TLS",
        "detect  ▸ SYN floods · port scans · ARP spoofing",
        "score   ▸ per-host threat risk with time decay",
        "map     ▸ every alert to a MITRE ATT&CK technique",
    ]
    cw, fs, tx, ty = 10.0, 17, 86, 312
    period, slot = 18.0, 4.5
    typing_defs, typing_text = "", ""
    for i, p in enumerate(phrases):
        s0 = i * slot
        kts, vals = discrete_typing(len(p), cw, s0 + 0.05, s0 + 1.9, s0 + slot, period)
        typing_defs += f'''
    <clipPath id="tp{i}"><rect x="{tx}" y="{ty - 18}" height="26" width="0">
      <animate attributeName="width" dur="{period}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{kts}" values="{vals}"/>
    </rect></clipPath>'''
        typing_text += f'<g clip-path="url(#tp{i})">{t(tx, ty, p, fs, TEXT, 500, cw)}</g>'
    ckt, cvals = [0.0], [tx]
    for i, p in enumerate(phrases):
        s0, n = i * slot, len(p)
        for k in range(n + 1):
            ckt.append(s0 + 0.05 + 1.85 * k / n if k else s0 + 0.001)
            cvals.append(round(tx + k * cw + 2, 1))
    cursor = (f'<rect class="blink" x="{tx}" y="{ty - 16}" width="9" height="20" fill="{SIGNAL}">'
              f'<animate attributeName="x" dur="{period}s" repeatCount="indefinite" calcMode="discrete" '
              f'keyTimes="{";".join(f"{x / period:.4f}" for x in ckt)}" values="{";".join(map(str, cvals))}"/></rect>')

    # IPv4 header of the scanning packet: 203.0.113.45 → 10.0.0.12, TTL 64, TCP
    raw = "45 00 00 3C 1C 46 40 00 40 06 B1 E6 CB 00 71 2D 0A 00 00 0C".split()
    fields = [(0, 1, "VERSION · IHL", "IPv4 · 20-byte header", SIGNAL),
              (1, 1, "DSCP · ECN", "0x00 · best effort", MUTED),
              (2, 2, "TOTAL LENGTH", "0x003C → 60 bytes", CYAN),
              (4, 2, "IDENTIFICATION", "0x1C46", MUTED),
              (6, 2, "FLAGS · OFFSET", "DF · don't fragment", WARN),
              (8, 1, "TIME TO LIVE", "0x40 → 64 hops", SIGNAL),
              (9, 1, "PROTOCOL", "0x06 → TCP", ACCENT),
              (10, 2, "HEADER CHECKSUM", "0xB1E6 · verified", MUTED),
              (12, 4, "SOURCE", "203.0.113.45 · external", DANGER),
              (16, 4, "DESTINATION", "10.0.0.12 · web-01", SIGNAL)]
    bx, by, bw, bstep = 64, 386, 25, 27
    AP = len(fields) * 0.9
    anat = f'''
    {t(bx, by - 16, "▸ DISSECTING FRAME #4471", 12, SIGNAL, 800, 7.6)}
    {t(bx + 190, by - 16, "IPv4 header · 20 bytes · offset 0x0E", 12, DIM, 600, 7.0)}'''
    for i, b in enumerate(raw):
        anat += f'''
    <rect x="{bx + i * bstep}" y="{by}" width="{bw}" height="30" rx="4" fill="{SURF}" stroke="{LINE}"/>
    {t(bx + i * bstep + bw / 2, by + 20, b, 12.5, TEXT, 700, anchor="middle")}'''
    for s, n, _, _, col in fields:
        anat += f'<rect x="{bx + s * bstep + 1}" y="{by + 34}" width="{n * bstep - 3}" height="3" rx="1.5" fill="{col}" opacity=".8"/>'
    hx = ";".join(str(bx + f[0] * bstep - 3) for f in fields)
    hw = ";".join(str(f[1] * bstep + 4) for f in fields)
    hc = ";".join(f[4] for f in fields)
    hk = ";".join(f"{i / len(fields):.4f}" for i in range(len(fields)))
    anat += f'''
    <rect x="{bx - 3}" y="{by - 4}" width="{bstep + 4}" height="38" rx="6" fill="{SIGNAL}" fill-opacity=".1" stroke="{SIGNAL}" stroke-width="2" filter="url(#glow)">
      <animate attributeName="x" dur="{AP}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{hk}" values="{hx}"/>
      <animate attributeName="width" dur="{AP}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{hk}" values="{hw}"/>
      <animate attributeName="stroke" dur="{AP}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{hk}" values="{hc}"/>
      <animate attributeName="fill" dur="{AP}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{hk}" values="{hc}"/>
    </rect>
    <rect x="{bx}" y="{by + 48}" width="{len(raw) * bstep - 2}" height="44" rx="8" fill="{SURF2}" stroke="{LINE}"/>
    <path d="M{bx + 14} {by + 62}l6 8-6 8" fill="none" stroke="{SIGNAL}" stroke-width="2">
      <animate attributeName="stroke" dur="{AP}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{hk}" values="{hc}"/></path>'''
    for i, (s, n, lab, val, col) in enumerate(fields):
        anat += f'''
    <g opacity="0">{vis(i * 0.9, (i + 1) * 0.9, AP, discrete=True)}
      {t(bx + 34, by + 67, lab, 10.5, DIM, 800, 6.8)}
      {t(bx + 34, by + 84, val, 14, col, 700, 8.4)}
      {t(bx + len(raw) * bstep - 16, by + 76, f"bytes {s:02d}–{s + n - 1:02d}", 11, MUTED, 600, 6.8, anchor="end")}
    </g>'''

    # ── right column: sensor mesh + attack story ────────────────────────────
    SX, SY = 958, 312
    nodes = {"dns": ("dns-01", "10.0.0.53", 1004, 132), "web": ("web-01", "10.0.0.12", 772, 176),
             "db": ("db-01", "10.0.0.31", 752, 430), "gw": ("gw", "10.0.0.1", 944, 466),
             "ws": ("ws-07", "10.0.0.23", 1156, 446)}
    XX, XY = 1190, 172
    mesh = ""
    peers = [("dns", "web"), ("web", "db"), ("db", "gw"), ("gw", "ws")]
    for a, b in peers:
        _, _, x1, y1 = nodes[a]
        _, _, x2, y2 = nodes[b]
        mesh += f'<path d="M{x1} {y1}L{x2} {y2}" stroke="{LINE}" stroke-width="1.5"/>'
    for k, (_, _, x, y) in nodes.items():
        pid = f"sp_{k}"
        mesh += f'''
    <path id="{pid}" d="M{SX} {SY}L{x} {y}" stroke="{SIGNAL}" stroke-opacity=".22" stroke-width="1.5" stroke-dasharray="4 6">
      <animate attributeName="stroke-dashoffset" from="20" to="0" dur="1.2s" repeatCount="indefinite"/></path>'''
        d = 1.6 + (x % 7) * 0.15
        mesh += f'''
    <circle r="3" fill="{SIGNAL}"><animateMotion dur="{d:.2f}s" repeatCount="indefinite" keyPoints="1;0" keyTimes="0;1" calcMode="linear"><mpath href="#{pid}"/></animateMotion></circle>
    <circle r="2.5" fill="{TEXT}" opacity=".7"><animateMotion dur="{d * 1.4:.2f}s" begin="-{d / 2:.2f}s" repeatCount="indefinite"><mpath href="#{pid}"/></animateMotion></circle>'''

    sonar = "".join(f'''
    <circle cx="{SX}" cy="{SY}" r="40" fill="none" stroke="{SIGNAL}" stroke-width="1.5">
      <animate attributeName="r" values="40;300" dur="4s" begin="{b}s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values=".5;0" dur="4s" begin="{b}s" repeatCount="indefinite"/>
    </circle>''' for b in (0, 2))

    hits = {"dns": 3.9, "web": 4.3, "db": 4.7, "gw": 5.1, "ws": 5.5}
    node_svg, scan_svg = "", ""
    for k, (name, ip, x, y) in nodes.items():
        h = hits[k]
        node_svg += f'''
    <g>
      <polygon points="{hexpts(x, y, 13)}" fill="{VOID}" stroke="{SIGNAL}" stroke-width="2"/>
      <polygon points="{hexpts(x, y, 5)}" fill="{SIGNAL}"/>
      <g opacity="0">{vis(h, h + 1.1, P)}
        <polygon points="{hexpts(x, y, 13)}" fill="{WARN}" fill-opacity=".25" stroke="{WARN}" stroke-width="2.5" filter="url(#glow)"/>
        <circle cx="{x}" cy="{y}" r="13" fill="none" stroke="{WARN}" stroke-width="1.5">
          <animate attributeName="r" values="13;13;36;36" dur="{P}s" keyTimes="0;{h / P:.4f};{(h + 1.1) / P:.4f};1" repeatCount="indefinite"/>
        </circle>
        {t(x, y - 22, "PROBED", 9.5, WARN, 800, 6.4, anchor="middle")}
      </g>
      {t(x, y + 30, name, 11, TEXT, 700, 6.8, anchor="middle")}
      {t(x, y + 44, ip, 10, MUTED, 500, 6.1, anchor="middle")}
    </g>'''
        for j in range(3):
            a = h - 0.55 + j * 0.07
            scan_svg += f'''
    <circle r="{3 - j * 0.6:.1f}" fill="{DANGER}" filter="url(#glow)" opacity="0">{vis(a, a + 0.55, P, fade=0.04)}
      <animateMotion dur="{P}s" repeatCount="indefinite" path="M{XX} {XY}L{x} {y}" keyPoints="0;0;1;1" keyTimes="0;{a / P:.4f};{(a + 0.55) / P:.4f};1" calcMode="linear"/>
    </circle>'''
        scan_svg += f'''
    <path d="M{XX} {XY}L{x} {y}" stroke="{DANGER}" stroke-width="1.5" stroke-dasharray="2 5" opacity="0">{vis(h - 0.5, 9.2, P, peak=.55)}</path>'''

    # attacker, reticle, containment, threat card
    L = 6 * 30   # hex ring perimeter (r=30)
    br = "".join(f'<path d="M{dx * 26} {dy * 14}V{dy * 26}H{dx * 14}" fill="none" stroke="{DANGER}" stroke-width="3" stroke-linecap="round"/>'
                 for dx in (-1, 1) for dy in (-1, 1))
    attacker = f'''
    <g>
      <polygon points="{hexpts(XX, XY, 13)}" fill="{VOID}" stroke="{DIM}" stroke-width="2" stroke-dasharray="3 3"/>
      {t(XX, XY + 5, "?", 13, DIM, 800, anchor="middle")}
      <g opacity="0">{vis(3.3, 11.4, P)}
        <polygon points="{hexpts(XX, XY, 13)}" fill="{DANGER}" stroke="{DANGER}" stroke-width="2" filter="url(#glow)">
          <animate attributeName="fill-opacity" values="1;.35;1" dur=".5s" repeatCount="indefinite"/></polygon>
      </g>
      <g opacity="0">{vis(3.3, 11.4, P)}{t(XX, XY - 44, "203.0.113.45", 10.5, DANGER, 700, 6.6, anchor="middle")}</g>
      <g opacity="0">{vis(5.6, 8.8, P)}
        <g transform="translate({XX} {XY})">
          <g>
            <animateTransform attributeName="transform" type="scale" dur="{P}s" repeatCount="indefinite" values="2.6;2.6;1;1;1.12;1" keyTimes="0;{5.6 / P:.4f};{6.2 / P:.4f};{7.0 / P:.4f};{7.2 / P:.4f};1"/>
            <g><animateTransform attributeName="transform" type="rotate" dur="{P}s" repeatCount="indefinite" values="90;90;0;0" keyTimes="0;{5.6 / P:.4f};{6.2 / P:.4f};1"/>
              {br}
              <path d="M-36 0h8M28 0h8M0 -36v8M0 28v8" stroke="{DANGER}" stroke-width="2"/>
            </g>
          </g>
        </g>
      </g>
      <g opacity="0">{vis(8.6, 11.4, P)}
        <polygon points="{hexpts(XX, XY, 30)}" fill="{ACCENT}" fill-opacity=".1" stroke="{ACCENT}" stroke-width="3" stroke-dasharray="{L}" stroke-dashoffset="{L}" filter="url(#glow)">
          <animate attributeName="stroke-dashoffset" dur="{P}s" repeatCount="indefinite" values="{L};{L};0;0" keyTimes="0;{8.6 / P:.4f};{9.4 / P:.4f};1"/>
        </polygon>
        {t(XX, XY + 50, "QUARANTINED", 9.5, ACCENT, 800, 6.6, anchor="middle")}
      </g>
    </g>'''

    cx0, cy0, cwid, chei = 1034, 240, 214, 142
    scores = [(6.4, "18", WARN), (6.8, "41", WARN), (7.2, "63", WARN), (7.6, "82", DANGER)]
    score_svg = ""
    for i, (a, v, col) in enumerate(scores):
        b = scores[i + 1][0] if i + 1 < len(scores) else 11.4
        score_svg += f'<g opacity="0">{vis(a, b, P, discrete=True)}{t(cx0 + 16, cy0 + 124, v, 26, col, 800, 16)}</g>'
    card = f'''
    <g opacity="0">{vis(6.2, 11.4, P)}
      <rect x="{cx0}" y="{cy0}" width="{cwid}" height="{chei}" rx="10" fill="{SURF2}" fill-opacity=".96" stroke="{DANGER}" stroke-opacity=".7" stroke-width="1.5"/>
      <rect x="{cx0}" y="{cy0}" width="{cwid}" height="24" rx="10" fill="{DANGER}" fill-opacity=".16"/>
      <circle cx="{cx0 + 14}" cy="{cy0 + 12}" r="4" fill="{DANGER}"><animate attributeName="opacity" values="1;.2;1" dur=".6s" repeatCount="indefinite"/></circle>
      {t(cx0 + 24, cy0 + 16.5, "TARGET LOCKED", 11, DANGER, 800, 7.6)}
      {t(cx0 + cwid - 12, cy0 + 16.5, "#A-0217", 10, MUTED, 600, 6.2, anchor="end")}
      {t(cx0 + 16, cy0 + 46, "203.0.113.45", 15, TEXT, 800, 9)}
      {t(cx0 + 16, cy0 + 64, "PORT_SCAN · 5 hosts · 312 ports", 10.5, MUTED, 600, 6.2)}
      <rect x="{cx0 + 16}" y="{cy0 + 73}" width="148" height="18" rx="9" fill="{ACCENT}" fill-opacity=".16"/>
      {t(cx0 + 24, cy0 + 86, "T1046 · DISCOVERY", 10, ACCENT, 800, 7.6)}
      {t(cx0 + 16, cy0 + 104, "THREAT SCORE", 9.5, DIM, 800, 6.4)}
      {score_svg}
      <rect x="{cx0 + 62}" y="{cy0 + 112}" width="136" height="8" rx="4" fill="{SURF}"/>
      <rect x="{cx0 + 62}" y="{cy0 + 112}" width="0" height="8" rx="4" fill="url(#scoreBar)">
        <animate attributeName="width" dur="{P}s" repeatCount="indefinite" values="0;0;{136 * .82:.1f};{136 * .82:.1f};0" keyTimes="0;{6.3 / P:.4f};{7.6 / P:.4f};{11.3 / P:.4f};1"/></rect>
      <g opacity="0">{vis(7.6, 11.4, P, discrete=True)}{t(cx0 + 198, cy0 + 106, "MALICIOUS", 9.5, DANGER, 800, 6.4, anchor="end")}</g>
    </g>'''

    phases = [(0.0, 3.3, "●", "MONITORING", "5 hosts · 0 alerts · sonar sweep", SIGNAL),
              (3.3, 5.6, "▲", "ANOMALY", "unknown host probing the subnet", WARN),
              (5.6, 8.6, "◎", "LOCKED", "port scan → T1046 · scoring host", DANGER),
              (8.6, 12.0, "■", "CONTAINED", "host quarantined · IOC exported", ACCENT)]
    status = ""
    for a, b, ic, lab, txt, col in phases:
        status += f'''
    <g opacity="0">{vis(a, b, P, discrete=True)}
      {t(708, 92, ic, 13, col, 800)}
      {t(728, 92, lab, 12.5, col, 800, 8)}
      {t(728 + len(lab) * 8 + 14, 92, txt, 12, MUTED, 600, 7.0)}
    </g>'''
    # timeline scrubber for the story
    status += f'''
    <rect x="708" y="104" width="500" height="2" rx="1" fill="{LINE}"/>
    {"".join(f'<rect x="{708 + a / P * 500:.1f}" y="104" width="{(b - a) / P * 500 - 3:.1f}" height="2" rx="1" fill="{col}" opacity=".45"/>' for a, b, _, _, _, col in phases)}
    <circle cy="105" r="4" fill="{TEXT}" filter="url(#glow)"><animate attributeName="cx" values="708;1208" dur="{P}s" repeatCount="indefinite"/></circle>'''

    # hex-dump ticker
    dump = ("0000  45 00 00 3c 1c 46 40 00 40 06 b1 e6 cb 00 71 2d  E..<.F@.@.....q-     "
            "0010  0a 00 00 0c d4 31 00 16 5e 2b 7a 10 00 00 00 00  .....1..^+z.....     "
            "0020  a0 02 fa f0 3c 1e 00 00 02 04 05 b4 04 02 08 0a  ....<...........     ")
    dcw = 7.0
    ticker = f'''
    <g clip-path="url(#tickclip)" opacity=".55">
      <g><animateTransform attributeName="transform" type="translate" from="0 0" to="-{len(dump) * dcw:.1f} 0" dur="40s" repeatCount="indefinite"/>
        {t(40, H - 22, dump * 2, 11.5, DIM, 600, dcw)}
      </g>
    </g>'''

    corners = "".join(
        f'<path d="M{x} {y + 22 * sy}V{y}H{x + 22 * sx}" fill="none" stroke="{SIGNAL}" stroke-width="2" stroke-opacity=".7"/>'
        for x, y, sx, sy in [(18, 18, 1, 1), (W - 18, 18, -1, 1), (18, H - 18, 1, -1), (W - 18, H - 18, -1, -1)])

    hexs = "".join(f'<polygon points="{hexpts(px, py, 18)}" fill="none" stroke="#14233A" stroke-width="1"/>'
                   for px, py in [(0, 0), (31.18, 0), (15.59, 27), (0, 54), (31.18, 54)])

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="NetScope — a sensor mesh detects a port scan, locks on to the attacker and contains it">
  <title>NetScope — Network Packet Analyzer &amp; Threat Intelligence Console</title>
  <style>.blink{{animation:b 1s steps(1) infinite}}@keyframes b{{50%{{opacity:0}}}}{REDUCED}</style>
  <defs>{common_defs()}
    <pattern id="hexmesh" width="31.18" height="54" patternUnits="userSpaceOnUse">{hexs}</pattern>
    <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#FFFFFF" opacity=".025"/></pattern>
    <radialGradient id="meshFade" gradientUnits="userSpaceOnUse" cx="{SX}" cy="{SY}" r="560">
      <stop offset="0" stop-color="#fff" stop-opacity="1"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
    <mask id="meshMask"><rect width="{W}" height="{H}" fill="url(#meshFade)"/></mask>
    <radialGradient id="vignette" cx=".5" cy=".5" r=".75"><stop offset=".6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".65"/></radialGradient>
    <linearGradient id="wordBase" x1="0" x2="1"><stop offset="0" stop-color="{SIGNAL}"/><stop offset=".6" stop-color="#7FE8D8"/><stop offset="1" stop-color="{ACCENT}"/></linearGradient>
    <linearGradient id="shine" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".44" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#F2FFF9" stop-opacity=".9"/><stop offset=".56" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
      <animateTransform attributeName="gradientTransform" type="translate" values="-1 0;1.2 0" dur="5s" repeatCount="indefinite"/>
    </linearGradient>
    <linearGradient id="scoreBar" x1="0" x2="1"><stop offset="0" stop-color="{WARN}"/><stop offset="1" stop-color="{DANGER}"/></linearGradient>
    <clipPath id="slice1"><rect x="0" y="{wy - 62}" width="{W}" height="16"/></clipPath>
    <clipPath id="slice2"><rect x="0" y="{wy - 26}" width="{W}" height="9"/></clipPath>
    <clipPath id="right"><rect x="676" y="112" width="{W - 694}" height="{H - 160}"/></clipPath>
    <clipPath id="tickclip"><rect x="40" y="{H - 40}" width="{W - 80}" height="26"/></clipPath>
    <clipPath id="card"><rect width="{W}" height="{H}" rx="24"/></clipPath>
    {typing_defs}
  </defs>
  <g clip-path="url(#card)">
    <rect width="{W}" height="{H}" fill="{VOID}"/>
    <rect width="{W}" height="{H}" fill="url(#hexmesh)" mask="url(#meshMask)"/>
    <circle cx="220" cy="230" r="320" fill="url(#glowG)" opacity=".7"/>
    <circle cx="{SX}" cy="{SY}" r="360" fill="url(#glowA)"/>

    <!-- HUD -->
    {corners}
    {t(44, 50, "◢ NETSCOPE", 12, SIGNAL, 800, 7.6)}{t(130, 50, "// SOC-CONSOLE · SENSOR-01 · PASSIVE NDR", 12, DIM, 600, 7.2)}
    <circle cx="{W - 236}" cy="46" r="5" fill="{DANGER}"><animate attributeName="opacity" values="1;.15;1" dur="1.2s" repeatCount="indefinite"/></circle>
    {t(W - 224, 50, "REC", 12, DANGER, 800, 7.6)}{t(W - 190, 50, "18 pkt/s · ws:8765", 12, MUTED, 600, 7.6)}
    <rect x="40" y="66" width="{W - 80}" height="1" fill="{LINE}"/>
    <rect x="40" y="{H - 48}" width="{W - 80}" height="1" fill="{LINE}"/>

    <!-- left -->
    {t(64, 128, "[ PACKET ANALYZER ]", 12, ACCENT, 800, 8.4)}{t(236, 128, "+ THREAT INTELLIGENCE", 12, MUTED, 700, 8.4)}
    {wordmark}
    {t(66, 252, "see the traffic · understand the protocol · catch the anomaly", 14, MUTED, 600, 8.35)}
    {t(64, ty, "$", fs, SIGNAL, 800)}
    {typing_text}
    {cursor}
    {anat}

    <!-- right -->
    <rect x="676" y="78" width="1" height="{H - 140}" fill="{LINE}"/>
    {status}
    <g clip-path="url(#right)">
      {sonar}
      {mesh}
      {scan_svg}
    </g>
    {logo(SX, SY, .62)}
    {node_svg}
    {attacker}
    {card}

    {ticker}
    <rect width="{W}" height="{H}" fill="url(#scan)"/>
    <rect width="{W}" height="{H}" fill="url(#vignette)"/>
    <rect y="-60" width="{W}" height="60" fill="{SIGNAL}" opacity=".03"><animate attributeName="y" values="-60;{H}" dur="6s" repeatCount="indefinite"/></rect>
  </g>
  <rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="23.5" fill="none" stroke="#1C2A45" stroke-width="1.5"/>
</svg>'''


# ════════════════════════════════════════════════════════════════════════════
# 1b · TELEMETRY RACK — replaces generic shield badges
# ════════════════════════════════════════════════════════════════════════════
def rack():
    W, H = 1280, 150
    mods = [("RUNTIME", "PYTHON 3.8+", "stdlib-only demo & dashboard", SIGNAL, "cursor"),
            ("CAPTURE", "SCAPY · BPF", "live interfaces + .pcap replay", "#4FD1FF", "scope"),
            ("INTEL", "ATT&CK × 7", "techniques · 5 tactics mapped", DANGER, "cells"),
            ("STREAM", "WEBSOCKET", "init → packet → heartbeat", ACCENT, "flow"),
            ("QA", "PYTEST × 46", "analyzer → live NDR engine", WARN, "bars")]
    mw, gap, x0, y0, mh = 236, 12, 26, 18, 114
    s = ""
    for i, (lab, val, sub, col, viz) in enumerate(mods):
        x = x0 + i * (mw + gap)
        screws = "".join(f'<circle cx="{x + sx}" cy="{y0 + sy}" r="2.2" fill="{LINE}"/>' for sx in (8, mw - 8) for sy in (8, mh - 8))
        s += f'''
    <g>
      <rect x="{x}" y="{y0}" width="{mw}" height="{mh}" rx="12" fill="{SURF}" stroke="{LINE}" stroke-width="1.5"/>
      <rect x="{x + 14}" y="{y0}" width="{mw - 28}" height="2" fill="{col}" opacity=".9"/>
      {screws}
      <circle cx="{x + 22}" cy="{y0 + 26}" r="4" fill="{col}" filter="url(#glow)"><animate attributeName="opacity" values="1;.3;1" dur="{1.1 + i * .23:.2f}s" repeatCount="indefinite"/></circle>
      {t(x + 34, y0 + 30, lab, 11, col, 800, 7.6)}
      {t(x + mw - 18, y0 + 30, f"0{i + 1}", 11, DIM, 800, 7.6, anchor="end")}
      {t(x + 20, y0 + 64, val, 19, TEXT, 800, 11.2)}
      {t(x + 20, y0 + 84, sub, 10.5, MUTED, 500, 6.1)}'''
        vy = y0 + 96
        if viz == "cursor":
            s += f'''{t(x + 20, vy + 10, ">>> import netscope", 10.5, DIM, 600, 6.4)}
      <rect class="blink" x="{x + 20 + 22 * 6.4 + 3:.1f}" y="{vy + 1}" width="6" height="11" fill="{col}"/>'''
        elif viz == "scope":
            pts = " ".join(f"{k * 4},{6 * math_sin(k):.1f}" for k in range(0, 100))
            s += f'''
      <clipPath id="sc{i}"><rect x="{x + 20}" y="{vy - 4}" width="{mw - 40}" height="16"/></clipPath>
      <g clip-path="url(#sc{i})"><g transform="translate({x + 20} {vy + 5})">
        <polyline points="{pts}" fill="none" stroke="{col}" stroke-width="1.6" filter="url(#glow)">
          <animateTransform attributeName="transform" type="translate" from="0 0" to="-{4 * 20:.0f} 0" dur="1.4s" repeatCount="indefinite"/></polyline></g></g>'''
        elif viz == "cells":
            for k in range(7):
                s += f'''
      <rect x="{x + 20 + k * 28}" y="{vy}" width="24" height="10" rx="2" fill="{col}" opacity=".18">
        <animate attributeName="opacity" values=".18;.95;.18;.18" keyTimes="0;.06;.2;1" dur="3.5s" begin="{k * .5:.1f}s" repeatCount="indefinite"/></rect>'''
        elif viz == "flow":
            s += f'<rect x="{x + 20}" y="{vy + 4}" width="{mw - 40}" height="2" rx="1" fill="{LINE}"/>'
            for k in range(4):
                s += f'''
      <rect y="{vy + 1}" width="14" height="8" rx="4" fill="{col}" opacity=".85"><animate attributeName="x" values="{x + 20};{x + mw - 34}" dur="2.4s" begin="-{k * .6:.1f}s" repeatCount="indefinite"/></rect>'''
        elif viz == "bars":
            for k in range(10):
                s += f'''
      <rect x="{x + 20 + k * 19.6:.1f}" y="{vy}" width="16" height="10" rx="2" fill="{col}" opacity=".15">
        <animate attributeName="opacity" values=".15;.15;.9;.9;.15" keyTimes="0;{k * .07:.2f};{k * .07 + .02:.2f};.92;1" dur="4s" repeatCount="indefinite"/></rect>'''
        s += "\n    </g>"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Spec rack: Python 3.8+, Scapy, MITRE ATT&amp;CK, WebSocket, pytest">
  <title>NetScope spec rack</title>
  <style>.blink{{animation:b 1s steps(1) infinite}}@keyframes b{{50%{{opacity:0}}}}{REDUCED}</style>
  <defs>{common_defs()}</defs>
  {s}
</svg>'''


def math_sin(k):
    import math
    return math.sin(k * math.pi / 10) * (0.6 + 0.4 * math.sin(k * math.pi / 50 * 5))


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


for name, fn in [("hero", hero), ("rack", rack), ("terminal", terminal), ("architecture", architecture),
                 ("threat-board", threat_board), ("mitre-attack", mitre), ("divider", divider),
                 ("footer", footer)]:
    with open(os.path.join(OUT, f"{name}.svg"), "w") as f:
        f.write(fn())
    print("wrote", name)
