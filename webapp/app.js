// NetScope web console — connects to the NetScope backend over WebSocket
// and renders the same wire protocol the original dashboard used:
//   {type:"init", packets:[...], alerts:[...], stats:{...}}
//   {type:"packet", packet:{...}, alerts:[...], stats:{...}}
//   {type:"heartbeat", stats:{...}}

(() => {
  const STORAGE_KEY = "netscope.ws_url";
  const MAX_STREAM_ROWS = 200;
  const MAX_FEED_ITEMS = 60;

  const $ = (sel) => document.querySelector(sel);
  const el = {
    connIndicator: $("#conn-indicator"),
    connDot: $("#conn-dot"),
    connLabel: $("#conn-label"),
    dialog: $("#conn-dialog"),
    wsInput: $("#ws-url-input"),
    connCancel: $("#conn-cancel"),
    connForm: $("#conn-form"),

    statPackets: $("#stat-packets"),
    statPps: $("#stat-pps"),
    statEnc: $("#stat-enc"),
    statUptime: $("#stat-uptime"),

    entropyValue: $("#entropy-value"),
    entropyFill: $("#entropy-fill"),
    threatTotal: $("#threat-total"),
    postureClean: $("#posture-clean"),
    postureSuspicious: $("#posture-suspicious"),
    postureMalicious: $("#posture-malicious"),
    countClean: $("#count-clean"),
    countSuspicious: $("#count-suspicious"),
    countMalicious: $("#count-malicious"),
    throughputValue: $("#throughput-value"),
    throughputCanvas: $("#throughput-canvas"),
    protocolBars: $("#protocol-bars"),

    mapSvg: $("#map-svg"),
    threatBody: $("#threat-table-body"),
    alertsFeed: $("#alerts-feed"),
    cryptoFeed: $("#crypto-feed"),
    detailView: $("#detail-view"),
    statsGrid: $("#stats-grid"),

    streamFilter: $("#stream-filter"),
    streamBody: $("#stream-body"),
  };

  // ── Connection management ────────────────────────────────────────────
  let ws = null;
  let reconnectTimer = null;
  let reconnectDelay = 1500;

function guessDefaultWsUrl() {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) return saved;
    return "wss://netscope-backend-ekkj.onrender.com/ws";
}

  function setConnState(state) {
    // state: "connecting" | "live" | "down"
    el.connDot.className = "conn-dot" + (state === "live" ? " live" : state === "down" ? " down" : "");
    el.connLabel.textContent =
      state === "live" ? "Live" : state === "down" ? "Disconnected — click to configure" : "Connecting…";
  }

  function connect(url) {
    if (ws) { try { ws.close(); } catch (e) {} }
    if (reconnectTimer) clearTimeout(reconnectTimer);
    setConnState("connecting");
    try {
      ws = new WebSocket(url);
    } catch (e) {
      setConnState("down");
      scheduleReconnect(url);
      return;
    }
    ws.onopen = () => { setConnState("live"); reconnectDelay = 1500; };
    ws.onclose = () => { setConnState("down"); scheduleReconnect(url); };
    ws.onerror = () => { setConnState("down"); };
    ws.onmessage = (evt) => {
      try {
        const msg = JSON.parse(evt.data);
        handleMessage(msg);
      } catch (e) { /* ignore malformed frame */ }
    };
  }

  function scheduleReconnect(url) {
    reconnectTimer = setTimeout(() => connect(url), reconnectDelay);
    reconnectDelay = Math.min(reconnectDelay * 1.6, 15000);
  }

  el.connIndicator.addEventListener("click", () => {
    el.wsInput.value = guessDefaultWsUrl();
    el.dialog.showModal();
  });
  el.connCancel.addEventListener("click", () => el.dialog.close());
  el.connForm.addEventListener("submit", (e) => {
    const url = el.wsInput.value.trim();
    if (!url) return;
    localStorage.setItem(STORAGE_KEY, url);
    connect(url);
  });

  // ── State ─────────────────────────────────────────────────────────────
  const hosts = new Map(); // ip -> {x,y,vx,vy,class}
  let throughputHistory = [];
  let lastPacketRow = null;
  let filterFn = () => true;

  // ── Message handling ──────────────────────────────────────────────────
  function handleMessage(msg) {
    if (msg.type === "init") {
      (msg.packets || []).forEach(addStreamRow);
      (msg.alerts || []).forEach(addAlert);
      renderStats(msg.stats);
    } else if (msg.type === "packet") {
      addStreamRow(msg.packet);
      (msg.alerts || []).forEach(addAlert);
      pulseNode(msg.packet);
      renderStats(msg.stats);
    } else if (msg.type === "heartbeat") {
      renderStats(msg.stats);
    }
  }

  // ── Top stat chips + gauges ─────────────────────────────────────────
  function renderStats(stats) {
    if (!stats) return;
    el.statPackets.textContent = fmtNum(stats.total_packets);
    el.statPps.textContent = (stats.pps ?? 0).toFixed ? stats.pps.toFixed(1) : stats.pps;
    el.statEnc.textContent = `${(stats.crypto?.encrypted_pct ?? 0).toFixed(1)}%`;
    el.statUptime.textContent = fmtUptime(stats.uptime_s || 0);

    const ent = stats.crypto?.last_entropy ?? 0;
    el.entropyValue.textContent = `${ent.toFixed ? ent.toFixed(2) : ent} bits/B`;
    el.entropyFill.style.width = `${Math.min(100, (ent / 8) * 100)}%`;

    const t = stats.threat || { hosts_tracked: 0, malicious: 0, suspicious: 0, top: [] };
    const clean = Math.max(0, t.hosts_tracked - t.malicious - t.suspicious);
    el.threatTotal.textContent = `${t.hosts_tracked} hosts`;
    const total = Math.max(1, t.hosts_tracked);
    el.postureClean.style.width = `${(clean / total) * 100}%`;
    el.postureSuspicious.style.width = `${(t.suspicious / total) * 100}%`;
    el.postureMalicious.style.width = `${(t.malicious / total) * 100}%`;
    el.countClean.textContent = clean;
    el.countSuspicious.textContent = t.suspicious;
    el.countMalicious.textContent = t.malicious;

    renderThreatTable(t.top || []);
    renderProtocolBars(stats.protocol_counts || {});
    renderThroughput(stats.throughput);
    renderStatsGrid(stats);

    (t.top || []).forEach((h) => setHostClass(h.ip, h.level || classify(h)));
  }

  function classify(h) {
    const score = h.score ?? 0;
    if (score >= 70) return "malicious";
    if (score >= 25) return "suspicious";
    return "clean";
  }

  function renderThreatTable(top) {
    el.threatBody.innerHTML = top.map((h) => {
      const cls = h.level || classify(h);
      const types = (h.types || []).join(", ") || "—";
      return `<tr><td>${esc(h.ip || "—")}</td><td>${esc(types)}</td>` +
             `<td>${(h.score ?? 0).toFixed ? h.score.toFixed(1) : h.score}</td>` +
             `<td><span class="badge ${cls}">${cls}</span></td></tr>`;
    }).join("") || `<tr><td colspan="4" style="color:var(--muted)">No hosts scored yet.</td></tr>`;
  }

  function renderProtocolBars(counts) {
    const max = Math.max(1, ...Object.values(counts));
    el.protocolBars.innerHTML = Object.entries(counts).map(([name, n]) => `
      <div class="protocol-row">
        <span class="name">${esc(name)}</span>
        <span class="bar"><i style="width:${(n / max) * 100}%"></i></span>
        <span class="n">${fmtNum(n)}</span>
      </div>`).join("");
  }

  function renderThroughput(t) {
    let val = 0;
    if (Array.isArray(t)) {
      const last = t[t.length - 1];
      val = typeof last === "number" ? last : (last?.bytes ?? last?.value ?? 0);
      throughputHistory = t.slice(-60);
    } else if (typeof t === "number") {
      val = t;
      throughputHistory.push(val);
      if (throughputHistory.length > 60) throughputHistory.shift();
    }
    el.throughputValue.textContent = fmtBytes(val) + "/s";
    drawSparkline(el.throughputCanvas, throughputHistory.map((v) => typeof v === "number" ? v : (v?.bytes ?? v?.value ?? 0)));
  }

  function drawSparkline(canvas, data) {
    const ctx = canvas.getContext("2d");
    const w = canvas.width, h = canvas.height;
    ctx.clearRect(0, 0, w, h);
    if (!data.length) return;
    const max = Math.max(1, ...data);
    ctx.beginPath();
    data.forEach((v, i) => {
      const x = (i / Math.max(1, data.length - 1)) * w;
      const y = h - (v / max) * (h - 6) - 3;
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    });
    ctx.strokeStyle = "#31F2A0";
    ctx.lineWidth = 1.6;
    ctx.stroke();
    ctx.lineTo(w, h); ctx.lineTo(0, h); ctx.closePath();
    ctx.fillStyle = "rgba(49,242,160,.12)";
    ctx.fill();
  }

  function renderStatsGrid(stats) {
    const cells = [
      ["Total bytes", fmtBytes(stats.total_bytes)],
      ["Connections (live)", fmtNum(stats.connections_est)],
      ["Connections (total)", fmtNum(stats.connections_total)],
      ["Retransmissions", fmtNum(stats.retransmissions)],
      ["Alerts (total)", fmtNum(stats.alerts_total)],
      ["Avg entropy", (stats.crypto?.avg_entropy ?? 0).toFixed ? stats.crypto.avg_entropy.toFixed(2) : 0],
    ];
    el.statsGrid.innerHTML = cells.map(([k, v]) =>
      `<div class="stats-cell"><div class="k">${esc(k)}</div><div class="v">${esc(String(v))}</div></div>`).join("");
  }

  // ── Alerts / crypto feeds ────────────────────────────────────────────
  function addAlert(a) {
    const sev = severityOf(a);
    const li = document.createElement("li");
    li.className = `feed-item sev-${sev}`;
    li.innerHTML = `<div class="row1"><span>${esc(a.type || "alert")}</span><span>${esc(a.time || "")}</span></div>` +
      `<div class="row2">${esc(a.message || JSON.stringify(a))}</div>`;
    el.alertsFeed.prepend(li);
    trimList(el.alertsFeed, MAX_FEED_ITEMS);

    if (a.src) setHostClass(a.src, sev === "high" ? "malicious" : "suspicious");
  }

  function addCrypto(c) {
    const li = document.createElement("li");
    li.className = "feed-item sev-low";
    li.innerHTML = `<div class="row1"><span>${esc((c.methods || []).join(", ") || "encrypted")}</span><span>${esc(c.timestamp || "")}</span></div>` +
      `<div class="row2">${esc(c.src)} → ${esc(c.dst)}:${esc(String(c.dst_port ?? ""))} · ${fmtBytes(c.bytes)}</div>`;
    el.cryptoFeed.prepend(li);
    trimList(el.cryptoFeed, MAX_FEED_ITEMS);
  }

  function severityOf(a) {
    const s = (a.severity || a.level || "").toString().toLowerCase();
    if (s.includes("high") || s.includes("crit")) return "high";
    if (s.includes("med") || s.includes("warn")) return "med";
    return "low";
  }

  function trimList(listEl, max) {
    while (listEl.children.length > max) listEl.removeChild(listEl.lastChild);
  }

  // ── Packet stream table ──────────────────────────────────────────────
  function addStreamRow(pkt) {
    if (!pkt) return;
    if (pkt.enc) addCrypto({ timestamp: pkt.timestamp, src: pkt.src_ip, dst: pkt.dst_ip, dst_port: pkt.dst_port, methods: pkt.enc_methods, bytes: pkt.length });

    const tr = document.createElement("tr");
    tr.dataset.raw = JSON.stringify(pkt);
    if (pkt.enc) tr.classList.add("enc");
    tr.innerHTML = `<td>${esc(pkt.timestamp || "")}</td><td>${esc(pkt.protocol || "")}</td>` +
      `<td>${esc(pkt.src_ip || "")}${pkt.src_port ? ":" + pkt.src_port : ""}</td>` +
      `<td>${esc(pkt.dst_ip || "")}${pkt.dst_port ? ":" + pkt.dst_port : ""}</td>` +
      `<td>${fmtNum(pkt.length)}</td><td>${esc(pkt.info || pkt.service || "")}</td>`;
    tr.style.display = filterFn(pkt) ? "" : "none";
    tr.addEventListener("click", () => showDetail(pkt));
    el.streamBody.prepend(tr);
    trimList(el.streamBody, MAX_STREAM_ROWS);
    lastPacketRow = pkt;

    setHostClass(pkt.src_ip, "clean", true);
  }

  function showDetail(pkt) {
    el.detailView.textContent = JSON.stringify(pkt, null, 2);
    document.querySelector('.tab[data-tab="detail"]').click();
  }

  function parseFilter(text) {
    const terms = text.trim().split(/\s+/).filter(Boolean);
    if (!terms.length) return () => true;
    const preds = terms.map((t) => {
      const [key, val] = t.includes(":") ? t.split(/:(.+)/) : [null, t];
      if (key === "ip") return (p) => p.src_ip === val || p.dst_ip === val;
      if (key === "proto") return (p) => (p.protocol || "").toLowerCase() === val.toLowerCase();
      if (key === "port") return (p) => String(p.src_port) === val || String(p.dst_port) === val;
      if (key === "enc") return (p) => String(!!p.enc) === val.toLowerCase();
      const needle = t.toLowerCase();
      return (p) => JSON.stringify(p).toLowerCase().includes(needle);
    });
    return (p) => preds.every((fn) => fn(p));
  }

  el.streamFilter.addEventListener("input", () => {
    filterFn = parseFilter(el.streamFilter.value);
    [...el.streamBody.children].forEach((tr) => {
      const pkt = JSON.parse(tr.dataset.raw);
      tr.style.display = filterFn(pkt) ? "" : "none";
    });
  });

  // ── Network radar map ─────────────────────────────────────────────────
  const NS = "http://www.w3.org/2000/svg";
  function ensureNode(ip) {
    if (hosts.has(ip)) return hosts.get(ip);
    const angle = Math.random() * Math.PI * 2;
    const r = 60 + Math.random() * 150;
    const node = {
      x: 300 + Math.cos(angle) * r,
      y: 230 + Math.sin(angle) * r * 0.8,
      cls: "clean",
    };
    hosts.set(ip, node);
    const g = document.createElementNS(NS, "g");
    g.setAttribute("data-ip", ip);
    const circle = document.createElementNS(NS, "circle");
    circle.setAttribute("cx", node.x);
    circle.setAttribute("cy", node.y);
    circle.setAttribute("r", ip.startsWith("192.168") || ip.startsWith("10.") ? 6 : 4.5);
    circle.setAttribute("class", "node-circle");
    circle.setAttribute("fill", colorFor("clean"));
    const label = document.createElementNS(NS, "text");
    label.setAttribute("x", node.x + 8);
    label.setAttribute("y", node.y + 3);
    label.setAttribute("class", "node-label");
    label.textContent = ip;
    g.appendChild(circle);
    g.appendChild(label);
    el.mapSvg.appendChild(g);
    node.g = g; node.circle = circle;
    return node;
  }

  function colorFor(cls) {
    return cls === "malicious" ? "#FF3E6C" : cls === "suspicious" ? "#FFB13C" : "#31F2A0";
  }

  function setHostClass(ip, cls, onlyIfUnset) {
    if (!ip) return;
    const node = ensureNode(ip);
    if (onlyIfUnset && node.cls !== "clean" && cls === "clean") return;
    if (rank(cls) < rank(node.cls) && onlyIfUnset) return;
    node.cls = cls;
    node.circle.setAttribute("fill", colorFor(cls));
    if (cls === "malicious") node.circle.setAttribute("r", 8);
  }
  function rank(cls) { return cls === "malicious" ? 2 : cls === "suspicious" ? 1 : 0; }

  function pulseNode(pkt) {
    if (!pkt || !pkt.src_ip) return;
    const node = ensureNode(pkt.src_ip);
    if (pkt.dst_ip) ensureNode(pkt.dst_ip);
    const pulse = document.createElementNS(NS, "circle");
    pulse.setAttribute("cx", node.x);
    pulse.setAttribute("cy", node.y);
    pulse.setAttribute("r", 2);
    pulse.setAttribute("fill", "none");
    pulse.setAttribute("stroke", colorFor(node.cls));
    pulse.setAttribute("stroke-width", "1.4");
    pulse.setAttribute("class", "node-pulse");
    el.mapSvg.appendChild(pulse);
    setTimeout(() => pulse.remove(), 1700);

    // cap node count so the map stays legible
    if (hosts.size > 60) {
      const oldest = hosts.keys().next().value;
      const old = hosts.get(oldest);
      if (old?.g) old.g.remove();
      hosts.delete(oldest);
    }
  }

  // ── Tabs ──────────────────────────────────────────────────────────────
  document.querySelectorAll(".tab").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach((b) => { b.classList.remove("active"); b.setAttribute("aria-selected", "false"); });
      document.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));
      btn.classList.add("active"); btn.setAttribute("aria-selected", "true");
      $("#tab-" + btn.dataset.tab).classList.add("active");
    });
  });

  // ── Formatting helpers ────────────────────────────────────────────────
  function fmtNum(n) { n = n || 0; return n.toLocaleString ? n.toLocaleString() : String(n); }
  function fmtBytes(n) {
    n = n || 0;
    if (n < 1024) return `${n.toFixed ? n.toFixed(0) : n} B`;
    if (n < 1024 ** 2) return `${(n / 1024).toFixed(1)} KB`;
    return `${(n / 1024 ** 2).toFixed(1)} MB`;
  }
  function fmtUptime(s) {
    s = Math.floor(s || 0);
    const h = String(Math.floor(s / 3600)).padStart(2, "0");
    const m = String(Math.floor((s % 3600) / 60)).padStart(2, "0");
    const sec = String(s % 60).padStart(2, "0");
    return `${h}:${m}:${sec}`;
  }
  function esc(str) {
    return String(str ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }

  // ── Boot ──────────────────────────────────────────────────────────────
  connect(guessDefaultWsUrl());
})();
