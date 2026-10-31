/**
 * NetScope — Enterprise Network Observability & Packet Intelligence Platform
 * Author: Arman Ahemad Khan (github.com/arman080325)
 * Architecture: High-performance, zero-build reactive single-page app
 * Complies with the approved Figma redesign and master brief specifications.
 */

(() => {
  'use strict';

  // ══════════════════════════════════════════════════════════════════════════
  //  Constants & Storage Keys
  // ══════════════════════════════════════════════════════════════════════════
  const STORAGE_WS_KEY = 'netscope.ws_url';
  const STORAGE_THEME_KEY = 'netscope.theme';
  const STORAGE_SIDEBAR_KEY = 'netscope.sidebar_collapsed';
  const MAX_PACKETS = 250;
  const MAX_ALERTS = 100;
  const MAX_THROUGHPUT_POINTS = 30;

  // ══════════════════════════════════════════════════════════════════════════
  //  Navigation & Screen Metadata (Approved Figma Hierarchy)
  // ══════════════════════════════════════════════════════════════════════════
  const NAV_GROUPS = [
    {
      label: 'Overview',
      items: [{ id: 'overview', name: 'Dashboard', icon: 'grid' }]
    },
    {
      label: 'Network monitoring',
      items: [
        { id: 'live', name: 'Live Traffic', icon: 'activity' },
        { id: 'packets', name: 'Packet Explorer', icon: 'packet' },
        { id: 'topology', name: 'Network Topology', icon: 'network' },
        { id: 'hosts', name: 'Hosts', icon: 'server' },
        { id: 'flows', name: 'Sessions & Flows', icon: 'flow' }
      ]
    },
    {
      label: 'Security',
      items: [
        { id: 'threats', name: 'Threat Intelligence', icon: 'shield' },
        { id: 'alerts', name: 'Security Alerts', icon: 'alert', badge: '12' },
        { id: 'encryption', name: 'Encryption Analysis', icon: 'lock' }
      ]
    },
    {
      label: 'Analytics',
      items: [
        { id: 'protocols', name: 'Protocol Analytics', icon: 'chart' },
        { id: 'reports', name: 'Reports', icon: 'report' }
      ]
    },
    {
      label: 'Configuration',
      items: [
        { id: 'capture', name: 'Capture Configuration', icon: 'sliders' },
        { id: 'settings', name: 'Settings', icon: 'settings' },
        { id: 'docs', name: 'Documentation', icon: 'book' }
      ]
    }
  ];

  const PAGE_META = {
    overview: ['Network Overview', 'Monitor network activity, traffic performance and security events.'],
    live: ['Live Traffic', 'Observe real-time packet stream, throughput and inspection details.'],
    packets: ['Packet Explorer', 'Inspect, filter and investigate captured network packets.'],
    topology: ['Network Topology', 'Explore host relationships and communication patterns.'],
    hosts: ['Host Inventory', 'Review observed hosts, activity and risk classification.'],
    flows: ['Sessions & Flows', 'Analyze communication flows and estimated connections.'],
    threats: ['Threat Intelligence', 'Prioritize heuristic findings and higher-risk hosts.'],
    alerts: ['Security Alerts', 'Investigate suspicious network behaviors and detections.'],
    encryption: ['Encryption Analysis', 'Assess payload entropy and encryption indicators.'],
    protocols: ['Protocol Analytics', 'Understand protocol usage, services and traffic trends.'],
    reports: ['Reports', 'Generate a summary of the current analysis session.'],
    capture: ['Capture Configuration', 'Configure live, simulated or offline analysis.'],
    settings: ['Settings', 'Customize the NetScope workspace and connection preferences.'],
    docs: ['Documentation', 'Understand capture, analysis and detection behavior.']
  };

  // ══════════════════════════════════════════════════════════════════════════
  //  Traffic Timeframe Datasets (1H, 6H, 24H)
  // ══════════════════════════════════════════════════════════════════════════
  const TRAFFIC_TIMEFRAME_DATA = {
    '1H': {
      throughput: '6.24',
      avgThroughput: '5.12',
      peakThroughput: '7.80',
      totalVolume: '2.14 GB',
      xLabels: ['14:00', '14:15', '14:30', '14:45', '15:00'],
      yLabels: ['12.0', '8.0', '4.0', '0'],
      pathArea: 'M0 158 C50 140 85 160 130 120 S205 130 250 105 S335 48 380 88 S470 120 520 64 S620 74 670 42 S755 68 800 34 V210H0Z',
      pathPrimary: 'M0 158 C50 140 85 160 130 120 S205 130 250 105 S335 48 380 88 S470 120 520 64 S620 74 670 42 S755 68 800 34',
      pathSecondary: 'M0 184 C70 166 110 180 155 152 S250 168 300 130 S390 155 440 122 S540 142 590 104 S690 126 735 91 S780 100 800 78'
    },
    '6H': {
      throughput: '8.45',
      avgThroughput: '6.18',
      peakThroughput: '11.40',
      totalVolume: '14.8 GB',
      xLabels: ['09:00', '10:30', '12:00', '13:30', '15:00'],
      yLabels: ['16.0', '12.0', '6.0', '0'],
      pathArea: 'M0 175 C60 160 120 130 180 90 S300 110 360 65 S440 30 510 45 S600 80 670 60 S740 40 800 52 V210H0Z',
      pathPrimary: 'M0 175 C60 160 120 130 180 90 S300 110 360 65 S440 30 510 45 S600 80 670 60 S740 40 800 52',
      pathSecondary: 'M0 190 C70 178 130 150 190 120 S310 135 370 95 S450 60 520 75 S610 105 680 88 S750 68 800 80'
    },
    '24H': {
      throughput: '14.20',
      avgThroughput: '4.95',
      peakThroughput: '15.80',
      totalVolume: '58.6 GB',
      xLabels: ['Yesterday 15:00', '21:00', '03:00', '09:00', 'Today 15:00'],
      yLabels: ['20.0', '14.0', '7.0', '0'],
      pathArea: 'M0 95 C80 110 140 145 220 170 S340 190 410 185 S500 130 580 80 S670 40 730 30 S770 45 800 38 V210H0Z',
      pathPrimary: 'M0 95 C80 110 140 145 220 170 S340 190 410 185 S500 130 580 80 S670 40 730 30 S770 45 800 38',
      pathSecondary: 'M0 125 C90 135 150 165 230 185 S350 200 420 196 S510 155 590 110 S680 75 740 60 S780 72 800 65'
    }
  };

  // ══════════════════════════════════════════════════════════════════════════
  //  Application State Store
  // ══════════════════════════════════════════════════════════════════════════
  const state = {
    activeRoute: 'live',
    previousRoute: 'overview',
    sidebarCollapsed: localStorage.getItem(STORAGE_SIDEBAR_KEY) === 'true',
    mobileMenuOpen: false,
    theme: localStorage.getItem(STORAGE_THEME_KEY) || 'dark',
    trafficTimeframe: '1H', // '1H' | '6H' | '24H'

    // Connection
    connState: 'connecting', // 'live' | 'demo' | 'connecting' | 'down'
    wsUrl: getInitialWsUrl(),
    uptimeSeconds: 0,
    isDemoMode: true,

    // Live Stream Controls
    paused: false,
    autoScroll: true,
    streamSearch: '',
    streamProtocol: 'ALL',
    selectedPacketId: null,

    // Core Data Buffers
    packets: [],
    alerts: [],
    stats: {
      total_packets: 18432,
      total_bytes: 312800000,
      pps: 42.8,
      throughput_mbps: 6.24,
      connections_est: 18,
      connections_total: 286,
      retransmissions: 42,
      protocol_counts: { TCP: 11428, UDP: 3872, ICMP: 1475, ARP: 922, DNS: 735 },
      top_hosts: [
        { ip: '192.168.1.24', class: 'Private', status: 'Suspicious', packets: 8642, bytes: '184.2 MB', score: 48, lastSeen: '4 sec ago' },
        { ip: '192.168.1.1', class: 'Private', status: 'Clean', packets: 4218, bytes: '91.7 MB', score: 4, lastSeen: '1 sec ago' },
        { ip: '10.0.0.42', class: 'Private', status: 'Malicious', packets: 2741, bytes: '58.4 MB', score: 82, lastSeen: '12 sec ago' },
        { ip: '172.217.14.206', class: 'Public', status: 'Clean', packets: 1882, bytes: '42.1 MB', score: 0, lastSeen: '5 sec ago' },
        { ip: '45.33.32.156', class: 'Public', status: 'Suspicious', packets: 486, bytes: '2.8 MB', score: 64, lastSeen: '16 sec ago' },
        { ip: '224.0.0.251', class: 'Multicast', status: 'Clean', packets: 312, bytes: '184 KB', score: 0, lastSeen: '28 sec ago' }
      ],
      throughputHistory: [
        { time: '14:00', in: 3.8, out: 1.8 },
        { time: '14:08', in: 4.5, out: 2.1 },
        { time: '14:16', in: 5.2, out: 2.4 },
        { time: '14:24', in: 4.8, out: 2.0 },
        { time: '14:32', in: 6.24, out: 2.7 }
      ],
      crypto: {
        encrypted: 14450,
        encrypted_pct: 78.4,
        avg_entropy: 7.14,
        recent_entropy: 7.62,
        high_entropy: 9842,
        methods: [
          ['TLS / SSL signatures', '8,942'],
          ['Shannon entropy', '4,182'],
          ['SSH banners', '486'],
          ['Port-based inference', '428'],
          ['Base64 heuristic', '312'],
          ['AES-GCM heuristic', '100']
        ]
      },
      flows: [
        { src: '192.168.1.24', dst: '172.217.14.206', proto: 'TCP', sport: 52418, dport: 443, pkts: 842, bytes: '82.4 MB', state: 'Established' },
        { src: '10.0.0.42', dst: '185.199.108.133', proto: 'TCP', sport: 49162, dport: 443, pkts: 484, bytes: '42.1 MB', state: 'Established' },
        { src: '192.168.1.16', dst: '192.168.1.1', proto: 'UDP', sport: 55192, dport: 53, pkts: 392, bytes: '28.8 MB', state: 'Established' },
        { src: '45.33.32.156', dst: '192.168.1.24', proto: 'TCP', sport: 42002, dport: 22, pkts: 244, bytes: '12.4 MB', state: 'SYN sent' },
        { src: '192.168.1.31', dst: '224.0.0.251', proto: 'UDP', sport: 5353, dport: 5353, pkts: 198, bytes: '8.2 MB', state: 'Established' },
        { src: '192.168.1.1', dst: '192.168.1.24', proto: 'ICMP', sport: '—', dport: '—', pkts: 164, bytes: '4.8 MB', state: 'Established' }
      ]
    }
  };

  // Seed initial sample packets matching Figma design
  state.packets = [
    { id: 18432, timestamp: '14:32:08.241', protocol: 'TCP', src_ip: '192.168.1.24', src_port: 52418, dst_ip: '172.217.14.206', dst_port: 443, length: 1428, flags: 'ACK', info: 'TLS Application Data', ttl: 64, src_class: 'Private', dst_class: 'Public', service: 'HTTPS', enc: true, enc_methods: ['TLS signature detected'] },
    { id: 18431, timestamp: '14:32:08.237', protocol: 'DNS', src_ip: '192.168.1.16', src_port: 55192, dst_ip: '192.168.1.1', dst_port: 53, length: 86, flags: '—', info: 'Standard query A api.github.com', ttl: 64, src_class: 'Private', dst_class: 'Private', service: 'DNS', enc: false },
    { id: 18430, timestamp: '14:32:08.216', protocol: 'TCP', src_ip: '10.0.0.42', src_port: 49162, dst_ip: '185.199.108.133', dst_port: 443, length: 1514, flags: 'PSH, ACK', info: 'TLS Application Data', ttl: 58, src_class: 'Private', dst_class: 'Public', service: 'HTTPS', enc: true, enc_methods: ['TLS signature detected'] },
    { id: 18429, timestamp: '14:32:08.192', protocol: 'UDP', src_ip: '192.168.1.31', src_port: 5353, dst_ip: '224.0.0.251', dst_port: 5353, length: 234, flags: '—', info: 'mDNS response PTR workstation.local', ttl: 255, src_class: 'Private', dst_class: 'Multicast', service: 'mDNS', enc: false },
    { id: 18428, timestamp: '14:32:08.154', protocol: 'ICMP', src_ip: '192.168.1.1', src_port: null, dst_ip: '192.168.1.24', dst_port: null, length: 98, flags: '—', info: 'Echo reply id=0x2f1 seq=442', ttl: 64, src_class: 'Private', dst_class: 'Private', service: 'ICMP', enc: false },
    { id: 18427, timestamp: '14:32:08.108', protocol: 'TCP', src_ip: '192.168.1.24', src_port: 52416, dst_ip: '104.18.32.47', dst_port: 443, length: 66, flags: 'SYN', info: '52416 → 443 [SYN] Seq=0', ttl: 64, src_class: 'Private', dst_class: 'Public', service: 'HTTPS', enc: false },
    { id: 18426, timestamp: '14:32:08.072', protocol: 'ARP', src_ip: '192.168.1.1', src_port: null, dst_ip: '192.168.1.18', dst_port: null, length: 60, flags: '—', info: 'Who has 192.168.1.18? Tell 192.168.1.1', ttl: null, src_class: 'Private', dst_class: 'Private', service: 'ARP', enc: false },
    { id: 18425, timestamp: '14:32:07.998', protocol: 'TCP', src_ip: '45.33.32.156', src_port: 42002, dst_ip: '192.168.1.24', dst_port: 22, length: 74, flags: 'SYN', info: '42002 → 22 [SYN] Seq=0', ttl: 48, src_class: 'Public', dst_class: 'Private', service: 'SSH', enc: false }
  ];
  state.selectedPacketId = 18432;

  // Seed sample alerts matching Figma design
  state.alerts = [
    { severity: 'High', type: 'Port Scan', src: '45.33.32.156', dst: '192.168.1.24', detail: '18 ports contacted in 4.2 seconds', timestamp: '14:31:52' },
    { severity: 'Suspicious', type: 'DNS Tunneling', src: '192.168.1.42', dst: '8.8.8.8', detail: 'Unusually long DNS query (148 chars)', timestamp: '14:29:18' },
    { severity: 'High', type: 'Credential Exposure', src: '10.0.0.18', dst: '172.16.4.20', detail: 'Cleartext FTP authentication pattern', timestamp: '14:22:07' },
    { severity: 'Info', type: 'Low TTL', src: '192.168.1.88', dst: '192.168.1.1', detail: 'Packet observed with TTL value of 2', timestamp: '14:18:40' },
    { severity: 'Suspicious', type: 'C2 Beaconing', src: '10.0.0.42', dst: '185.199.108.133', detail: 'Regular 60 second connection interval', timestamp: '14:12:16' }
  ];

  // ══════════════════════════════════════════════════════════════════════════
  //  Helper Functions
  // ══════════════════════════════════════════════════════════════════════════
  function $(sel, parent = document) {
    return parent.querySelector(sel);
  }

  function $$(sel, parent = document) {
    return Array.from(parent.querySelectorAll(sel));
  }

  function getInitialWsUrl() {
    const saved = localStorage.getItem(STORAGE_WS_KEY);
    if (saved) return saved;

    const loc = window.location;
    if (loc.hostname === 'localhost' || loc.hostname === '127.0.0.1') {
      // Local server uses single port 8080 (backend/app.py) or 8765 (frontend/server.py)
      const port = loc.port || '8080';
      return `ws://${loc.hostname}:${port}/ws`;
    }
    // Remote Render backend fallback
    return 'wss://netscope-backend-ekkj.onrender.com/ws';
  }

  function formatBytes(bytes) {
    if (!bytes || bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
  }

  function formatDuration(sec) {
    const s = Math.floor(sec || 0);
    const hrs = String(Math.floor(s / 3600)).padStart(2, '0');
    const mins = String(Math.floor((s % 3600) / 60)).padStart(2, '0');
    const secs = String(s % 60).padStart(2, '0');
    return `${hrs}:${mins}:${secs}`;
  }

  function icon(name, size = 16, extraClass = '') {
    const cls = extraClass ? ` ${extraClass}` : '';
    return `<svg class="icon${cls}" width="${size}" height="${size}" viewBox="0 0 24 24" aria-hidden="true" style="flex-shrink:0;"><use href="#icon-${name}"></use></svg>`;
  }

  function escapeHtml(str) {
    if (str === null || str === undefined) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  function copyToClipboard(text, btnElement) {
    if (!navigator.clipboard) return;
    navigator.clipboard.writeText(text).then(() => {
      if (btnElement) {
        const originalHtml = btnElement.innerHTML;
        btnElement.innerHTML = icon('check', 12);
        btnElement.style.color = 'var(--teal)';
        setTimeout(() => {
          btnElement.innerHTML = originalHtml;
          btnElement.style.color = '';
        }, 1500);
      }
    }).catch(() => {});
  }

  // ══════════════════════════════════════════════════════════════════════════
  //  WebSocket Engine & Lifecycle
  // ══════════════════════════════════════════════════════════════════════════
  let socket = null;
  let reconnectTimer = null;
  let reconnectDelay = 1500;
  let simulatedTrafficTimer = null;

  function initWebSocket() {
    if (socket) {
      try { socket.close(); } catch (e) {}
    }
    if (reconnectTimer) clearTimeout(reconnectTimer);

    updateConnectionUI('connecting');

    try {
      socket = new WebSocket(state.wsUrl);
    } catch (err) {
      updateConnectionUI('down');
      scheduleReconnect();
      startSimulatedFallback();
      return;
    }

    socket.onopen = () => {
      reconnectDelay = 1500;
      updateConnectionUI('live');
      stopSimulatedFallback();
    };

    socket.onclose = () => {
      updateConnectionUI('down');
      scheduleReconnect();
      startSimulatedFallback();
    };

    socket.onerror = () => {
      updateConnectionUI('down');
    };

    socket.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        handleServerMessage(msg);
      } catch (err) {
        // Ignore unparseable frames
      }
    };
  }

  function scheduleReconnect() {
    reconnectTimer = setTimeout(() => {
      initWebSocket();
    }, reconnectDelay);
    reconnectDelay = Math.min(reconnectDelay * 1.5, 12000);
  }

  function updateConnectionUI(status) {
    state.connState = status;
    const dot = $('#sidebar-conn-dot');
    const title = $('#sidebar-conn-title');
    const subtitle = $('#sidebar-conn-subtitle');
    const topBadge = $('#top-status-badge');
    const footerInfo = $('#footer-conn-info');

    if (dot) dot.className = `online-dot ${status === 'live' ? '' : status === 'down' ? 'down' : 'connecting'}`;
    
    if (title && subtitle) {
      if (status === 'live') {
        title.textContent = 'Backend connected';
        subtitle.textContent = `${state.isDemoMode ? 'Demo mode' : 'Live capture'} · ${Math.round(state.stats.pps || 18)} pps`;
      } else if (status === 'connecting') {
        title.textContent = 'Connecting…';
        subtitle.textContent = 'Attempting connection';
      } else {
        title.textContent = 'Disconnected';
        subtitle.textContent = 'Simulated feed active (Click to setup)';
      }
    }

    if (topBadge) {
      if (status === 'live') {
        topBadge.className = 'badge good';
        topBadge.innerHTML = '<i></i> Connected';
      } else if (status === 'connecting') {
        topBadge.className = 'badge warn';
        topBadge.innerHTML = '<i></i> Connecting';
      } else {
        topBadge.className = 'badge warn';
        topBadge.innerHTML = '<i></i> Offline · Simulated';
      }
    }

    if (footerInfo) {
      footerInfo.textContent = status === 'live' 
        ? `Backend connected · ${state.isDemoMode ? 'Demo feed' : 'Live feed'}`
        : 'Backend offline · Local simulation mode';
    }
  }

  function handleServerMessage(msg) {
    if (!msg || !msg.type) return;

    if (msg.type === 'init') {
      if (Array.isArray(msg.packets) && msg.packets.length > 0) {
        state.packets = msg.packets.slice(0, MAX_PACKETS);
        if (!state.selectedPacketId && state.packets[0]) {
          state.selectedPacketId = state.packets[0].id;
        }
      }
      if (Array.isArray(msg.alerts)) {
        state.alerts = msg.alerts.slice(0, MAX_ALERTS);
      }
      if (msg.stats) {
        mergeStats(msg.stats);
      }
      renderActivePage();
      return;
    }

    if (msg.type === 'packet') {
      if (msg.packet) {
        if (!state.paused) {
          state.packets.unshift(msg.packet);
          if (state.packets.length > MAX_PACKETS) {
            state.packets.pop();
          }
        }
      }
      if (Array.isArray(msg.alerts) && msg.alerts.length > 0) {
        msg.alerts.forEach((a) => state.alerts.unshift(a));
        if (state.alerts.length > MAX_ALERTS) {
          state.alerts = state.alerts.slice(0, MAX_ALERTS);
        }
      }
      if (msg.stats) {
        mergeStats(msg.stats);
      }

      // Fast-update visible page if on Live or Overview
      if (state.activeRoute === 'live') {
        updateLivePacketStreamIncremental(msg.packet);
      } else if (state.activeRoute === 'overview') {
        updateOverviewIncremental();
      }
      return;
    }

    if (msg.type === 'heartbeat') {
      if (msg.stats) {
        mergeStats(msg.stats);
      }
      state.uptimeSeconds = (state.stats.uptime_s || (state.uptimeSeconds + 1));
      updateTopMetricsDisplay();
    }
  }

  function mergeStats(incoming) {
    if (!incoming) return;
    state.stats.total_packets = incoming.total_packets ?? state.stats.total_packets;
    state.stats.total_bytes = incoming.total_bytes ?? state.stats.total_bytes;
    state.stats.pps = incoming.pps ?? state.stats.pps;
    state.stats.uptime_s = incoming.uptime_s ?? state.stats.uptime_s;
    if (incoming.protocol_counts) state.stats.protocol_counts = incoming.protocol_counts;
    if (incoming.crypto) state.stats.crypto = incoming.crypto;

    // Track throughput series
    const pps = state.stats.pps || 18;
    const mbps = parseFloat(((pps * 650 * 8) / 1000000).toFixed(2));
    state.stats.throughput_mbps = mbps;

    const history = state.stats.throughputHistory;
    const now = new Date();
    const timeStr = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`;
    history.push({ time: timeStr, in: mbps, out: parseFloat((mbps * 0.42).toFixed(2)) });
    if (history.length > MAX_THROUGHPUT_POINTS) history.shift();
  }

  // ══════════════════════════════════════════════════════════════════════════
  //  Simulated Traffic Generator (Active when backend is offline/disconnected)
  // ══════════════════════════════════════════════════════════════════════════
  let simSeq = 18432;
  function startSimulatedFallback() {
    if (simulatedTrafficTimer) return;
    simulatedTrafficTimer = setInterval(() => {
      if (state.connState === 'live') {
        stopSimulatedFallback();
        return;
      }

      simSeq++;
      const protos = ['TCP', 'UDP', 'DNS', 'ICMP', 'ARP'];
      const p = protos[Math.floor(Math.random() * protos.length)];
      const now = new Date();
      const timeStr = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}.${String(Math.floor(Math.random() * 999)).padStart(3, '0')}`;
      
      const newPkt = {
        id: simSeq,
        timestamp: timeStr,
        protocol: p,
        src_ip: `192.168.1.${Math.floor(Math.random() * 40) + 1}`,
        dst_ip: `10.0.0.${Math.floor(Math.random() * 50) + 1}`,
        src_port: p === 'ICMP' || p === 'ARP' ? null : Math.floor(Math.random() * 30000) + 1024,
        dst_port: p === 'ICMP' || p === 'ARP' ? null : (p === 'DNS' ? 53 : [80, 443, 22, 5353][Math.floor(Math.random() * 4)]),
        length: Math.floor(Math.random() * 1400) + 60,
        flags: p === 'TCP' ? ['SYN', 'ACK', 'PSH, ACK'][Math.floor(Math.random() * 3)] : '—',
        info: p === 'TCP' ? 'TCP traffic payload segment' : p === 'DNS' ? 'Query A record host' : `${p} packet segment`,
        ttl: 64,
        src_class: 'Private',
        dst_class: 'Private',
        service: p === 'DNS' ? 'DNS' : 'HTTPS',
        enc: Math.random() > 0.4
      };

      if (!state.paused) {
        state.packets.unshift(newPkt);
        if (state.packets.length > MAX_PACKETS) state.packets.pop();
      }

      state.stats.total_packets++;
      state.stats.total_bytes += newPkt.length;
      state.stats.pps = parseFloat((35 + Math.random() * 15).toFixed(1));

      if (state.activeRoute === 'live') {
        updateLivePacketStreamIncremental(newPkt);
      }
    }, 1200);
  }

  function stopSimulatedFallback() {
    if (simulatedTrafficTimer) {
      clearInterval(simulatedTrafficTimer);
      simulatedTrafficTimer = null;
    }
  }

  // ══════════════════════════════════════════════════════════════════════════
  //  UI Shell & Sidebar Navigation
  // ══════════════════════════════════════════════════════════════════════════
  function renderSidebar() {
    const navEl = $('#sidebar-nav');
    if (!navEl) return;

    let html = '';
    NAV_GROUPS.forEach((group) => {
      html += `<div class="nav-group">
        <label>${escapeHtml(group.label)}</label>`;
      group.items.forEach((item) => {
        const isActive = state.activeRoute === item.id;
        const badgeHtml = item.badge ? `<em>${escapeHtml(item.badge)}</em>` : '';
        html += `
          <button class="nav-item ${isActive ? 'active' : ''}" data-route="${item.id}" type="button" title="${escapeHtml(item.name)}">
            ${icon(item.icon, 18)}
            <span>${escapeHtml(item.name)}</span>
            ${badgeHtml}
          </button>
        `;
      });
      html += `</div>`;
    });

    navEl.innerHTML = html;

    // Attach click listeners
    $$('.nav-item', navEl).forEach((btn) => {
      btn.addEventListener('click', () => {
        const route = btn.getAttribute('data-route');
        navigateTo(route);
      });
    });
  }

  function navigateTo(routeId) {
    if (!PAGE_META[routeId]) routeId = 'live';
    if (state.activeRoute !== routeId && state.activeRoute !== 'settings') {
      state.previousRoute = state.activeRoute;
    }
    state.activeRoute = routeId;
    window.location.hash = `#${routeId}`;

    // Close mobile menu if open
    closeMobileMenu();

    // Update sidebar active highlights
    $$('.nav-item').forEach((btn) => {
      btn.classList.toggle('active', btn.getAttribute('data-route') === routeId);
    });

    // Update Topbar
    const [title, desc] = PAGE_META[routeId];
    const topIcon = $('#top-current-icon');
    const topTitle = $('#top-current-title');
    const item = NAV_GROUPS.flatMap(g => g.items).find(i => i.id === routeId);

    if (topTitle) topTitle.textContent = title;
    if (topIcon && item) topIcon.innerHTML = icon(item.icon, 18);

    document.title = `NetScope — ${title}`;

    // Render screen
    renderActivePage();
    window.scrollTo(0, 0);
  }

  function toggleSidebarCollapse() {
    state.sidebarCollapsed = !state.sidebarCollapsed;
    localStorage.setItem(STORAGE_SIDEBAR_KEY, String(state.sidebarCollapsed));
    $('#app-root').classList.toggle('collapsed', state.sidebarCollapsed);
    const btn = $('#sidebar-collapse-btn');
    if (btn) {
      btn.title = state.sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar';
      btn.setAttribute('aria-label', state.sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar');
    }
  }

  function openMobileMenu() {
    state.mobileMenuOpen = true;
    $('#app-sidebar').classList.add('mobile-open');
    $('#sidebar-backdrop').removeAttribute('hidden');
  }

  function closeMobileMenu() {
    state.mobileMenuOpen = false;
    $('#app-sidebar').classList.remove('mobile-open');
    $('#sidebar-backdrop').setAttribute('hidden', '');
  }

  function toggleTheme() {
    state.theme = state.theme === 'dark' ? 'light' : 'dark';
    localStorage.setItem(STORAGE_THEME_KEY, state.theme);
    applyTheme(state.theme);
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    const root = $('#app-root');
    if (root) {
      root.classList.toggle('dark', theme === 'dark');
      root.classList.toggle('light', theme === 'light');
    }
  }

  // ══════════════════════════════════════════════════════════════════════════
  //  Screen Renderers (14 Screens Matching Figma)
  // ══════════════════════════════════════════════════════════════════════════
  function renderActivePage() {
    const mainEl = $('#page-content');
    if (!mainEl) return;

    const route = state.activeRoute;
    const [title, desc] = PAGE_META[route] || PAGE_META.live;
    const prevRouteTitle = PAGE_META[state.previousRoute || 'overview']?.[0] || 'Overview';

    // Standard Figma Page Heading with Brand Breadcrumbs & Settings Back Button
    let headingHtml = `
      <div class="page-heading ${route === 'settings' ? 'settings-heading' : ''}">
        <div>
          <div class="breadcrumbs">
            ${route === 'settings' ? `
              <button id="btn-back-breadcrumb" class="breadcrumb-back-btn" type="button" aria-label="Go back">
                ${icon('arrow-left', 13)}
                <span>Back to ${escapeHtml(prevRouteTitle)}</span>
              </button>
              <span class="breadcrumb-sep">/</span>
            ` : ''}
            <span class="breadcrumb-brand">
              <img class="breadcrumb-icon dark-only" src="NetScope_Short_Icon_Dark_Mode.png" alt="NetScope" width="13" height="13" />
              <img class="breadcrumb-icon light-only" src="NetScope_Short_Icon_Light_Mode.png" alt="NetScope" width="13" height="13" />
              <span>NetScope</span>
            </span>
            ${icon('chevron', 12)}
            <span>${escapeHtml(title)}</span>
          </div>
          <div class="page-title-row">
            <h1 class="page-title">${escapeHtml(title)}</h1>
            ${route === 'settings' ? `
              <button id="btn-settings-back" class="btn btn-back-pill" type="button" title="Back to ${escapeHtml(prevRouteTitle)}">
                ${icon('arrow-left', 14)} Back to ${escapeHtml(prevRouteTitle)}
              </button>
            ` : ''}
          </div>
          <p class="page-description">${escapeHtml(desc)}</p>
        </div>
        <div class="page-actions">
          <span class="badge purple"><i></i> Sample data</span>
          ${route === 'live' || route === 'overview' ? `
            <button id="btn-head-pause" class="btn" type="button">
              ${icon(state.paused ? 'play' : 'pause', 15)} ${state.paused ? 'Resume view' : 'Pause view'}
            </button>
            <button id="btn-head-config" class="btn primary" type="button">
              ${icon('sliders', 15)} Capture settings
            </button>
          ` : ''}
        </div>
      </div>
    `;

    let bodyHtml = '';
    switch (route) {
      case 'overview':
        bodyHtml = renderOverviewPage();
        break;
      case 'live':
        bodyHtml = renderLiveTrafficPage();
        break;
      case 'packets':
        bodyHtml = renderPacketExplorerPage();
        break;
      case 'topology':
        bodyHtml = renderTopologyPage();
        break;
      case 'hosts':
        bodyHtml = renderHostsPage();
        break;
      case 'flows':
        bodyHtml = renderFlowsPage();
        break;
      case 'threats':
        bodyHtml = renderThreatsPage();
        break;
      case 'alerts':
        bodyHtml = renderAlertsPage();
        break;
      case 'encryption':
        bodyHtml = renderEncryptionPage();
        break;
      case 'protocols':
        bodyHtml = renderProtocolsPage();
        break;
      case 'reports':
        bodyHtml = renderReportsPage();
        break;
      case 'capture':
        bodyHtml = renderCaptureConfigPage();
        break;
      case 'settings':
        bodyHtml = renderSettingsPage();
        break;
      case 'docs':
        bodyHtml = renderDocsPage();
        break;
      default:
        bodyHtml = renderLiveTrafficPage();
    }

    mainEl.innerHTML = headingHtml + bodyHtml;
    attachPageListeners(route);
  }

  // ══════════════════════════════════════════════════════════════════════════
  //  1. SIGNATURE LIVE TRAFFIC WORKSPACE (Section 7)
  // ══════════════════════════════════════════════════════════════════════════
  function renderLiveTrafficPage() {
    const s = state.stats;
    const pps = Math.round(s.pps || 42);
    const totalPkts = (s.total_packets || 18432).toLocaleString();
    const throughput = `${s.throughput_mbps || 6.24}`;
    const activeHosts = s.top_hosts.length || 24;

    const filteredPackets = getFilteredPackets();
    const selectedPkt = state.packets.find(p => p.id === state.selectedPacketId) || state.packets[0];

    return `
      <!-- Status Strip -->
      <div class="capture-strip">
        <div>
          <span class="pulse-indicator"></span>
          <b>${state.isDemoMode ? 'Demo capture active' : 'Live hardware capture active'}</b>
          <span>Simulated traffic · ${pps} packets/sec</span>
        </div>
        <div>
          ${icon('clock', 14)} Updated just now
          <button id="strip-pause-btn" class="btn ghost" type="button">
            ${icon(state.paused ? 'play' : 'pause', 14)} ${state.paused ? 'Resume view' : 'Pause view'}
          </button>
        </div>
      </div>

      <!-- 4 Top KPI Cards -->
      <div class="metrics four">
        <div class="card metric">
          <div class="metric-label">Total packets</div>
          <div class="metric-value">${totalPkts}</div>
          <div class="metric-bottom">
            <span>Capture duration ${formatDuration(state.uptimeSeconds || 2538)}</span>
            <div class="spark">${renderSparkbars([24, 35, 29, 52, 46, 64, 76, 68])}</div>
          </div>
        </div>
        <div class="card metric">
          <div class="metric-label">Current packet rate</div>
          <div class="metric-value">${pps} <small>pps</small></div>
          <div class="metric-bottom">
            <span>Peak 96.2 pps</span>
            <div class="spark blue">${renderSparkbars([20, 36, 44, 34, 68, 55, 80, 72])}</div>
          </div>
        </div>
        <div class="card metric">
          <div class="metric-label">Network throughput</div>
          <div class="metric-value">${throughput} <small>Mbps</small></div>
          <div class="metric-bottom">
            <span>In 4.1 · Out 2.1 Mbps</span>
            <div class="spark">${renderSparkbars([30, 45, 60, 50, 70, 85, 90, 80])}</div>
          </div>
        </div>
        <div class="card metric">
          <div class="metric-label">Active hosts</div>
          <div class="metric-value">${activeHosts}</div>
          <div class="metric-bottom">
            <span>18 local · 6 external</span>
            <div class="spark">${renderSparkbars([15, 18, 20, 22, 24, 24, 24, 24])}</div>
          </div>
        </div>
      </div>

      <!-- Real-Time Throughput Chart -->
      <section class="card" style="margin-bottom: 12px;">
        <div class="card-head">
          <div class="card-title">Real-time throughput</div>
          <div class="actions">
            <button id="chart-pause-btn" class="btn" type="button">
              ${icon(state.paused ? 'play' : 'pause', 14)} ${state.paused ? 'Resume view' : 'Pause view'}
            </button>
            <button id="chart-reset-btn" class="btn ghost" type="button">Reset</button>
          </div>
        </div>
        <div class="legend">
          <span><i class="teal"></i> Incoming</span>
          <span><i class="blue"></i> Outgoing</span>
          ${state.paused ? `<span class="badge warn"><i></i> Visualization paused · capture continues</span>` : ''}
          <b>Current ${throughput} Mbps</b>
        </div>
        ${renderThroughputSvgChart()}
      </section>

      <!-- Signature Packet Stream & Inspector Workspace -->
      <section class="card" style="margin-bottom: 12px;">
        <div class="card-head">
          <div class="card-title">Live Packet Stream &amp; Inspector</div>
          <div class="actions">
            <span class="badge info"><i></i> ${filteredPackets.length} matching</span>
            <button id="stream-autoscroll-btn" class="btn ${state.autoScroll ? 'primary' : 'ghost'}" type="button" title="Lock stream to latest packets">
              ${icon('activity', 14)} Auto-scroll: ${state.autoScroll ? 'ON' : 'OFF'}
            </button>
          </div>
        </div>

        <div style="padding: 12px 14px 6px;">
          <!-- Stream Controls Toolbar -->
          <div class="toolbar">
            <label class="search" for="stream-search-input">
              ${icon('search', 16)}
              <input id="stream-search-input" type="text" placeholder="Filter by IP, port, protocol or info…" value="${escapeHtml(state.streamSearch)}" autocomplete="off" />
              <kbd>ESC</kbd>
            </label>
            
            <div class="segmented" id="proto-filter-group">
              ${['ALL', 'TCP', 'UDP', 'DNS', 'ICMP', 'ARP'].map(p => `
                <button class="${state.streamProtocol === p ? 'active' : ''}" data-proto="${p}" type="button">${p}</button>
              `).join('')}
            </div>

            <button id="btn-stream-clear" class="btn ghost" type="button" title="Clear current visible buffer">
              ${icon('x', 14)} Clear
            </button>
          </div>
        </div>

        <div class="packet-workspace ${!selectedPkt ? 'no-inspector' : ''}" style="padding: 0 14px 14px;">
          <!-- Dense Packet Table -->
          <div class="packet-list card" style="background: var(--surface-2); border-color: var(--border-soft);">
            <div class="table-scroll" id="packet-table-container">
              <table class="data-table packet-table">
                <thead>
                  <tr>
                    <th style="width: 55px;">No.</th>
                    <th style="width: 95px;">Time</th>
                    <th style="width: 65px;">Protocol</th>
                    <th>Source</th>
                    <th style="width: 65px;">Port</th>
                    <th>Destination</th>
                    <th style="width: 65px;">Port</th>
                    <th style="width: 60px;">Length</th>
                    <th style="width: 70px;">Flags</th>
                    <th>Information</th>
                  </tr>
                </thead>
                <tbody id="packet-stream-body">
                  ${renderPacketTableRows(filteredPackets, selectedPkt ? selectedPkt.id : null)}
                </tbody>
              </table>
            </div>
          </div>

          <!-- Packet Inspector Side Drawer -->
          ${selectedPkt ? renderPacketInspector(selectedPkt) : ''}
        </div>
      </section>

      <!-- Secondary Analytics: 3-column grid -->
      <div class="grid-3">
        <div class="card">
          <div class="card-head"><div class="card-title">Protocol distribution</div></div>
          ${renderProtocolBars()}
        </div>
        <div class="card">
          <div class="card-head"><div class="card-title">Top source addresses</div></div>
          ${renderHostMini()}
        </div>
        <div class="card">
          <div class="card-head"><div class="card-title">Packet size distribution</div></div>
          <div class="histogram">
            ${[35, 62, 85, 48, 30, 20, 14, 8].map((v, i) => `
              <i style="height: ${v}%;">
                <span>${i === 0 ? '64' : i === 3 ? '512' : i === 7 ? '1500' : ''}</span>
              </i>
            `).join('')}
          </div>
        </div>
      </div>
    `;
  }

  function getFilteredPackets() {
    const term = (state.streamSearch || '').toLowerCase().trim();
    const proto = state.streamProtocol;

    return state.packets.filter((p) => {
      if (proto !== 'ALL' && p.protocol !== proto) return false;
      if (!term) return true;
      const combined = `${p.src_ip} ${p.dst_ip} ${p.src_port || ''} ${p.dst_port || ''} ${p.protocol} ${p.info || ''} ${p.flags || ''}`.toLowerCase();
      return combined.includes(term);
    });
  }

  function renderPacketTableRows(packetsList, selectedId) {
    if (!packetsList || packetsList.length === 0) {
      return `<tr><td colspan="10" style="text-align: center; padding: 24px; color: var(--muted);">No packets match current filter criteria</td></tr>`;
    }

    return packetsList.map((pkt) => {
      const isSelected = pkt.id === selectedId;
      const protoClass = `p-${pkt.protocol.toLowerCase()}`;
      return `
        <tr class="packet-row ${isSelected ? 'selected' : ''}" data-packet-id="${pkt.id}">
          <td class="mono">${pkt.id}</td>
          <td class="mono">${escapeHtml(pkt.timestamp)}</td>
          <td class="protocol ${protoClass}">
            <span class="proto-chip ${pkt.protocol.toLowerCase()}">${escapeHtml(pkt.protocol)}</span>
          </td>
          <td class="mono" style="color: var(--text);">${escapeHtml(pkt.src_ip)}</td>
          <td class="mono">${pkt.src_port ?? '—'}</td>
          <td class="mono" style="color: var(--text);">${escapeHtml(pkt.dst_ip)}</td>
          <td class="mono">${pkt.dst_port ?? '—'}</td>
          <td class="mono">${(pkt.length || 0).toLocaleString()}</td>
          <td class="mono">${escapeHtml(pkt.flags || '—')}</td>
          <td style="color: var(--text-2); max-width: 280px; overflow: hidden; text-overflow: ellipsis;">
            ${escapeHtml(pkt.info || '')}
          </td>
        </tr>
      `;
    }).join('');
  }

  function renderPacketInspector(pkt) {
    if (!pkt) return '';
    const isEncrypted = pkt.enc;
    return `
      <aside class="inspector card" id="packet-inspector-panel">
        <div class="card-head">
          <div class="card-title">Packet ${pkt.id}</div>
          <button id="inspector-close-btn" class="btn ghost" type="button" aria-label="Close inspector">
            ${icon('x', 14)}
          </button>
        </div>

        <div class="inspector-summary">
          <span class="badge ${pkt.protocol === 'TCP' ? 'info' : 'good'}">${escapeHtml(pkt.protocol)}</span>
          <span><b>${(pkt.length || 0).toLocaleString()}</b> bytes</span>
          <span>${icon('clock', 12)} ${escapeHtml(pkt.timestamp)}</span>
          ${isEncrypted ? `<span class="badge purple">Encrypted</span>` : ''}
        </div>

        <div class="inspector-body">
          <details open>
            <summary><span class="arrow">⌄</span> Packet Summary</summary>
            <div class="detail-rows">
              <div>
                <span>Source</span>
                <code>${escapeHtml(pkt.src_ip)}${pkt.src_port ? `:${pkt.src_port}` : ''}
                  <button class="copy-btn" data-copy="${escapeHtml(pkt.src_ip)}" title="Copy IP">${icon('copy', 12)}</button>
                </code>
              </div>
              <div>
                <span>Destination</span>
                <code>${escapeHtml(pkt.dst_ip)}${pkt.dst_port ? `:${pkt.dst_port}` : ''}
                  <button class="copy-btn" data-copy="${escapeHtml(pkt.dst_ip)}" title="Copy IP">${icon('copy', 12)}</button>
                </code>
              </div>
              <div>
                <span>Protocol</span>
                <code>${escapeHtml(pkt.protocol)} ${pkt.service ? `/ ${escapeHtml(pkt.service)}` : ''}</code>
              </div>
              <div>
                <span>Frame length</span>
                <code>${(pkt.length || 0).toLocaleString()} bytes (${(pkt.length || 0) * 8} bits)</code>
              </div>
            </div>
          </details>

          <details open>
            <summary><span class="arrow">⌄</span> Network layer · IPv4</summary>
            <div class="detail-rows">
              <div><span>Source IP</span><code>${escapeHtml(pkt.src_ip)} (${pkt.src_class || 'Private'})</code></div>
              <div><span>Destination IP</span><code>${escapeHtml(pkt.dst_ip)} (${pkt.dst_class || 'Public'})</code></div>
              <div><span>TTL</span><code>${pkt.ttl ?? 64}</code></div>
              <div><span>Header length</span><code>20 bytes</code></div>
            </div>
          </details>

          <details open>
            <summary><span class="arrow">⌄</span> Transport layer · ${escapeHtml(pkt.protocol)}</summary>
            <div class="detail-rows">
              <div><span>Source port</span><code>${pkt.src_port ?? '—'}</code></div>
              <div><span>Destination port</span><code>${pkt.dst_port ? `${pkt.dst_port} (${pkt.service || 'Unknown'})` : '—'}</code></div>
              <div><span>Flags</span><code>${escapeHtml(pkt.flags || 'None')}</code></div>
              <div><span>Payload details</span><code>${escapeHtml(pkt.info || 'Standard traffic')}</code></div>
            </div>
          </details>

          <details open>
            <summary><span class="arrow">⌄</span> Security &amp; Cryptography</summary>
            <div class="detail-rows">
              <div><span>Encryption status</span><code>${isEncrypted ? 'Encrypted payload signature' : 'Cleartext payload'}</code></div>
              <div><span>Detection method</span><code>${pkt.enc_methods ? escapeHtml(pkt.enc_methods.join(', ')) : (isEncrypted ? 'TLS record header' : 'None')}</code></div>
              <div><span>Source host score</span><code>${pkt.src_ip === '10.0.0.42' ? 'Malicious · 82' : pkt.src_ip === '45.33.32.156' ? 'Suspicious · 64' : 'Clean · 4'}</code></div>
            </div>
          </details>
        </div>
      </aside>
    `;
  }

  function updateLivePacketStreamIncremental(newPkt) {
    const tableBody = $('#packet-stream-body');
    if (!tableBody) return;

    const filtered = getFilteredPackets();
    tableBody.innerHTML = renderPacketTableRows(filtered, state.selectedPacketId);

    // Auto-scroll logic: scroll to top of table if autoScroll is enabled
    if (state.autoScroll) {
      const container = $('#packet-table-container');
      if (container) container.scrollTop = 0;
    }
  }

  // ══════════════════════════════════════════════════════════════════════════
  //  2. OVERVIEW / DASHBOARD SCREEN
  // ══════════════════════════════════════════════════════════════════════════
  function renderOverviewPage() {
    const s = state.stats;
    const totalPkts = (s.total_packets || 18432).toLocaleString();
    const pps = s.pps || 42.8;
    const throughput = `${s.throughput_mbps || 6.24}`;
    const encPct = `${s.crypto?.encrypted_pct || 78.4}`;

    return `
      <div class="capture-strip">
        <div>
          <span class="pulse-indicator"></span>
          <b>Demo capture active</b>
          <span>Simulated traffic · ${Math.round(pps)} packets/sec</span>
        </div>
        <div>
          ${icon('clock', 14)} Updated just now
          <button class="btn ghost" type="button">${icon('pause', 14)} Pause view</button>
        </div>
      </div>

      <div class="metrics six">
        <div class="card metric">
          <div class="metric-label">Total packets</div>
          <div class="metric-value">${totalPkts}</div>
          <div class="metric-bottom">
            <span>+12.4% this session</span>
            <div class="spark">${renderSparkbars([24, 35, 29, 52, 46, 64, 76, 68])}</div>
          </div>
        </div>
        <div class="card metric">
          <div class="metric-label">Packets per second</div>
          <div class="metric-value">${pps}</div>
          <div class="metric-bottom">
            <span>Peak 96.2 pps</span>
            <div class="spark blue">${renderSparkbars([20, 36, 44, 34, 68, 55, 80, 72])}</div>
          </div>
        </div>
        <div class="card metric">
          <div class="metric-label">Network throughput</div>
          <div class="metric-value">${throughput} <small>Mbps</small></div>
          <div class="metric-bottom"><span>↑ 1.8 Mbps</span></div>
        </div>
        <div class="card metric">
          <div class="metric-label">Active hosts</div>
          <div class="metric-value">24</div>
          <div class="metric-bottom"><span>6 external hosts</span></div>
        </div>
        <div class="card metric">
          <div class="metric-label">Security alerts</div>
          <div class="metric-value" style="color: var(--warn);">${state.alerts.length || 12}</div>
          <div class="metric-bottom">
            <span>3 high severity</span>
            <div class="spark orange">${renderSparkbars([12, 28, 20, 46, 22, 68, 48, 36])}</div>
          </div>
        </div>
        <div class="card metric">
          <div class="metric-label">Encrypted traffic</div>
          <div class="metric-value">${encPct} <small>%</small></div>
          <div class="metric-bottom"><span>14,450 packets</span></div>
        </div>
      </div>

      <div class="dashboard-grid">
        <section class="card traffic-card">
          <div class="card-head">
            <div class="card-title">Network traffic overview</div>
            <div class="segmented" id="traffic-timeframe-controls">
              <button class="${(state.trafficTimeframe || '1H') === '1H' ? 'active' : ''}" data-timeframe="1H" type="button">1H</button>
              <button class="${state.trafficTimeframe === '6H' ? 'active' : ''}" data-timeframe="6H" type="button">6H</button>
              <button class="${state.trafficTimeframe === '24H' ? 'active' : ''}" data-timeframe="24H" type="button">24H</button>
            </div>
          </div>
          <div class="legend" id="traffic-legend">
            <span><i class="teal"></i> Incoming</span>
            <span><i class="blue"></i> Outgoing</span>
            <b id="traffic-legend-rate">Current ${(TRAFFIC_TIMEFRAME_DATA[state.trafficTimeframe || '1H'] || TRAFFIC_TIMEFRAME_DATA['1H']).throughput} Mbps</b>
            <span class="mono" id="traffic-legend-vol" style="margin-left: 8px; font-size: 10px; color: var(--muted);">${(TRAFFIC_TIMEFRAME_DATA[state.trafficTimeframe || '1H'] || TRAFFIC_TIMEFRAME_DATA['1H']).totalVolume} total (${state.trafficTimeframe || '1H'})</span>
          </div>
          <div id="traffic-chart-container">
            ${renderThroughputSvgChart(false, state.trafficTimeframe || '1H')}
          </div>
        </section>

        <section class="card">
          <div class="card-head">
            <div class="card-title">Protocol distribution</div>
            <button class="btn ghost" type="button">${icon('more', 16)}</button>
          </div>
          ${renderProtocolBars()}
        </section>

        <section class="card topology-card">
          <div class="card-head">
            <div class="card-title">Network topology</div>
            <button class="btn ghost" type="button" onclick="window.location.hash='#topology'">
              Open explorer ${icon('chevron', 12)}
            </button>
          </div>
          ${renderTopologyMiniGraph()}
        </section>

        <section class="card">
          <div class="card-head"><div class="card-title">Threat posture</div></div>
          <div class="posture">
            <div class="risk-ring">
              <b>24</b><span>hosts</span>
            </div>
            <div class="posture-list">
              <span><i class="clean"></i> Clean <b>19</b></span>
              <span><i class="suspicious"></i> Suspicious <b>4</b></span>
              <span><i class="malicious"></i> Malicious <b>1</b></span>
            </div>
          </div>
          <p class="callout warn">
            ${icon('alert', 16)}
            <span>10.0.0.42 has exceeded the malicious threshold with a score of 82.</span>
          </p>
        </section>

        <section class="card wide-card">
          <div class="card-head">
            <div class="card-title">Recent security alerts</div>
            <button class="btn ghost" type="button" onclick="window.location.hash='#alerts'">
              View all ${icon('chevron', 12)}
            </button>
          </div>
          ${renderAlertsTableHtml(state.alerts.slice(0, 4))}
        </section>

        <section class="card">
          <div class="card-head"><div class="card-title">Top communicating hosts</div></div>
          ${renderHostMini()}
        </section>

        <section class="card full-card">
          <div class="card-head">
            <div class="card-title">Recent packet activity</div>
            <button class="btn ghost" type="button" onclick="window.location.hash='#packets'">
              Open Packet Explorer ${icon('chevron', 12)}
            </button>
          </div>
          <div class="table-scroll">
            <table class="data-table">
              <thead>
                <tr>
                  <th>No.</th><th>Time</th><th>Protocol</th><th>Source</th><th>Src Port</th>
                  <th>Destination</th><th>Dst Port</th><th>Length</th><th>Flags</th><th>Information</th>
                </tr>
              </thead>
              <tbody>
                ${renderPacketTableRows(state.packets.slice(0, 6), null)}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    `;
  }

  function updateOverviewIncremental() {
    // Light weight update of packet counts and throughput
    const statCards = $$('.metric-value');
    if (statCards[0]) statCards[0].textContent = (state.stats.total_packets || 18432).toLocaleString();
    if (statCards[1]) statCards[1].textContent = `${Math.round(state.stats.pps || 42)}`;
  }

  // ══════════════════════════════════════════════════════════════════════════
  //  3. PACKET EXPLORER SCREEN
  // ══════════════════════════════════════════════════════════════════════════
  function renderPacketExplorerPage() {
    const selectedPkt = state.packets.find(p => p.id === state.selectedPacketId) || state.packets[0];
    const filtered = getFilteredPackets();

    return `
      <div class="toolbar">
        <label class="search" for="explorer-query">
          ${icon('search', 16)}
          <input id="explorer-query" placeholder="Filter packets (e.g. ip:192.168.1.10 proto:tcp)" value="${escapeHtml(state.streamSearch)}" autocomplete="off" />
          <kbd>⌘ K</kbd>
        </label>
        <button class="select-btn" type="button">All protocols <span>⌄</span></button>
        <button class="select-btn" type="button">Source IP <span>⌄</span></button>
        <button class="select-btn" type="button">Destination IP <span>⌄</span></button>
        <button class="btn" type="button">${icon('filter', 14)} Filters</button>
      </div>

      <div class="filter-help">
        <span>${(state.stats.total_packets || 18432).toLocaleString()} packets</span>
        <span>Syntax:</span>
        <code>ip:192.168.1.10</code>
        <code>proto:tcp</code>
        <code>port:443</code>
        <code>enc:true</code>
        <button id="explorer-clear-btn" class="btn ghost" type="button">${icon('x', 14)} Clear filters</button>
      </div>

      <div class="packet-workspace">
        <div class="card packet-list">
          <div class="table-scroll">
            <table class="data-table packet-table">
              <thead>
                <tr>
                  <th>No.</th><th>Time</th><th>Protocol</th><th>Source</th><th>Src Port</th>
                  <th>Destination</th><th>Dst Port</th><th>Length</th><th>Flags</th><th>Information</th>
                </tr>
              </thead>
              <tbody id="explorer-packet-body">
                ${renderPacketTableRows(filtered, selectedPkt ? selectedPkt.id : null)}
              </tbody>
            </table>
          </div>
        </div>

        ${selectedPkt ? renderPacketInspector(selectedPkt) : ''}
      </div>
    `;
  }

  // ══════════════════════════════════════════════════════════════════════════
  //  4. NETWORK TOPOLOGY SCREEN
  // ══════════════════════════════════════════════════════════════════════════
  function renderTopologyPage() {
    return `
      <div class="topology-workspace">
        <div class="card graph-card">
          <div class="card-head">
            <div class="card-title">Communication graph</div>
            <div class="actions">
              <label class="search small">
                ${icon('search', 14)}
                <input placeholder="Find host…" autocomplete="off" />
              </label>
              <button class="btn ghost" type="button">Last 15 min</button>
            </div>
          </div>

          <div class="topology large">
            <svg viewBox="0 0 100 100" preserveAspectRatio="none">
              <defs>
                <filter id="lg-glow-teal" x="-50%" y="-50%" width="200%" height="200%">
                  <feGaussianBlur in="SourceGraphic" stdDeviation="1.5" result="blur" />
                  <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
                </filter>
                <filter id="lg-glow-blue" x="-50%" y="-50%" width="200%" height="200%">
                  <feGaussianBlur in="SourceGraphic" stdDeviation="1.5" result="blur" />
                  <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
                </filter>
                <filter id="lg-glow-danger" x="-50%" y="-50%" width="200%" height="200%">
                  <feGaussianBlur in="SourceGraphic" stdDeviation="2" result="blur" />
                  <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
                </filter>
              </defs>

              <line x1="50" y1="50" x2="22" y2="26" class="topo-link active-link" />
              <line x1="50" y1="50" x2="22" y2="74" class="topo-link risk" />
              <line x1="50" y1="50" x2="76" y2="22" class="topo-link active-link" />
              <line x1="50" y1="50" x2="82" y2="54" class="topo-link active-link" />
              <line x1="50" y1="50" x2="72" y2="82" class="topo-link active-link" />
              <line x1="22" y1="74" x2="82" y2="54" class="topo-link risk" />

              <!-- Animated Traveling Packets -->
              <circle r="1.8" fill="#5795e8" filter="url(#lg-glow-blue)">
                <animateMotion path="M22,26 L50,50 L76,22" dur="3s" repeatCount="indefinite" />
              </circle>
              <circle r="1.8" fill="#19b89a" filter="url(#lg-glow-teal)">
                <animateMotion path="M76,22 L50,50 L22,26" dur="2.6s" begin="0.8s" repeatCount="indefinite" />
              </circle>
              <circle r="2.2" fill="#e05260" filter="url(#lg-glow-danger)">
                <animateMotion path="M22,74 L50,50" dur="1.5s" repeatCount="indefinite" />
              </circle>
              <circle r="2.0" fill="#e05260" filter="url(#lg-glow-danger)">
                <animateMotion path="M22,74 L82,54" dur="2.0s" begin="0.6s" repeatCount="indefinite" />
              </circle>
              <circle r="1.8" fill="#19b89a" filter="url(#lg-glow-teal)">
                <animateMotion path="M50,50 L72,82" dur="3.2s" begin="0.4s" repeatCount="indefinite" />
              </circle>
            </svg>

            <!-- Nodes -->
            <div class="node gateway good" style="left: 50%; top: 50%;">
              <span>${icon('network', 20)}</span>
              <label>192.168.1.1 (Gateway)</label>
            </div>
            <div class="node host warn" style="left: 22%; top: 26%;">
              <span>${icon('server', 20)}</span>
              <label>192.168.1.24</label>
            </div>
            <div class="node host danger" style="left: 22%; top: 74%;">
              <span>${icon('server', 20)}</span>
              <label>10.0.0.42</label>
            </div>
            <div class="node external good" style="left: 76%; top: 22%;">
              <span>${icon('server', 20)}</span>
              <label>172.217.14.206</label>
            </div>
            <div class="node external warn" style="left: 82%; top: 54%;">
              <span>${icon('server', 20)}</span>
              <label>185.199.108.133</label>
            </div>
            <div class="node host good" style="left: 72%; top: 82%;">
              <span>${icon('server', 20)}</span>
              <label>192.168.1.31</label>
            </div>

            <div class="graph-tools">
              <button class="btn ghost" type="button">${icon('search', 16)}</button>
              <button class="btn ghost" type="button">${icon('sliders', 16)}</button>
              <button class="btn ghost" type="button">Reset</button>
            </div>

            <div class="graph-legend">
              <span><i class="clean"></i> Clean</span>
              <span><i class="suspicious"></i> Suspicious</span>
              <span><i class="malicious"></i> Malicious</span>
              <span>Line width = traffic volume</span>
            </div>
          </div>
        </div>

        <!-- Selected Host Panel -->
        <div class="card host-panel">
          <div class="card-head"><div class="card-title">Selected host</div></div>
          <div class="host-avatar danger">${icon('server', 24)}</div>
          <h2>10.0.0.42</h2>
          <p>Private IPv4 address</p>

          <div class="big-score">
            <span>Threat score</span>
            <b>82</b>
            <div><i style="width: 82%;"></i></div>
            <span class="badge danger">Malicious</span>
          </div>

          <div style="text-align: left; padding: 0 14px;">
            <details open class="inspector">
              <summary><span class="arrow">⌄</span> Activity</summary>
              <div class="detail-rows">
                <div><span>Packets</span><code>2,741</code></div>
                <div><span>Traffic</span><code>58.4 MB</code></div>
                <div><span>First seen</span><code>13:49:52</code></div>
                <div><span>Last seen</span><code>12 sec ago</code></div>
              </div>
            </details>
            <details open class="inspector">
              <summary><span class="arrow">⌄</span> Relationships</summary>
              <div class="detail-rows">
                <div><span>Communicates with</span><code>6 hosts</code></div>
                <div><span>External hosts</span><code>2</code></div>
                <div><span>Top destination</span><code>185.199.108.133</code></div>
              </div>
            </details>
          </div>

          <p class="callout warn" style="margin-top: 14px;">
            ${icon('alert', 16)}
            <span>Classification is based on heuristic detections and does not confirm compromise.</span>
          </p>
        </div>
      </div>
    `;
  }

  // ══════════════════════════════════════════════════════════════════════════
  //  5. HOST INVENTORY SCREEN
  // ══════════════════════════════════════════════════════════════════════════
  function renderHostsPage() {
    const hosts = state.stats.top_hosts || [];
    return `
      <div class="metrics four">
        <div class="card metric">
          <div class="metric-label">Total hosts</div>
          <div class="metric-value">24</div>
          <div class="metric-bottom"><span>6 external</span></div>
        </div>
        <div class="card metric">
          <div class="metric-label">Clean</div>
          <div class="metric-value">19</div>
          <div class="metric-bottom"><span>Score below 25</span></div>
        </div>
        <div class="card metric">
          <div class="metric-label">Suspicious</div>
          <div class="metric-value" style="color: var(--warn);">4</div>
          <div class="metric-bottom"><span>Score 25–69</span></div>
        </div>
        <div class="card metric">
          <div class="metric-label">Malicious</div>
          <div class="metric-value" style="color: var(--danger);">1</div>
          <div class="metric-bottom"><span>Score 70+</span></div>
        </div>
      </div>

      <div class="toolbar">
        <label class="search">
          ${icon('search', 16)}
          <input placeholder="Search IP address…" autocomplete="off" />
        </label>
        <button class="select-btn" type="button">All classifications <span>⌄</span></button>
        <button class="select-btn" type="button">All address types <span>⌄</span></button>
        <button class="select-btn" type="button">Last observed <span>⌄</span></button>
      </div>

      <div class="card">
        <div class="table-scroll">
          <table class="data-table">
            <thead>
              <tr>
                <th>IP address</th>
                <th>Address type</th>
                <th>Classification</th>
                <th>Packets</th>
                <th>Traffic volume</th>
                <th>Threat score</th>
                <th>Last observed</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              ${hosts.map(h => `
                <tr>
                  <td class="mono" style="color: var(--text); font-weight: 500;">${h.ip}</td>
                  <td>${h.class}</td>
                  <td>
                    <span class="badge ${h.status === 'Malicious' ? 'danger' : h.status === 'Suspicious' ? 'warn' : 'good'}">
                      ${h.status}
                    </span>
                  </td>
                  <td class="mono">${(h.packets || 0).toLocaleString()}</td>
                  <td class="mono">${h.bytes}</td>
                  <td>
                    <span class="score ${h.score >= 70 ? 'danger' : h.score >= 25 ? 'warn' : 'good'}">${h.score}</span>
                  </td>
                  <td>${h.lastSeen}</td>
                  <td><span class="online-dot" style="margin-right: 5px;"></span> Active</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
        <div class="pagination">
          <span>Showing 1–6 of 24 hosts</span>
          <div>
            <button class="btn" disabled type="button">Previous</button>
            <button class="btn" type="button">Next</button>
          </div>
        </div>
      </div>
    `;
  }

  // ══════════════════════════════════════════════════════════════════════════
  //  6. SESSIONS & FLOWS SCREEN
  // ══════════════════════════════════════════════════════════════════════════
  function renderFlowsPage() {
    const flows = state.stats.flows || [];
    return `
      <div class="metrics four">
        <div class="card metric">
          <div class="metric-label">Active connections</div>
          <div class="metric-value">18</div>
          <div class="metric-bottom"><span>Estimated established</span></div>
        </div>
        <div class="card metric">
          <div class="metric-label">Total connections</div>
          <div class="metric-value">286</div>
          <div class="metric-bottom"><span>Current session</span></div>
        </div>
        <div class="card metric">
          <div class="metric-label">TCP retransmissions</div>
          <div class="metric-value">42</div>
          <div class="metric-bottom"><span>0.36% of TCP</span></div>
        </div>
        <div class="card metric">
          <div class="metric-label">Top flows</div>
          <div class="metric-value">10</div>
          <div class="metric-bottom"><span>72% of total traffic</span></div>
        </div>
      </div>

      <div class="toolbar">
        <label class="search">
          ${icon('search', 16)}
          <input placeholder="Search source or destination IP…" autocomplete="off" />
        </label>
        <button class="select-btn" type="button">All protocols <span>⌄</span></button>
        <button class="select-btn" type="button">Connection state <span>⌄</span></button>
        <button class="select-btn" type="button">Last 15 min <span>⌄</span></button>
      </div>

      <div class="card">
        <div class="table-scroll">
          <table class="data-table">
            <thead>
              <tr>
                <th>Source IP</th>
                <th>Destination IP</th>
                <th>Protocol</th>
                <th>Src Port</th>
                <th>Dst Port</th>
                <th>Packets</th>
                <th>Bytes</th>
                <th>Connection</th>
              </tr>
            </thead>
            <tbody>
              ${flows.map(f => `
                <tr>
                  <td class="mono" style="color: var(--text);">${f.src}</td>
                  <td class="mono" style="color: var(--text);">${f.dst}</td>
                  <td><span class="badge info">${f.proto}</span></td>
                  <td class="mono">${f.sport}</td>
                  <td class="mono">${f.dport}</td>
                  <td class="mono">${f.pkts}</td>
                  <td class="mono">${f.bytes}</td>
                  <td><span class="badge ${f.state === 'Established' ? 'good' : 'warn'}">${f.state}</span></td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;
  }

  // ══════════════════════════════════════════════════════════════════════════
  //  7. THREAT INTELLIGENCE SCREEN
  // ══════════════════════════════════════════════════════════════════════════
  function renderThreatsPage() {
    const hosts = (state.stats.top_hosts || []).slice().sort((a, b) => b.score - a.score);
    return `
      <div class="metrics four">
        <div class="card metric">
          <div class="metric-label">Hosts tracked</div>
          <div class="metric-value">24</div>
          <div class="metric-bottom"><span>Current session</span></div>
        </div>
        <div class="card metric">
          <div class="metric-label">Suspicious hosts</div>
          <div class="metric-value" style="color: var(--warn);">4</div>
          <div class="metric-bottom"><span>16.7% of hosts</span></div>
        </div>
        <div class="card metric">
          <div class="metric-label">Malicious hosts</div>
          <div class="metric-value" style="color: var(--danger);">1</div>
          <div class="metric-bottom"><span>Heuristic classification</span></div>
        </div>
        <div class="card metric">
          <div class="metric-label">Highest risk host</div>
          <div class="metric-value" style="color: var(--danger);">82</div>
          <div class="metric-bottom"><span>10.0.0.42</span></div>
        </div>
      </div>

      <div class="two-column">
        <div class="card main">
          <div class="card-head"><div class="card-title">Host threat leaderboard</div></div>
          <div class="leaderboard">
            ${hosts.map((h, i) => `
              <div>
                <span class="rank">${String(i + 1).padStart(2, '0')}</span>
                <span>
                  <b>${h.ip}</b>
                  <small>${h.class} · ${h.status} classification</small>
                </span>
                <div class="riskbar">
                  <i style="width: ${h.score}%;"></i>
                </div>
                <strong>${h.score}</strong>
              </div>
            `).join('')}
          </div>
        </div>

        <div class="card">
          <div class="card-head"><div class="card-title">Risk classification thresholds</div></div>
          <div class="threshold-list">
            <div>
              <span class="badge good">Clean</span>
              <b>0–24</b>
              <p>No significant suspicious behavior or heuristic anomalies observed.</p>
            </div>
            <div>
              <span class="badge warn">Suspicious</span>
              <b>25–69</b>
              <p>One or more heuristic indicators require operational review.</p>
            </div>
            <div>
              <span class="badge danger">Malicious</span>
              <b>70–100</b>
              <p>Multiple high-weighted anomalies observed (e.g. port scan + SYN flood).</p>
            </div>
          </div>
          <p class="callout info">
            ${icon('shield', 16)}
            <span>Scores decay automatically over time. A high score prioritizes investigation; it does not prove compromise.</span>
          </p>
        </div>
      </div>
    `;
  }

  // ══════════════════════════════════════════════════════════════════════════
  //  8. SECURITY ALERTS SCREEN
  // ══════════════════════════════════════════════════════════════════════════
  function renderAlertsPage() {
    return `
      <div class="metrics four">
        <div class="card metric">
          <div class="metric-label">Total alerts</div>
          <div class="metric-value">${state.alerts.length || 12}</div>
          <div class="metric-bottom"><span>Current session</span></div>
        </div>
        <div class="card metric">
          <div class="metric-label">High severity</div>
          <div class="metric-value" style="color: var(--danger);">3</div>
          <div class="metric-bottom"><span>Requires review</span></div>
        </div>
        <div class="card metric">
          <div class="metric-label">Suspicious</div>
          <div class="metric-value" style="color: var(--warn);">7</div>
          <div class="metric-bottom"><span>Heuristic findings</span></div>
        </div>
        <div class="card metric">
          <div class="metric-label">Informational</div>
          <div class="metric-value" style="color: var(--blue);">2</div>
          <div class="metric-bottom"><span>Context only</span></div>
        </div>
      </div>

      <div class="toolbar">
        <label class="search">
          ${icon('search', 16)}
          <input placeholder="Search alerts by IP or signature…" autocomplete="off" />
        </label>
        <button class="select-btn" type="button">All severities <span>⌄</span></button>
        <button class="select-btn" type="button">All detection types <span>⌄</span></button>
        <button class="select-btn" type="button">Any time <span>⌄</span></button>
      </div>

      <div class="card">
        <div class="card-head">
          <div class="card-title">Detections (${state.alerts.length})</div>
          <button id="btn-export-alerts-json" class="btn" type="button">
            ${icon('download', 14)} Export JSON
          </button>
        </div>
        ${renderAlertsTableHtml(state.alerts)}
      </div>

      <div class="page-note">
        ${icon('alert', 16)}
        <span>NetScope detections identify traffic patterns that may be suspicious. They should be validated before being treated as confirmed attacks.</span>
      </div>
    `;
  }

  function renderAlertsTableHtml(alertList) {
    if (!alertList || alertList.length === 0) {
      return `<p style="padding: 24px; text-align: center; color: var(--muted);">No security alerts recorded.</p>`;
    }

    return `
      <div class="table-scroll">
        <table class="data-table">
          <thead>
            <tr>
              <th>Severity</th>
              <th>Detection type</th>
              <th>Source IP</th>
              <th>Destination</th>
              <th>Description</th>
              <th>Time</th>
            </tr>
          </thead>
          <tbody>
            ${alertList.map(a => {
              const tone = a.severity === 'High' ? 'danger' : a.severity === 'Suspicious' ? 'warn' : 'info';
              return `
                <tr>
                  <td><span class="badge ${tone}">${escapeHtml(a.severity)}</span></td>
                  <td style="font-weight: 600; color: var(--text);">${escapeHtml(a.type)}</td>
                  <td class="mono">${escapeHtml(a.src)}</td>
                  <td class="mono">${escapeHtml(a.dst)}</td>
                  <td>${escapeHtml(a.detail || a.description || '')}</td>
                  <td class="mono">${escapeHtml(a.timestamp)}</td>
                </tr>
              `;
            }).join('')}
          </tbody>
        </table>
      </div>
    `;
  }

  // ══════════════════════════════════════════════════════════════════════════
  //  9. ENCRYPTION ANALYSIS SCREEN
  // ══════════════════════════════════════════════════════════════════════════
  function renderEncryptionPage() {
    const c = state.stats.crypto || {};
    return `
      <div class="metrics five">
        <div class="card metric">
          <div class="metric-label">Encrypted payloads</div>
          <div class="metric-value">${(c.encrypted || 14450).toLocaleString()}</div>
          <div class="metric-bottom"><span>Detected or inferred</span></div>
        </div>
        <div class="card metric">
          <div class="metric-label">Traffic percentage</div>
          <div class="metric-value">${c.encrypted_pct || 78.4} <small>%</small></div>
          <div class="metric-bottom"><span>+4.2% this session</span></div>
        </div>
        <div class="card metric">
          <div class="metric-label">Average entropy</div>
          <div class="metric-value">${c.avg_entropy || 7.14}</div>
          <div class="metric-bottom"><span>bits per byte</span></div>
        </div>
        <div class="card metric">
          <div class="metric-label">Recent entropy</div>
          <div class="metric-value">${c.recent_entropy || 7.62}</div>
          <div class="metric-bottom"><span>Latest payload</span></div>
        </div>
        <div class="card metric">
          <div class="metric-label">High entropy</div>
          <div class="metric-value">${(c.high_entropy || 9842).toLocaleString()}</div>
          <div class="metric-bottom"><span>Above 7.2 threshold</span></div>
        </div>
      </div>

      <div class="two-column entropy-layout">
        <div class="card main">
          <div class="card-head"><div class="card-title">Payload entropy over time</div></div>
          ${renderThroughputSvgChart(true)}
          <p class="callout info">
            ${icon('lock', 16)}
            <span>High entropy can indicate encrypted or compressed data. It is not conclusive proof of encryption.</span>
          </p>
        </div>

        <div class="card">
          <div class="card-head"><div class="card-title">Detection methods</div></div>
          <div class="method-list">
            ${(c.methods || [
              ['TLS / SSL signatures', '8,942'],
              ['Shannon entropy', '4,182'],
              ['SSH banners', '486'],
              ['Port-based inference', '428'],
              ['Base64 heuristic', '312'],
              ['AES-GCM heuristic', '100']
            ]).map(m => `
              <div><span>${m[0]}</span><b>${m[1]}</b></div>
            `).join('')}
          </div>
        </div>
      </div>

      <div class="card" style="margin-top: 12px;">
        <div class="card-head"><div class="card-title">Recent encryption findings</div></div>
        <div class="table-scroll">
          <table class="data-table">
            <thead>
              <tr>
                <th>Time</th><th>Source</th><th>Destination</th><th>Dst Port</th><th>Detection method</th><th>Packet size</th>
              </tr>
            </thead>
            <tbody>
              ${state.packets.slice(0, 5).map((p, i) => `
                <tr>
                  <td class="mono">${p.timestamp}</td>
                  <td class="mono">${p.src_ip}</td>
                  <td class="mono">${p.dst_ip}</td>
                  <td class="mono">${p.dst_port || '443'}</td>
                  <td>${i === 3 ? 'High entropy' : 'TLS signature'}</td>
                  <td class="mono">${p.length} bytes</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;
  }

  // ══════════════════════════════════════════════════════════════════════════
  //  10. PROTOCOL ANALYTICS SCREEN
  // ══════════════════════════════════════════════════════════════════════════
  let activeProtoTab = 'Overview';
  function renderProtocolsPage() {
    const tabs = ['Overview', 'TCP', 'UDP', 'ICMP', 'ARP', 'DNS', 'DHCP', 'HTTP', 'HTTPS', 'SSH', 'FTP'];
    return `
      <div class="tabs">
        ${tabs.map(t => `
          <button class="${t === activeProtoTab ? 'active' : ''}" data-tab="${t}" type="button">${t}</button>
        `).join('')}
      </div>

      <div class="metrics four">
        <div class="card metric">
          <div class="metric-label">${activeProtoTab === 'Overview' ? 'TCP' : activeProtoTab} packets</div>
          <div class="metric-value">${activeProtoTab === 'Overview' ? '11,428' : '2,842'}</div>
          <div class="metric-bottom"><span>62.0% of all packets</span></div>
        </div>
        <div class="card metric">
          <div class="metric-label">Traffic volume</div>
          <div class="metric-value">194.2 <small>MB</small></div>
          <div class="metric-bottom"><span>68.4% of traffic</span></div>
        </div>
        <div class="card metric">
          <div class="metric-label">Top service</div>
          <div class="metric-value">HTTPS</div>
          <div class="metric-bottom"><span>Port 443</span></div>
        </div>
        <div class="card metric">
          <div class="metric-label">Unique endpoints</div>
          <div class="metric-value">18</div>
          <div class="metric-bottom"><span>4 external</span></div>
        </div>
      </div>

      <div class="grid-2">
        <div class="card">
          <div class="card-head"><div class="card-title">Protocol traffic trend</div></div>
          ${renderThroughputSvgChart()}
        </div>
        <div class="card">
          <div class="card-head"><div class="card-title">Protocol distribution</div></div>
          ${renderProtocolBars()}
        </div>
      </div>

      <div class="grid-2">
        <div class="card">
          <div class="card-head"><div class="card-title">Top services</div></div>
          <div class="method-list">
            ${[
              ['HTTPS · 443', '8,942'],
              ['DNS · 53', '1,284'],
              ['SSH · 22', '486'],
              ['HTTP · 80', '412'],
              ['mDNS · 5353', '312']
            ].map(s => `<div><span>${s[0]}</span><b>${s[1]} packets</b></div>`).join('')}
          </div>
        </div>

        <div class="card">
          <div class="card-head"><div class="card-title">Top destination ports</div></div>
          <div class="horizontal-bars">
            ${[
              ['443', 85],
              ['53', 48],
              ['22', 29],
              ['80', 24],
              ['5353', 18]
            ].map(b => `
              <div>
                <code>${b[0]}</code>
                <span><i style="width: ${b[1]}%;"></i></span>
                <b>${b[1]}%</b>
              </div>
            `).join('')}
          </div>
        </div>
      </div>
    `;
  }

  // ══════════════════════════════════════════════════════════════════════════
  //  11. REPORTS SCREEN
  // ══════════════════════════════════════════════════════════════════════════
  function renderReportsPage() {
    return `
      <div class="report-hero">
        <div>
          <span class="report-icon">${icon('report', 24)}</span>
          <div>
            <h2>Current session report</h2>
            <p>Analysis summary for capture started today at 13:49 (Duration ${formatDuration(state.uptimeSeconds || 2538)}).</p>
          </div>
        </div>
        <div class="actions">
          <button id="btn-export-session-json" class="btn" type="button">
            ${icon('download', 14)} Export JSON
          </button>
          <button id="btn-export-session-html" class="btn primary" type="button">
            ${icon('download', 14)} Export HTML
          </button>
        </div>
      </div>

      <div class="report-grid">
        ${[
          ['Session summary', '42m 18s', '18,432 packets analyzed', 'clock'],
          ['Traffic statistics', '312.8 MB', '6.24 Mbps current', 'activity'],
          ['Protocol breakdown', '10 protocols', 'TCP is 62% of traffic', 'chart'],
          ['Security findings', '12 alerts', '3 high severity', 'shield'],
          ['Encryption findings', '78.4%', '14,450 encrypted payloads', 'lock'],
          ['Top communicating hosts', '24 hosts', '192.168.1.24 is most active', 'server']
        ].map(r => `
          <div class="card report-card">
            <span>${icon(r[3], 20)}</span>
            <div>
              <h3>${r[0]}</h3>
              <b>${r[1]}</b>
              <p>${r[2]}</p>
            </div>
            ${icon('chevron', 14)}
          </div>
        `).join('')}
      </div>

      <div class="page-note">
        ${icon('clock', 16)}
        <span>Reports summarize the active analysis session in real-time. NetScope does not store historical telemetry in cloud storage without authorization.</span>
      </div>
    `;
  }

  // ══════════════════════════════════════════════════════════════════════════
  //  12. CAPTURE CONFIGURATION SCREEN
  // ══════════════════════════════════════════════════════════════════════════
  let activeCaptureMode = 'Demo / Simulated Traffic';
  function renderCaptureConfigPage() {
    const modes = [
      ['Live Capture', 'Capture directly from a network interface.', 'radio'],
      ['Demo / Simulated Traffic', 'Generate realistic traffic for exploration.', 'activity'],
      ['Offline PCAP Analysis', 'Analyze a local capture file.', 'upload']
    ];

    return `
      <div class="mode-grid">
        ${modes.map(m => `
          <button class="mode-card ${activeCaptureMode === m[0] ? 'active' : ''}" data-mode="${m[0]}" type="button">
            <span>${icon(m[2], 22)}</span>
            <div>
              <b>${m[0]}</b>
              <p>${m[1]}</p>
            </div>
            <i class="radio-select"></i>
          </button>
        `).join('')}
      </div>

      <div class="config-layout">
        <div class="card config-form">
          <div class="card-head"><div class="card-title">${activeCaptureMode}</div></div>

          ${activeCaptureMode === 'Live Capture' ? `
            <label class="field">
              <span>Network interface</span>
              <input value="eth0" />
            </label>
            <label class="field">
              <span>BPF packet filter</span>
              <input value="tcp or udp" />
            </label>
            <div class="field-row">
              <label class="field"><span>Packet count</span><input value="0 (unlimited)" /></label>
              <label class="field"><span>Timeout</span><input value="60 seconds" /></label>
            </div>
            <label class="toggle-row">
              <span><b>Save output PCAP</b><small>Write captured packets to a local file</small></span>
              <input type="checkbox" />
              <i></i>
            </label>
            <p class="callout warn">
              ${icon('alert', 16)}
              <span>Live packet capture requires appropriate operating-system permissions (root/Administrator) and explicit backend configuration.</span>
            </p>
            <button class="btn primary" type="button" style="margin-top: 8px;">
              ${icon('play', 14)} Start live capture
            </button>
          ` : activeCaptureMode === 'Offline PCAP Analysis' ? `
            <div class="dropzone">
              ${icon('upload', 28)}
              <b>Select a PCAP file</b>
              <p>Choose a .pcap or .pcapng file available to the analysis engine.</p>
              <button class="btn" type="button" style="margin-top: 6px;">Choose file</button>
            </div>
            <label class="field">
              <span>BPF analysis filter (optional)</span>
              <input value="No filter" />
            </label>
            <button class="btn primary" type="button" style="margin-top: 8px;">
              ${icon('play', 14)} Start analysis
            </button>
          ` : `
            <label class="field">
              <span>Packets per second</span>
              <input value="42" />
            </label>
            <label class="toggle-row">
              <span><b>Include simulated security events</b><small>Generate representative heuristic anomaly findings</small></span>
              <input type="checkbox" checked />
              <i></i>
            </label>
            <p class="callout info">
              ${icon('activity', 16)}
              <span>The standard hosted backend uses simulated traffic. All generated telemetry is clearly labelled as sample data.</span>
            </p>
            <div class="actions" style="margin-top: 12px;">
              <button class="btn" type="button">${icon('x', 14)} Stop demo</button>
              <button class="btn primary" type="button">${icon('play', 14)} Restart demo</button>
            </div>
          `}
        </div>

        <div class="card capture-status">
          <span class="status-orb">${icon('activity', 26)}</span>
          <span class="badge good">Running</span>
          <h3>${activeCaptureMode} active</h3>
          <p>Simulated traffic at 42 packets per second.</p>
          <div>
            <span>Duration <b>${formatDuration(state.uptimeSeconds || 2538)}</b></span>
            <span>Packets <b>${(state.stats.total_packets || 18432).toLocaleString()}</b></span>
            <span>Output <b>Not saved</b></span>
          </div>
        </div>
      </div>
    `;
  }

  // ══════════════════════════════════════════════════════════════════════════
  //  13. SETTINGS SCREEN
  // ══════════════════════════════════════════════════════════════════════════
  let activeSettingsTab = 'Appearance';
  function renderSettingsPage() {
    const tabs = ['Appearance', 'Connection', 'Display preferences', 'Charts', 'Accessibility', 'About NetScope'];
    return `
      <div class="settings-layout">
        <aside>
          ${tabs.map(t => `
            <button class="${t === activeSettingsTab ? 'active' : ''}" data-tab="${t}" type="button">${t}</button>
          `).join('')}
        </aside>

        <div>
          <div class="card">
            <div class="card-head"><div class="card-title">Appearance</div></div>
            <div class="theme-options">
              <button class="${state.theme === 'dark' ? 'active' : ''}" data-theme-val="dark" type="button">
                <span class="theme-preview dark"></span>
                <b>Dark</b>
              </button>
              <button class="${state.theme === 'light' ? 'active' : ''}" data-theme-val="light" type="button">
                <span class="theme-preview light"></span>
                <b>Light</b>
              </button>
              <button data-theme-val="system" type="button">
                <span class="theme-preview system"></span>
                <b>System</b>
              </button>
            </div>
          </div>

          <div class="card">
            <div class="card-head"><div class="card-title">Connection</div></div>
            <label class="field">
              <span>Backend WebSocket URL</span>
              <input id="setting-ws-url" value="${escapeHtml(state.wsUrl)}" />
            </label>
            <label class="toggle-row">
              <span><b>Reconnect automatically</b><small>Retry if backend connection drops</small></span>
              <input type="checkbox" checked />
              <i></i>
            </label>
            <label class="toggle-row">
              <span><b>Show connection notifications</b><small>Display status changes</small></span>
              <input type="checkbox" checked />
              <i></i>
            </label>
          </div>

          <div class="card">
            <div class="card-head"><div class="card-title">Display preferences</div></div>
            <div class="field-row">
              <label class="field"><span>Table density</span><input value="Compact" /></label>
              <label class="field"><span>Default time range</span><input value="Last 1 hour" /></label>
            </div>
            <label class="toggle-row">
              <span><b>Show technical timestamps</b><small>Use 24-hour timestamps with milliseconds</small></span>
              <input type="checkbox" checked />
              <i></i>
            </label>
            <label class="toggle-row">
              <span><b>Reduced motion</b><small>Minimize non-essential interface animation</small></span>
              <input type="checkbox" />
              <i></i>
            </label>
          </div>

          <div class="save-bar">
            <span>${icon('check', 16)} Preferences saved locally</span>
            <button id="btn-save-settings" class="btn primary" type="button">Save changes</button>
          </div>
        </div>
      </div>
    `;
  }

  // ══════════════════════════════════════════════════════════════════════════
  //  14. DOCUMENTATION SCREEN
  // ══════════════════════════════════════════════════════════════════════════
  function renderDocsPage() {
    return `
      <div class="docs-layout">
        <div class="card docs-list">
          ${[
            'Getting started', 'Capture modes', 'Packet filters',
            'Threat scoring', 'Detection reference', 'Encryption heuristics', 'Reports and exports'
          ].map((t, i) => `
            <button class="${i === 0 ? 'active' : ''}" type="button">
              ${icon(i < 3 ? 'book' : 'chevron', 16)} ${t} ${icon('chevron', 14)}
            </button>
          `).join('')}
        </div>

        <div class="card">
          <article class="docs-article">
            <span class="badge info">Getting started</span>
            <h2>Understand your network activity</h2>
            <p>NetScope combines packet capture, protocol dissection and heuristic security analysis in a single enterprise investigation workspace.</p>

            <h3>Choose a capture mode</h3>
            <p>Use simulated traffic to explore the interface, live capture when the backend has operating-system permissions (raw socket/Scapy access), or analyze an existing PCAP file available to the engine.</p>

            <h3>Interpret findings carefully</h3>
            <p>Security alerts and host scores are heuristic indicators. They help prioritize investigation but do not confirm malicious activity or compromise without contextual packet analysis.</p>

            <div class="callout info">
              ${icon('shield', 18)}
              <span>
                <b>Threat scoring thresholds</b><br />
                Clean: below 25 · Suspicious: 25–69 · Malicious: 70 and above
              </span>
            </div>
          </article>
        </div>
      </div>
    `;
  }

  // ══════════════════════════════════════════════════════════════════════════
  //  Component Render Helpers
  // ══════════════════════════════════════════════════════════════════════════
  function renderSparkbars(arr) {
    return (arr || [20, 40, 60, 80]).map(v => `<i style="height: ${v}%;"></i>`).join('');
  }

  function renderThroughputSvgChart(entropy = false, timeframe = (state.trafficTimeframe || '1H')) {
    const isEntropy = entropy;
    const tfData = TRAFFIC_TIMEFRAME_DATA[timeframe] || TRAFFIC_TIMEFRAME_DATA['1H'];
    const yLabels = isEntropy ? ['8.0', '6.0', '4.0', '0'] : tfData.yLabels;
    const pathArea = isEntropy 
      ? 'M0 170 C80 120 100 80 170 105 S250 40 320 72 S420 48 480 66 S580 36 650 55 S730 26 800 38 V210H0Z'
      : tfData.pathArea;
    const pathLinePrimary = isEntropy
      ? 'M0 170 C80 120 100 80 170 105 S250 40 320 72 S420 48 480 66 S580 36 650 55 S730 26 800 38'
      : tfData.pathPrimary;
    const pathLineSecondary = tfData.pathSecondary;
    const xLabels = isEntropy ? ['14:00', '14:08', '14:16', '14:24', '14:32'] : tfData.xLabels;

    return `
      <div class="chart-wrap">
        <div class="y-axis">
          <span>${yLabels[0]}</span>
          <span>${yLabels[1]}</span>
          <span>${yLabels[2]}</span>
          <span>${yLabels[3]}</span>
        </div>
        <div class="plot">
          <div class="grid-lines"><i></i><i></i><i></i><i></i></div>
          ${isEntropy ? `<div class="threshold-line"><span>7.2 threshold</span></div>` : ''}
          <svg viewBox="0 0 800 210" preserveAspectRatio="none">
            <path class="area" d="${pathArea}"></path>
            <path class="line primary" d="${pathLinePrimary}"></path>
            ${!isEntropy ? `<path class="line secondary" d="${pathLineSecondary}"></path>` : ''}
          </svg>
          <div class="x-axis">
            ${xLabels.map(label => `<span>${label}</span>`).join('')}
          </div>
        </div>
      </div>
    `;
  }

  function renderProtocolBars() {
    const data = [
      ['TCP', 62, '11,428', 'dot'],
      ['UDP', 21, '3,872', 'dot d1'],
      ['ICMP', 8, '1,475', 'dot d3'],
      ['ARP', 5, '922', 'dot d2'],
      ['Other', 4, '735', 'dot d4']
    ];

    return `
      <div class="protocol-list">
        ${data.map(d => `
          <div class="protocol-row">
            <div class="protocol-meta">
              <span><i class="${d[3]}"></i> ${d[0]}</span>
              <b>${d[1]}%</b>
            </div>
            <div class="bar"><i style="width: ${d[1]}%;"></i></div>
            <small>${d[2]} packets</small>
          </div>
        `).join('')}
      </div>
    `;
  }

  function renderHostMini() {
    const hosts = (state.stats.top_hosts || []).slice(0, 4);
    return `
      <div class="host-mini">
        ${hosts.map((h, i) => `
          <div>
            <span class="host-rank">${i + 1}</span>
            <span>
              <b>${h.ip}</b>
              <small>${h.bytes} transferred</small>
            </span>
            <span class="score ${h.score >= 70 ? 'danger' : h.score >= 25 ? 'warn' : 'good'}">${h.score}</span>
          </div>
        `).join('')}
      </div>
    `;
  }

  function renderTopologyMiniGraph() {
    return `
      <div class="topology-status-bar">
        <span><i class="pulse-indicator"></i> <b>Live mesh packet transfer</b></span>
        <span class="mono" style="font-size: 10px; color: var(--muted);">4 links · <span id="topo-pps-stat">42</span> pkts/s</span>
      </div>
      <div class="topology" id="overview-topology-wrap">
        <svg viewBox="0 0 100 100" preserveAspectRatio="none">
          <defs>
            <filter id="glow-teal" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur in="SourceGraphic" stdDeviation="1.5" result="blur" />
              <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
            </filter>
            <filter id="glow-blue" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur in="SourceGraphic" stdDeviation="1.5" result="blur" />
              <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
            </filter>
            <filter id="glow-danger" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur in="SourceGraphic" stdDeviation="2" result="blur" />
              <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
            </filter>
          </defs>

          <!-- 4 Active Symmetrical Network Conduit Links Connecting Center to Corners -->
          <line x1="50" y1="50" x2="20" y2="26" class="topo-link active-link" />
          <line x1="50" y1="50" x2="80" y2="26" class="topo-link active-link" />
          <line x1="50" y1="50" x2="20" y2="76" class="topo-link risk" />
          <line x1="50" y1="50" x2="80" y2="76" class="topo-link active-link" />

          <!-- Live Animated Packet Transfers -->
          <!-- 1. Outgoing Web Flow: Workstation -> Gateway -> Cloud (Blue) -->
          <circle r="2.2" fill="#5795e8" filter="url(#glow-blue)">
            <animateMotion path="M20,26 L50,50 L80,26" dur="2.8s" repeatCount="indefinite" />
          </circle>
          <circle r="2.2" fill="#5795e8" filter="url(#glow-blue)">
            <animateMotion path="M20,26 L50,50 L80,26" dur="2.8s" begin="1.4s" repeatCount="indefinite" />
          </circle>

          <!-- 2. Incoming Web Response: Cloud -> Gateway -> Workstation (Teal) -->
          <circle r="2.2" fill="#19b89a" filter="url(#glow-teal)">
            <animateMotion path="M80,26 L50,50 L20,26" dur="2.4s" begin="0.7s" repeatCount="indefinite" />
          </circle>
          <circle r="2.2" fill="#19b89a" filter="url(#glow-teal)">
            <animateMotion path="M80,26 L50,50 L20,26" dur="2.4s" begin="1.9s" repeatCount="indefinite" />
          </circle>

          <!-- 3. Threat Scan / Attack Flow: Attacker -> Gateway (Danger Red) -->
          <circle r="2.6" fill="#e05260" filter="url(#glow-danger)">
            <animateMotion path="M20,76 L50,50" dur="1.3s" repeatCount="indefinite" />
          </circle>
          <circle r="2.6" fill="#e05260" filter="url(#glow-danger)">
            <animateMotion path="M20,76 L50,50" dur="1.3s" begin="0.65s" repeatCount="indefinite" />
          </circle>

          <!-- 4. LAN Backup & Database Sync: Gateway <-> Local Host -->
          <circle r="2.0" fill="#19b89a" filter="url(#glow-teal)">
            <animateMotion path="M50,50 L80,76" dur="3.2s" begin="0.4s" repeatCount="indefinite" />
          </circle>
          <circle r="2.0" fill="#5795e8" filter="url(#glow-blue)">
            <animateMotion path="M80,76 L50,50" dur="3.0s" begin="1.8s" repeatCount="indefinite" />
          </circle>
        </svg>

        <!-- Center Gateway Node -->
        <div class="node gateway good" style="left: 50%; top: 50%;" data-topo-ip="192.168.1.1" data-topo-role="Core Gateway Router" data-topo-status="Clean" data-topo-score="0">
          <span>${icon('network', 18)}</span>
          <label>192.168.1.1 (Gateway)</label>
        </div>

        <!-- Workstation (Top-Left) -->
        <div class="node host info" style="left: 20%; top: 26%;" data-topo-ip="192.168.1.24" data-topo-role="Internal Workstation" data-topo-status="Clean" data-topo-score="12">
          <span>${icon('server', 16)}</span>
          <label>192.168.1.24</label>
        </div>

        <!-- Threat Host (Bottom-Left) -->
        <div class="node host danger" style="left: 20%; top: 76%;" data-topo-ip="10.0.0.42" data-topo-role="Suspicious Attacker" data-topo-status="Malicious" data-topo-score="82">
          <span>${icon('server', 16)}</span>
          <label>10.0.0.42 (Malicious)</label>
        </div>

        <!-- External Cloud / CDN (Top-Right) -->
        <div class="node external good" style="left: 80%; top: 26%;" data-topo-ip="172.217.14.206" data-topo-role="Google Cloud / Web (HTTPS)" data-topo-status="Clean" data-topo-score="0">
          <span>${icon('server', 16)}</span>
          <label>172.217.14.206</label>
        </div>

        <!-- Local Host / Storage (Bottom-Right) -->
        <div class="node host good" style="left: 80%; top: 76%;" data-topo-ip="192.168.1.105" data-topo-role="Local File Server" data-topo-status="Clean" data-topo-score="0">
          <span>${icon('server', 16)}</span>
          <label>192.168.1.105</label>
        </div>
      </div>
    `;
  }

  function updateTopMetricsDisplay() {
    const subtitle = $('#sidebar-conn-subtitle');
    if (subtitle && state.connState === 'live') {
      subtitle.textContent = `${state.isDemoMode ? 'Demo mode' : 'Live capture'} · ${Math.round(state.stats.pps || 18)} pps`;
    }
  }

  // ══════════════════════════════════════════════════════════════════════════
  //  Event Listeners & Interaction Wiring
  // ══════════════════════════════════════════════════════════════════════════
  function attachGlobalListeners() {
    // Sidebar collapse/expand button & brand click in collapsed state
    $('#sidebar-collapse-btn')?.addEventListener('click', () => {
      if (window.innerWidth <= 768 || state.mobileMenuOpen) {
        closeMobileMenu();
      } else {
        toggleSidebarCollapse();
      }
    });
    $('#brand-header')?.addEventListener('click', (e) => {
      if (window.innerWidth <= 768 || state.mobileMenuOpen) {
        return;
      }
      if (state.sidebarCollapsed && !e.target.closest('#sidebar-collapse-btn')) {
        toggleSidebarCollapse();
      }
    });

    // Mobile menu toggles
    $('#mobile-menu-btn')?.addEventListener('click', openMobileMenu);
    $('#sidebar-backdrop')?.addEventListener('click', closeMobileMenu);

    // Theme toggle button
    $('#btn-theme-toggle')?.addEventListener('click', toggleTheme);

    // Overview Network Traffic timeframe toggle (1H, 6H, 24H)
    $('#page-content')?.addEventListener('click', (e) => {
      const btn = e.target.closest('#traffic-timeframe-controls button[data-timeframe]');
      if (!btn) return;
      const tf = btn.getAttribute('data-timeframe');
      if (!tf || tf === state.trafficTimeframe) return;
      state.trafficTimeframe = tf;

      const controls = $('#traffic-timeframe-controls');
      if (controls) {
        controls.querySelectorAll('button').forEach(b => b.classList.toggle('active', b === btn));
      }

      const data = TRAFFIC_TIMEFRAME_DATA[tf] || TRAFFIC_TIMEFRAME_DATA['1H'];
      const chartContainer = $('#traffic-chart-container');
      if (chartContainer) {
        chartContainer.innerHTML = renderThroughputSvgChart(false, tf);
      }
      const rateEl = $('#traffic-legend-rate');
      if (rateEl) {
        rateEl.textContent = `Current ${data.throughput} Mbps`;
      }
      const volEl = $('#traffic-legend-vol');
      if (volEl) {
        volEl.textContent = `${data.totalVolume} total (${tf})`;
      }
    });

    // Settings shortcut button
    $('#btn-top-settings')?.addEventListener('click', () => navigateTo('settings'));
    $('#btn-notifications')?.addEventListener('click', () => navigateTo('alerts'));

    // Back navigation button (Settings header & breadcrumbs)
    $('#page-content')?.addEventListener('click', (e) => {
      const backBtn = e.target.closest('#btn-settings-back, #btn-back-breadcrumb, .btn-back-pill, [data-action="go-back"]');
      if (backBtn) {
        e.preventDefault();
        navigateTo(state.previousRoute || 'overview');
      }
    });

    // Interactive topology node click inspection
    $('#page-content')?.addEventListener('click', (e) => {
      const nodeEl = e.target.closest('.node[data-topo-ip]');
      if (!nodeEl) return;
      const ip = nodeEl.getAttribute('data-topo-ip');
      const role = nodeEl.getAttribute('data-topo-role') || 'Observed Host';
      const status = nodeEl.getAttribute('data-topo-status') || 'Clean';
      
      const wrap = nodeEl.closest('.topology');
      if (!wrap) return;

      let tooltip = wrap.querySelector('#topo-active-tooltip');
      if (!tooltip) {
        tooltip = document.createElement('div');
        tooltip.id = 'topo-active-tooltip';
        tooltip.className = 'topo-tooltip';
        wrap.appendChild(tooltip);
      }
      
      const badgeTone = status === 'Malicious' ? 'danger' : status === 'Suspicious' ? 'warn' : 'good';
      tooltip.innerHTML = `
        <span><b>${ip}</b> <span class="badge ${badgeTone}" style="margin-left:4px">${status}</span></span>
        <span style="color:var(--text-2); font-size:9.5px">${role}</span>
        <button class="btn btn-xs" type="button" style="height:22px; padding:0 8px; font-size:9.5px; margin-left:auto" onclick="window.location.hash='#packets'">Inspect →</button>
      `;
      tooltip.style.display = 'flex';
      
      clearTimeout(window.__topoTimer);
      window.__topoTimer = setTimeout(() => {
        if (tooltip) tooltip.style.display = 'none';
      }, 5000);
    });

    // Connection configuration dialog
    const connDialog = $('#conn-dialog');
    $('#sidebar-conn-card')?.addEventListener('click', () => {
      $('#conn-url-input').value = state.wsUrl;
      connDialog?.showModal();
    });
    $('#conn-dialog-cancel')?.addEventListener('click', () => connDialog?.close());
    $('#conn-dialog-save')?.addEventListener('click', () => {
      const input = $('#conn-url-input');
      if (input && input.value.trim()) {
        state.wsUrl = input.value.trim();
        localStorage.setItem(STORAGE_WS_KEY, state.wsUrl);
        initWebSocket();
      }
      connDialog?.close();
    });

    // Global Search (⌘ K shortcut)
    window.addEventListener('keydown', (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        $('#global-search-input')?.focus();
      }
    });

    // Hash routing
    window.addEventListener('hashchange', () => {
      const route = window.location.hash.replace('#', '');
      if (route && route !== state.activeRoute) {
        navigateTo(route);
      }
    });
  }

  function attachPageListeners(route) {
    // Universal Pause view buttons
    const pauseHandler = () => {
      state.paused = !state.paused;
      renderActivePage();
    };
    $('#strip-pause-btn')?.addEventListener('click', pauseHandler);
    $('#chart-pause-btn')?.addEventListener('click', pauseHandler);
    $('#btn-head-pause')?.addEventListener('click', pauseHandler);

    $('#btn-head-config')?.addEventListener('click', () => navigateTo('capture'));

    // Live Traffic Workspace Listeners
    if (route === 'live' || route === 'packets') {
      // Search input
      const searchInput = $('#stream-search-input') || $('#explorer-query');
      if (searchInput) {
        searchInput.addEventListener('input', (e) => {
          state.streamSearch = e.target.value;
          const filtered = getFilteredPackets();
          const body = $('#packet-stream-body') || $('#explorer-packet-body');
          if (body) body.innerHTML = renderPacketTableRows(filtered, state.selectedPacketId);
        });
      }

      // Protocol Quick-Filter buttons
      $$('#proto-filter-group button').forEach((btn) => {
        btn.addEventListener('click', () => {
          $$('#proto-filter-group button').forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
          state.streamProtocol = btn.getAttribute('data-proto');
          const filtered = getFilteredPackets();
          const body = $('#packet-stream-body') || $('#explorer-packet-body');
          if (body) body.innerHTML = renderPacketTableRows(filtered, state.selectedPacketId);
        });
      });

      // Clear button
      $('#btn-stream-clear')?.addEventListener('click', () => {
        state.packets = [];
        renderActivePage();
      });
      $('#explorer-clear-btn')?.addEventListener('click', () => {
        state.streamSearch = '';
        state.streamProtocol = 'ALL';
        renderActivePage();
      });

      // Auto-scroll toggle
      $('#stream-autoscroll-btn')?.addEventListener('click', () => {
        state.autoScroll = !state.autoScroll;
        const btn = $('#stream-autoscroll-btn');
        if (btn) {
          btn.className = `btn ${state.autoScroll ? 'primary' : 'ghost'}`;
          btn.innerHTML = `${icon('activity', 14)} Auto-scroll: ${state.autoScroll ? 'ON' : 'OFF'}`;
        }
      });

      // Packet Row Selection (Delegated)
      const tableBody = $('#packet-stream-body') || $('#explorer-packet-body');
      if (tableBody) {
        tableBody.addEventListener('click', (e) => {
          const row = e.target.closest('.packet-row');
          if (!row) return;

          const pktId = parseInt(row.getAttribute('data-packet-id'), 10);
          if (!pktId) return;

          state.selectedPacketId = pktId;
          const pkt = state.packets.find(p => p.id === pktId);

          // Update row highlight
          $$('.packet-row', tableBody).forEach(r => r.classList.remove('selected'));
          row.classList.add('selected');

          // Re-render Inspector panel
          const workspace = $('.packet-workspace');
          if (workspace && pkt) {
            const oldInspector = $('#packet-inspector-panel');
            if (oldInspector) oldInspector.remove();
            workspace.classList.remove('no-inspector');
            workspace.insertAdjacentHTML('beforeend', renderPacketInspector(pkt));
            attachInspectorListeners();
          }
        });
      }

      attachInspectorListeners();
    }

    // Protocol Analytics Tabs
    if (route === 'protocols') {
      $$('.tabs button').forEach((btn) => {
        btn.addEventListener('click', () => {
          activeProtoTab = btn.getAttribute('data-tab');
          renderActivePage();
        });
      });
    }

    // Capture Mode Selector
    if (route === 'capture') {
      $$('.mode-card').forEach((card) => {
        card.addEventListener('click', () => {
          activeCaptureMode = card.getAttribute('data-mode');
          renderActivePage();
        });
      });
    }

    // Settings Theme Selector
    if (route === 'settings') {
      $$('.theme-options button').forEach((btn) => {
        btn.addEventListener('click', () => {
          const val = btn.getAttribute('data-theme-val');
          if (val === 'dark' || val === 'light') {
            state.theme = val;
            applyTheme(val);
            localStorage.setItem(STORAGE_THEME_KEY, val);
          } else {
            const sysDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            state.theme = sysDark ? 'dark' : 'light';
            applyTheme(state.theme);
          }
          renderActivePage();
        });
      });

      $('#btn-save-settings')?.addEventListener('click', () => {
        const input = $('#setting-ws-url');
        if (input && input.value.trim()) {
          state.wsUrl = input.value.trim();
          localStorage.setItem(STORAGE_WS_KEY, state.wsUrl);
          initWebSocket();
        }
        alert('Settings saved successfully.');
      });
    }

    // Export Reports / Alerts Actions
    $('#btn-export-session-json')?.addEventListener('click', exportSessionJson);
    $('#btn-export-session-html')?.addEventListener('click', exportSessionHtml);
    $('#btn-export-alerts-json')?.addEventListener('click', exportAlertsJson);
  }

  function attachInspectorListeners() {
    $('#inspector-close-btn')?.addEventListener('click', () => {
      const inspector = $('#packet-inspector-panel');
      if (inspector) inspector.remove();
      $('.packet-workspace')?.classList.add('no-inspector');
      state.selectedPacketId = null;
      $$('.packet-row').forEach(r => r.classList.remove('selected'));
    });

    // Copy buttons
    $$('.copy-btn').forEach((btn) => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const text = btn.getAttribute('data-copy');
        if (text) copyToClipboard(text, btn);
      });
    });
  }

  function exportSessionJson() {
    const payload = {
      project: 'NetScope Network Packet Analyzer',
      exported_at: new Date().toISOString(),
      stats: state.stats,
      alerts: state.alerts,
      sample_packets: state.packets.slice(0, 50)
    };
    downloadFile('netscope-session-report.json', JSON.stringify(payload, null, 2), 'application/json');
  }

  function exportAlertsJson() {
    const payload = {
      project: 'NetScope Security Alerts',
      exported_at: new Date().toISOString(),
      alerts_count: state.alerts.length,
      alerts: state.alerts
    };
    downloadFile('netscope-security-alerts.json', JSON.stringify(payload, null, 2), 'application/json');
  }

  function exportSessionHtml() {
    const s = state.stats;
    const htmlContent = `<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>NetScope Session Report</title>
<style>body{font-family:sans-serif;padding:30px;background:#0b1020;color:#e8edf5;} h1{color:#19b89a;} table{width:100%;border-collapse:collapse;margin-top:20px;} th,td{padding:8px 12px;border:1px solid #29364b;text-align:left;} th{background:#182235;color:#a0aec0;}</style>
</head><body>
<h1>NetScope Session Report</h1>
<p>Generated: ${new Date().toLocaleString()}</p>
<p>Total Packets: ${s.total_packets || 18432} | Throughput: ${s.throughput_mbps || 6.24} Mbps | Security Alerts: ${state.alerts.length}</p>
<h2>Security Detections</h2>
<table><tr><th>Severity</th><th>Type</th><th>Source</th><th>Destination</th><th>Description</th></tr>
${state.alerts.map(a => `<tr><td>${a.severity}</td><td>${a.type}</td><td>${a.src}</td><td>${a.dst}</td><td>${a.detail || a.description || ''}</td></tr>`).join('')}
</table></body></html>`;
    downloadFile('netscope-session-report.html', htmlContent, 'text/html');
  }

  function downloadFile(filename, content, type) {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  // ══════════════════════════════════════════════════════════════════════════
  //  App Initialization
  // ══════════════════════════════════════════════════════════════════════════
  function init() {
    applyTheme(state.theme);
    $('#app-root')?.classList.toggle('collapsed', state.sidebarCollapsed);

    // Initial route from URL hash or default 'live'
    const initialRoute = window.location.hash.replace('#', '') || 'live';
    renderSidebar();
    navigateTo(initialRoute);
    attachGlobalListeners();

    // Start WebSocket
    initWebSocket();
  }

  // Run on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
