import { useMemo, useState } from 'react'

type PageId =
  | 'overview' | 'live' | 'packets' | 'topology' | 'hosts' | 'flows'
  | 'threats' | 'alerts' | 'encryption' | 'protocols' | 'reports'
  | 'capture' | 'settings' | 'docs'

type IconName =
  | 'grid' | 'activity' | 'packet' | 'network' | 'server' | 'flow' | 'shield'
  | 'alert' | 'lock' | 'chart' | 'report' | 'sliders' | 'settings' | 'book'
  | 'search' | 'bell' | 'sun' | 'chevron' | 'pause' | 'play' | 'filter'
  | 'download' | 'more' | 'clock' | 'x' | 'check' | 'upload' | 'radio'

const paths: Record<IconName, string> = {
  grid: 'M4 4h6v6H4zM14 4h6v6h-6zM4 14h6v6H4zM14 14h6v6h-6z',
  activity: 'M3 12h4l2.5-7 5 14 2.5-7h4',
  packet: 'M12 3l9 5-9 5-9-5 9-5zm-9 9l9 5 9-5M3 16l9 5 9-5',
  network: 'M12 5v4m0 6v4M5 12h14M5 9v6m14-6v6M9 9h6v6H9zM3 7h4v2H3zm0 8h4v2H3zm14-8h4v2h-4zm0 8h4v2h-4z',
  server: 'M4 4h16v6H4zM4 14h16v6H4zM8 7h.01M8 17h.01',
  flow: 'M5 5h6v6H5zM13 13h6v6h-6zM11 8h4a2 2 0 012 2v3M8 11v4a2 2 0 002 2h3',
  shield: 'M12 3l8 3v5c0 5-3.4 8.5-8 10-4.6-1.5-8-5-8-10V6l8-3zm-3 9l2 2 4-5',
  alert: 'M12 3l10 18H2L12 3zm0 6v5m0 3h.01',
  lock: 'M6 10h12v10H6zM8 10V7a4 4 0 018 0v3',
  chart: 'M4 19V9m5 10V5m5 14v-7m5 7V3',
  report: 'M6 3h9l4 4v14H6zM14 3v5h5M9 13h6m-6 4h6',
  sliders: 'M4 6h10m4 0h2M4 12h2m4 0h10M4 18h7m4 0h5M14 4v4M6 10v4m5 2v4',
  settings: 'M12 9a3 3 0 100 6 3 3 0 000-6zm8 3l2-1-2-4-2 .5-2-1-1-2h-5l-1 2-2 1L5 7l-2 4 2 1v2l-2 1 2 4 2-.5 2 1 1 2h5l1-2 2-1 2 .5 2-4-2-1z',
  book: 'M4 5a3 3 0 013-2h5v17H7a3 3 0 00-3 1zm16 0a3 3 0 00-3-2h-5v17h5a3 3 0 013 1z',
  search: 'M10.5 4a6.5 6.5 0 100 13 6.5 6.5 0 000-13zm5 11.5L21 21',
  bell: 'M6 9a6 6 0 0112 0c0 7 3 7 3 8H3c0-1 3-1 3-8m4 11h4',
  sun: 'M12 8a4 4 0 100 8 4 4 0 000-8zm0-6v2m0 16v2M4.9 4.9l1.4 1.4m11.4 11.4l1.4 1.4M2 12h2m16 0h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4',
  chevron: 'M9 18l6-6-6-6',
  pause: 'M8 5v14m8-14v14',
  play: 'M7 4l13 8-13 8z',
  filter: 'M3 5h18l-7 8v6l-4 2v-8z',
  download: 'M12 3v12m-5-5l5 5 5-5M4 19h16',
  more: 'M5 12h.01M12 12h.01M19 12h.01',
  clock: 'M12 3a9 9 0 100 18 9 9 0 000-18zm0 4v5l3 2',
  x: 'M6 6l12 12M18 6L6 18',
  check: 'M5 12l4 4L19 6',
  upload: 'M12 16V4m-5 5l5-5 5 5M4 16v4h16v-4',
  radio: 'M12 12h.01M8.5 8.5a5 5 0 000 7m7-7a5 5 0 010 7M5.5 5.5a9 9 0 000 13m0-13a9 9 0 010 13',
}

function Icon({ name, size = 18 }: { name: IconName; size?: number }) {
  const fill = ['grid', 'play'].includes(name) ? 'currentColor' : 'none'
  return <svg aria-hidden="true" width={size} height={size} viewBox="0 0 24 24" fill={fill} stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round"><path d={paths[name]} /></svg>
}

const nav: { label: string; items: { id: PageId; name: string; icon: IconName }[] }[] = [
  { label: 'Overview', items: [{ id: 'overview', name: 'Dashboard', icon: 'grid' }] },
  { label: 'Network monitoring', items: [
    { id: 'live', name: 'Live Traffic', icon: 'activity' },
    { id: 'packets', name: 'Packet Explorer', icon: 'packet' },
    { id: 'topology', name: 'Network Topology', icon: 'network' },
    { id: 'hosts', name: 'Hosts', icon: 'server' },
    { id: 'flows', name: 'Sessions & Flows', icon: 'flow' },
  ]},
  { label: 'Security', items: [
    { id: 'threats', name: 'Threat Intelligence', icon: 'shield' },
    { id: 'alerts', name: 'Security Alerts', icon: 'alert' },
    { id: 'encryption', name: 'Encryption Analysis', icon: 'lock' },
  ]},
  { label: 'Analytics', items: [
    { id: 'protocols', name: 'Protocol Analytics', icon: 'chart' },
    { id: 'reports', name: 'Reports', icon: 'report' },
  ]},
  { label: 'Configuration', items: [
    { id: 'capture', name: 'Capture Configuration', icon: 'sliders' },
    { id: 'settings', name: 'Settings', icon: 'settings' },
    { id: 'docs', name: 'Documentation', icon: 'book' },
  ]},
]

const pageMeta: Record<PageId, [string, string]> = {
  overview: ['Network Overview', 'Monitor network activity, traffic performance and security events.'],
  live: ['Live Traffic', 'Observe packet volume and throughput as the capture continues.'],
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
  docs: ['Documentation', 'Understand capture, analysis and detection behavior.'],
}

function Button({ children, icon, kind = 'secondary', onClick, disabled = false }: { children?: React.ReactNode; icon?: IconName; kind?: 'primary' | 'secondary' | 'ghost' | 'danger'; onClick?: () => void; disabled?: boolean }) {
  return <button className={`btn ${kind}`} onClick={onClick} disabled={disabled}>{icon && <Icon name={icon} size={16} />}{children}</button>
}

function Badge({ children, tone = 'neutral' }: { children: React.ReactNode; tone?: 'good' | 'warn' | 'danger' | 'info' | 'neutral' | 'purple' }) {
  return <span className={`badge ${tone}`}><i />{children}</span>
}

function Card({ title, action, children, className = '' }: { title?: string; action?: React.ReactNode; children: React.ReactNode; className?: string }) {
  return <section className={`card ${className}`}>{title && <div className="card-head"><div className="card-title">{title}</div>{action}</div>}{children}</section>
}

function Metric({ label, value, unit, detail, tone = 'teal', bars }: { label: string; value: string; unit?: string; detail: string; tone?: string; bars?: number[] }) {
  return <Card className="metric"><div className="metric-label">{label}</div><div className="metric-value">{value} <small>{unit}</small></div><div className="metric-bottom"><span>{detail}</span>{bars && <Spark bars={bars} tone={tone} />}</div></Card>
}

function Spark({ bars, tone = 'teal' }: { bars: number[]; tone?: string }) {
  return <div className={`spark ${tone}`}>{bars.map((v, i) => <i key={i} style={{ height: `${v}%` }} />)}</div>
}

const packets = [
  ['18432', '14:32:08.241', 'TCP', '192.168.1.24', '52418', '172.217.14.206', '443', '1,428', 'ACK', 'TLS Application Data'],
  ['18431', '14:32:08.237', 'DNS', '192.168.1.16', '55192', '192.168.1.1', '53', '86', '—', 'Standard query A api.github.com'],
  ['18430', '14:32:08.216', 'TCP', '10.0.0.42', '49162', '185.199.108.133', '443', '1,514', 'PSH, ACK', 'TLS Application Data'],
  ['18429', '14:32:08.192', 'UDP', '192.168.1.31', '5353', '224.0.0.251', '5353', '234', '—', 'mDNS response PTR workstation.local'],
  ['18428', '14:32:08.154', 'ICMP', '192.168.1.1', '—', '192.168.1.24', '—', '98', '—', 'Echo reply id=0x2f1 seq=442'],
  ['18427', '14:32:08.108', 'TCP', '192.168.1.24', '52416', '104.18.32.47', '443', '66', 'SYN', '52416 → 443 [SYN] Seq=0'],
  ['18426', '14:32:08.072', 'ARP', '192.168.1.1', '—', '192.168.1.18', '—', '60', '—', 'Who has 192.168.1.18? Tell 192.168.1.1'],
  ['18425', '14:32:07.998', 'TCP', '45.33.32.156', '42002', '192.168.1.24', '22', '74', 'SYN', '42002 → 22 [SYN] Seq=0'],
]

const alerts = [
  ['High', 'Port Scan', '45.33.32.156', '192.168.1.24', '18 ports contacted in 4.2 seconds', '14:31:52'],
  ['Suspicious', 'DNS Tunneling', '192.168.1.42', '8.8.8.8', 'Unusually long DNS query (148 chars)', '14:29:18'],
  ['High', 'Credential Exposure', '10.0.0.18', '172.16.4.20', 'Cleartext FTP authentication pattern', '14:22:07'],
  ['Info', 'Low TTL', '192.168.1.88', '192.168.1.1', 'Packet observed with TTL value of 2', '14:18:40'],
  ['Suspicious', 'C2 Beaconing', '10.0.0.42', '185.199.108.133', 'Regular 60 second connection interval', '14:12:16'],
]

const hosts = [
  ['192.168.1.24', 'Private', 'Suspicious', '8,642', '184.2 MB', '48', '4 sec ago'],
  ['192.168.1.1', 'Private', 'Clean', '4,218', '91.7 MB', '4', '1 sec ago'],
  ['10.0.0.42', 'Private', 'Malicious', '2,741', '58.4 MB', '82', '12 sec ago'],
  ['172.217.14.206', 'Public', 'Clean', '1,882', '42.1 MB', '0', '5 sec ago'],
  ['45.33.32.156', 'Public', 'Suspicious', '486', '2.8 MB', '64', '16 sec ago'],
  ['224.0.0.251', 'Multicast', 'Clean', '312', '184 KB', '0', '28 sec ago'],
]

function LineChart({ entropy = false }: { entropy?: boolean }) {
  return <div className={`chart-wrap ${entropy ? 'entropy-chart' : ''}`}>
    <div className="y-axis"><span>{entropy ? '8.0' : '120'}</span><span>{entropy ? '6.0' : '80'}</span><span>{entropy ? '4.0' : '40'}</span><span>0</span></div>
    <div className="plot">
      <div className="grid-lines"><i/><i/><i/><i/></div>
      {entropy && <div className="threshold"><span>7.2 threshold</span></div>}
      <svg viewBox="0 0 800 210" preserveAspectRatio="none" aria-label={entropy ? 'Entropy trend' : 'Network traffic trend'}>
        <defs><linearGradient id="area" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#19b89a" stopOpacity=".28"/><stop offset="1" stopColor="#19b89a" stopOpacity="0"/></linearGradient></defs>
        <path className="area" d={entropy ? 'M0 170 C80 120 100 80 170 105 S250 40 320 72 S420 48 480 66 S580 36 650 55 S730 26 800 38 V210H0Z' : 'M0 158 C50 140 85 160 130 120 S205 130 250 105 S335 48 380 88 S470 120 520 64 S620 74 670 42 S755 68 800 34 V210H0Z'} />
        <path className="line primary" d={entropy ? 'M0 170 C80 120 100 80 170 105 S250 40 320 72 S420 48 480 66 S580 36 650 55 S730 26 800 38' : 'M0 158 C50 140 85 160 130 120 S205 130 250 105 S335 48 380 88 S470 120 520 64 S620 74 670 42 S755 68 800 34'} />
        {!entropy && <path className="line secondary" d="M0 184 C70 166 110 180 155 152 S250 168 300 130 S390 155 440 122 S540 142 590 104 S690 126 735 91 S780 100 800 78" />}
      </svg>
      <div className="x-axis"><span>14:00</span><span>14:08</span><span>14:16</span><span>14:24</span><span>14:32</span></div>
    </div>
  </div>
}

function ProtocolBars() {
  const data = [['TCP', 62, '11,428'], ['UDP', 21, '3,872'], ['ICMP', 8, '1,475'], ['ARP', 5, '922'], ['Other', 4, '735']]
  return <div className="protocol-list">{data.map(([n, p, c], i) => <div className="protocol-row" key={n}><div className="protocol-meta"><span><i className={`dot d${i}`} />{n}</span><b>{p}%</b></div><div className="bar"><i style={{ width: `${p}%` }} /></div><small>{c} packets</small></div>)}</div>
}

function TopologyGraph({ large = false }: { large?: boolean }) {
  const nodes = [
    ['gateway', 48, 48, '192.168.1.1', 'good'],
    ['host', 24, 26, '192.168.1.24', 'warn'],
    ['host', 25, 74, '10.0.0.42', 'danger'],
    ['external', 73, 20, '172.217.14.206', 'good'],
    ['external', 78, 55, '185.199.108.133', 'warn'],
    ['host', 70, 82, '192.168.1.31', 'good'],
  ]
  return <div className={`topology ${large ? 'large' : ''}`}>
    <svg viewBox="0 0 100 100" preserveAspectRatio="none"><line x1="48" y1="48" x2="24" y2="26"/><line x1="48" y1="48" x2="25" y2="74" className="risk"/><line x1="48" y1="48" x2="73" y2="20"/><line x1="48" y1="48" x2="78" y2="55"/><line x1="48" y1="48" x2="70" y2="82"/><line x1="25" y1="74" x2="78" y2="55" className="risk"/></svg>
    {nodes.map(([type, x, y, label, tone]) => <div key={label} className={`node ${type} ${tone}`} style={{ left: `${x}%`, top: `${y}%` }}><span><Icon name={type === 'gateway' ? 'network' : 'server'} size={large ? 20 : 15}/></span><label>{label}</label></div>)}
    {large && <div className="graph-tools"><Button icon="search" kind="ghost"/><Button icon="sliders" kind="ghost"/><Button kind="ghost">Reset</Button></div>}
  </div>
}

function PageHeader({ id }: { id: PageId }) {
  return <div className="page-heading"><div><div className="breadcrumbs">NetScope <Icon name="chevron" size={12}/> {pageMeta[id][0]}</div><h1>{pageMeta[id][0]}</h1><p>{pageMeta[id][1]}</p></div><div className="page-actions"><Badge tone="purple">Sample data</Badge>{(id === 'overview' || id === 'live') && <><Button icon="pause">Pause view</Button><Button icon="sliders" kind="primary">Capture settings</Button></>}</div></div>
}

function Overview() {
  return <>
    <div className="capture-strip"><div><span className="pulse"/><b>Demo capture active</b><span>Simulated traffic · 42 packets/sec</span></div><div><Icon name="clock" size={15}/> Updated just now <Button icon="pause" kind="ghost">Pause view</Button></div></div>
    <div className="metrics six">
      <Metric label="Total packets" value="18,432" detail="+12.4% this session" bars={[24,35,29,52,46,64,76,68]} />
      <Metric label="Packets per second" value="42.8" detail="Peak 96.2 pps" tone="blue" bars={[20,36,44,34,68,55,80,72]} />
      <Metric label="Network throughput" value="6.24" unit="Mbps" detail="↑ 1.8 Mbps" />
      <Metric label="Active hosts" value="24" detail="6 external hosts" />
      <Metric label="Security alerts" value="12" detail="3 high severity" tone="orange" bars={[12,28,20,46,22,68,48,36]} />
      <Metric label="Encrypted traffic" value="78.4" unit="%" detail="14,450 packets" />
    </div>
    <div className="dashboard-grid">
      <Card title="Network traffic overview" className="traffic-card" action={<div className="segmented"><button className="active">1H</button><button>6H</button><button>24H</button></div>}><div className="legend"><span><i className="teal"/>Incoming</span><span><i className="blue"/>Outgoing</span><b>Current 6.24 Mbps</b></div><LineChart /></Card>
      <Card title="Protocol distribution" action={<Button icon="more" kind="ghost"/>}><ProtocolBars /></Card>
      <Card title="Network topology" className="topology-card" action={<Button kind="ghost">Open explorer <Icon name="chevron" size={13}/></Button>}><TopologyGraph /></Card>
      <Card title="Threat posture"><div className="posture"><div className="risk-ring"><b>24</b><span>hosts</span></div><div className="posture-list"><span><i className="clean"/>Clean <b>19</b></span><span><i className="suspicious"/>Suspicious <b>4</b></span><span><i className="malicious"/>Malicious <b>1</b></span></div></div><p className="callout warn"><Icon name="alert" size={16}/><span>10.0.0.42 has exceeded the malicious threshold with a score of 82.</span></p></Card>
      <Card title="Recent security alerts" className="wide-card" action={<Button kind="ghost">View all <Icon name="chevron" size={13}/></Button>}><AlertsTable compact /></Card>
      <Card title="Top communicating hosts"><HostMini /></Card>
      <Card title="Recent packet activity" className="full-card" action={<Button kind="ghost">Open Packet Explorer <Icon name="chevron" size={13}/></Button>}><PacketTable compact /></Card>
    </div>
  </>
}

function PacketTable({ compact = false, onSelect }: { compact?: boolean; onSelect?: (id: string) => void }) {
  return <div className="table-scroll"><table className="data-table packet-table"><thead><tr>{['No.','Time','Protocol','Source','Src Port','Destination','Dst Port','Length','Flags','Information'].map(x => <th key={x}>{x}</th>)}</tr></thead><tbody>{packets.slice(0, compact ? 5 : 8).map((r, i) => <tr key={r[0]} className={i === 0 && !compact ? 'selected' : ''} onClick={() => onSelect && onSelect(r[0])}>{r.map((c, ci) => <td key={ci} className={ci === 2 ? `protocol p-${c.toLowerCase()}` : ''}>{c}</td>)}</tr>)}</tbody></table></div>
}

function AlertsTable({ compact = false }: { compact?: boolean }) {
  return <div className="table-scroll"><table className="data-table"><thead><tr>{['Severity','Detection type','Source IP','Destination','Description','Time'].map(x => <th key={x}>{x}</th>)}</tr></thead><tbody>{alerts.slice(0, compact ? 3 : 5).map(r => <tr key={r[5]}>{r.map((c, i) => <td key={i}>{i === 0 ? <Badge tone={c === 'High' ? 'danger' : c === 'Suspicious' ? 'warn' : 'info'}>{c}</Badge> : c}</td>)}</tr>)}</tbody></table></div>
}

function HostMini() {
  return <div className="host-mini">{hosts.slice(0,4).map((h,i) => <div key={h[0]}><span className="host-rank">{i+1}</span><span><b>{h[0]}</b><small>{h[4]} transferred</small></span><span className={`score ${Number(h[5]) >= 70 ? 'danger' : Number(h[5]) >= 25 ? 'warn' : 'good'}`}>{h[5]}</span></div>)}</div>
}

function Toolbar({ search = 'Search…', filters = ['All protocols', 'Any source', 'Any destination'] }: { search?: string; filters?: string[] }) {
  return <div className="toolbar"><label className="search"><Icon name="search" size={16}/><input placeholder={search}/><kbd>⌘ K</kbd></label>{filters.map(f => <button className="select-btn" key={f}>{f}<span>⌄</span></button>)}<Button icon="filter">Filters</Button></div>
}

function LiveTraffic() {
  const [paused, setPaused] = useState(false)
  const [selectedPkt, setSelectedPkt] = useState('18432')
  return <>
    <div className="capture-strip"><div><span className="pulse"/><b>Demo capture active</b><span>Simulated traffic · 42 packets/sec</span></div><div><Icon name="clock" size={15}/> Updated just now <Button icon="pause" kind="ghost" onClick={() => setPaused(!paused)}>{paused ? 'Resume' : 'Pause'}</Button></div></div>
    <div className="metrics four"><Metric label="Total packets" value="18,432" detail="Capture duration 00:42:18"/><Metric label="Current packet rate" value="42.8" unit="pps" detail="Peak 96.2 pps"/><Metric label="Throughput" value="6.24" unit="Mbps" detail="In 4.1 · Out 2.1"/><Metric label="Active hosts" value="24" detail="18 local · 6 external"/></div>
    <Card title="Real-time throughput" action={<div className="actions"><Button icon={paused ? 'play' : 'pause'} onClick={() => setPaused(!paused)}>{paused ? 'Resume view' : 'Pause view'}</Button><Button kind="ghost">Reset</Button></div>}><div className="legend"><span><i className="teal"/>Incoming</span><span><i className="blue"/>Outgoing</span>{paused && <Badge tone="warn">Visualization paused · capture continues</Badge>}</div><LineChart /></Card>
    
    <Card title="Live Packet Stream & Inspection" style={{ marginTop: '12px' }}>
      <Toolbar search="Filter stream by IP, port or protocol…" filters={['All protocols', 'TCP', 'UDP', 'DNS']} />
      <div className="packet-workspace" style={{ padding: '0 14px 14px' }}>
        <Card className="packet-list"><PacketTable onSelect={(id) => setSelectedPkt(id)} /></Card>
        <Card className="inspector" title={`Packet ${selectedPkt}`} action={<Button icon="x" kind="ghost"/>}>
          <div className="inspector-summary"><Badge tone="info">TCP</Badge><span><b>1,428</b> bytes</span><span><Icon name="clock" size={14}/>14:32:08.241</span></div>
          <InspectSection title="Packet summary" rows={[['Source','192.168.1.24:52418'],['Destination','172.217.14.206:443'],['Protocol','TCP / TLS'],['Frame length','1,428 bytes']]}/>
          <InspectSection title="Network layer · IPv4" rows={[['Source IP','192.168.1.24 (Private)'],['Destination IP','172.217.14.206 (Public)'],['TTL','64'],['Header length','20 bytes']]}/>
          <InspectSection title="Transport layer · TCP" rows={[['Source port','52418'],['Destination port','443 (HTTPS)'],['TCP flags','PSH, ACK'],['Sequence','184923901']]}/>
          <InspectSection title="Security findings" rows={[['Encryption','TLS signature detected'],['Source host','Suspicious · Score 48'],['Related alerts','None for this packet']]}/>
        </Card>
      </div>
    </Card>

    <div className="grid-3"><Card title="Protocol distribution"><ProtocolBars/></Card><Card title="Top source addresses"><HostMini/></Card><Card title="Packet size distribution"><div className="histogram">{[35,62,85,48,30,20,14,8].map((v,i)=><i key={i} style={{height:`${v}%`}}><span>{i === 0 ? '64' : i === 3 ? '512' : i === 7 ? '1500' : ''}</span></i>)}</div></Card></div>
  </>
}

function PacketExplorer() {
  return <>
    <Toolbar search="Filter packets (e.g. ip:192.168.1.10)" filters={['All protocols','Source IP','Destination IP','Port']}/>
    <div className="filter-help"><span>18,432 packets</span><span>Syntax:</span><code>ip:192.168.1.10</code><code>proto:tcp</code><code>port:443</code><code>enc:true</code><Button icon="x" kind="ghost">Clear filters</Button></div>
    <div className="packet-workspace">
      <Card className="packet-list"><PacketTable/></Card>
      <Card className="inspector" title="Packet 18432" action={<Button icon="x" kind="ghost"/>}>
        <div className="inspector-summary"><Badge tone="info">TCP</Badge><span><b>1,428</b> bytes</span><span><Icon name="clock" size={14}/>14:32:08.241</span></div>
        <InspectSection title="Packet summary" rows={[['Source','192.168.1.24:52418'],['Destination','172.217.14.206:443'],['Protocol','TCP / TLS'],['Frame length','1,428 bytes']]}/>
        <InspectSection title="Network layer · IPv4" rows={[['Source IP','192.168.1.24 (Private)'],['Destination IP','172.217.14.206 (Public)'],['TTL','64'],['Header length','20 bytes']]}/>
        <InspectSection title="Transport layer · TCP" rows={[['Source port','52418'],['Destination port','443 (HTTPS)'],['TCP flags','PSH, ACK'],['Sequence','184923901']]}/>
        <InspectSection title="Security findings" rows={[['Encryption','TLS signature detected'],['Source host','Suspicious · Score 48'],['Related alerts','None for this packet']]}/>
      </Card>
    </div>
  </>
}

function InspectSection({ title, rows }: { title: string; rows: string[][] }) {
  return <details open><summary><span>⌄</span>{title}</summary><div className="detail-rows">{rows.map(r=><div key={r[0]}><span>{r[0]}</span><code>{r[1]}</code></div>)}</div></details>
}

function TopologyPage() {
  return <div className="topology-workspace"><Card className="graph-card" title="Communication graph" action={<div className="actions"><label className="search small"><Icon name="search" size={15}/><input placeholder="Find host"/></label><Button kind="ghost">Last 15 min</Button></div>}><TopologyGraph large/><div className="graph-legend"><span><i className="clean"/>Clean</span><span><i className="suspicious"/>Suspicious</span><span><i className="malicious"/>Malicious</span><span>Line width = traffic volume</span></div></Card><Card className="host-panel" title="Selected host"><div className="host-avatar danger"><Icon name="server" size={24}/></div><h2>10.0.0.42</h2><p>Private IPv4 address</p><div className="big-score"><span>Threat score</span><b>82</b><div><i style={{width:'82%'}}/></div><Badge tone="danger">Malicious</Badge></div><InspectSection title="Activity" rows={[['Packets','2,741'],['Traffic','58.4 MB'],['First seen','13:49:52'],['Last seen','12 sec ago']]}/><InspectSection title="Relationships" rows={[['Communicates with','6 hosts'],['External hosts','2'],['Top destination','185.199.108.133']]}/><p className="callout warn"><Icon name="alert" size={16}/><span>Classification is based on heuristic detections and does not confirm compromise.</span></p></Card></div>
}

function HostInventory() {
  return <><div className="metrics four"><Metric label="Total hosts" value="24" detail="6 external"/><Metric label="Clean" value="19" detail="Score below 25"/><Metric label="Suspicious" value="4" detail="Score 25–69"/><Metric label="Malicious" value="1" detail="Score 70+"/></div><Toolbar search="Search IP address…" filters={['All classifications','All address types','Last observed']}/><Card><div className="table-scroll"><table className="data-table"><thead><tr>{['IP address','Address type','Classification','Packets','Traffic volume','Threat score','Last observed','Status'].map(x=><th key={x}>{x}</th>)}</tr></thead><tbody>{hosts.map(h=><tr key={h[0]}>{h.map((c,i)=><td key={i}>{i===2?<Badge tone={c==='Malicious'?'danger':c==='Suspicious'?'warn':'good'}>{c}</Badge>:i===5?<span className={`score ${Number(c)>=70?'danger':Number(c)>=25?'warn':'good'}`}>{c}</span>:c}</td>)}<td><span className="online"/>Active</td></tr>)}</tbody></table></div><div className="pagination"><span>Showing 1–6 of 24 hosts</span><div><Button disabled>Previous</Button><Button>Next</Button></div></div></Card></>
}

function Threats() {
  return <><div className="metrics four"><Metric label="Hosts tracked" value="24" detail="Current session"/><Metric label="Suspicious hosts" value="4" detail="16.7% of hosts"/><Metric label="Malicious hosts" value="1" detail="Heuristic classification"/><Metric label="Highest risk host" value="82" detail="10.0.0.42"/></div><div className="two-column"><Card title="Host threat leaderboard" className="main"><div className="leaderboard">{hosts.slice().sort((a,b)=>Number(b[5])-Number(a[5])).map((h,i)=><div key={h[0]}><span className="rank">{String(i+1).padStart(2,'0')}</span><span><b>{h[0]}</b><small>{h[2]} · {i+1} heuristic detection{!i?'s':''}</small></span><div className="riskbar"><i style={{width:`${h[5]}%`}}/></div><strong>{h[5]}</strong></div>)}</div></Card><Card title="Risk classification"><div className="threshold-list"><div><Badge tone="good">Clean</Badge><b>0–24</b><p>No significant suspicious behavior observed.</p></div><div><Badge tone="warn">Suspicious</Badge><b>25–69</b><p>One or more heuristic indicators require review.</p></div><div><Badge tone="danger">Malicious</Badge><b>70–100</b><p>Multiple or heavily weighted indicators observed.</p></div></div><p className="callout info"><Icon name="shield" size={16}/><span>Scores decay over time. A high score prioritizes investigation; it does not prove compromise.</span></p></Card></div></>
}

function SecurityAlerts() {
  return <><div className="metrics four"><Metric label="Total alerts" value="12" detail="Current session"/><Metric label="High severity" value="3" detail="Requires review"/><Metric label="Suspicious" value="7" detail="Heuristic findings"/><Metric label="Informational" value="2" detail="Context only"/></div><Toolbar search="Search alerts…" filters={['All severities','All detection types','Any time']}/><Card title="Detections" action={<Button icon="download">Export JSON</Button>}><AlertsTable/></Card><p className="page-note"><Icon name="alert" size={16}/> NetScope detections identify patterns that may be suspicious. They should be validated before being treated as confirmed attacks.</p></>
}

function Encryption() {
  return <><div className="metrics five"><Metric label="Encrypted payloads" value="14,450" detail="Detected or inferred"/><Metric label="Traffic percentage" value="78.4" unit="%" detail="+4.2% this session"/><Metric label="Average entropy" value="7.14" detail="bits per byte"/><Metric label="Recent entropy" value="7.62" detail="Latest payload"/><Metric label="High entropy" value="9,842" detail="Above 7.2"/></div><div className="two-column entropy-layout"><Card title="Payload entropy over time" className="main"><LineChart entropy/><p className="callout info"><Icon name="lock" size={16}/><span>High entropy can indicate encrypted or compressed data. It is not conclusive proof of encryption.</span></p></Card><Card title="Detection methods"><div className="method-list">{[['TLS / SSL signatures','8,942'],['Shannon entropy','4,182'],['SSH banners','486'],['Port-based inference','428'],['Base64 heuristic','312'],['AES-GCM heuristic','100']].map(x=><div key={x[0]}><span>{x[0]}</span><b>{x[1]}</b></div>)}</div></Card></div><Card title="Recent findings"><div className="table-scroll"><table className="data-table"><thead><tr>{['Time','Source','Destination','Dst port','Detection method','Packet size'].map(x=><th key={x}>{x}</th>)}</tr></thead><tbody>{packets.slice(0,5).map((p,i)=><tr key={i}><td>{p[1]}</td><td>{p[3]}</td><td>{p[5]}</td><td>{p[6]}</td><td>{i===3?'High entropy':'TLS signature'}</td><td>{p[7]} bytes</td></tr>)}</tbody></table></div></Card></>
}

function ProtocolAnalytics() {
  const tabs=['Overview','TCP','UDP','ICMP','ARP','DNS','DHCP','HTTP','HTTPS','SSH','FTP']
  const [tab,setTab]=useState('Overview')
  return <><div className="tabs">{tabs.map(t=><button key={t} className={t===tab?'active':''} onClick={()=>setTab(t)}>{t}</button>)}</div><div className="metrics four"><Metric label={`${tab === 'Overview' ? 'TCP' : tab} packets`} value={tab==='Overview'?'11,428':'2,842'} detail="62.0% of packets"/><Metric label="Traffic volume" value="194.2" unit="MB" detail="68.4% of traffic"/><Metric label="Top service" value="HTTPS" detail="Port 443"/><Metric label="Unique endpoints" value="18" detail="4 external"/></div><div className="grid-2"><Card title="Protocol traffic trend"><LineChart/></Card><Card title="Protocol distribution"><ProtocolBars/></Card></div><div className="grid-2"><Card title="Top services"><div className="method-list">{[['HTTPS · 443','8,942'],['DNS · 53','1,284'],['SSH · 22','486'],['HTTP · 80','412'],['mDNS · 5353','312']].map(x=><div key={x[0]}><span>{x[0]}</span><b>{x[1]} packets</b></div>)}</div></Card><Card title="Top destination ports"><div className="horizontal-bars">{[['443',85],['53',48],['22',29],['80',24],['5353',18]].map(x=><div key={x[0]}><code>{x[0]}</code><span><i style={{width:`${x[1]}%`}}/></span><b>{x[1]}%</b></div>)}</div></Card></div></>
}

function Flows() {
  return <><div className="metrics four"><Metric label="Active connections" value="18" detail="Estimated"/><Metric label="Total connections" value="286" detail="Current session"/><Metric label="TCP retransmissions" value="42" detail="0.36% of TCP"/><Metric label="Top flows" value="10" detail="72% of traffic"/></div><Toolbar search="Search source or destination…" filters={['All protocols','Connection state','Last 15 min']}/><Card><div className="table-scroll"><table className="data-table"><thead><tr>{['Source IP','Destination IP','Protocol','Src port','Dst port','Packets','Bytes','Connection'].map(x=><th key={x}>{x}</th>)}</tr></thead><tbody>{packets.slice(0,7).map((p,i)=><tr key={i}><td>{p[3]}</td><td>{p[5]}</td><td><Badge tone="info">{p[2]}</Badge></td><td>{p[4]}</td><td>{p[6]}</td><td>{[842,484,392,244,198,164,120][i]}</td><td>{['82.4 MB','42.1 MB','28.8 MB','12.4 MB','8.2 MB','4.8 MB','2.1 MB'][i]}</td><td>{i===5?'SYN sent':'Established'}</td></tr>)}</tbody></table></div></Card></>
}

function Reports() {
  return <><div className="report-hero"><div><span className="report-icon"><Icon name="report" size={26}/></span><div><h2>Current session report</h2><p>Analysis summary for demo capture started today at 13:49.</p></div></div><div className="actions"><Button icon="download">Export JSON</Button><Button icon="download" kind="primary">Export HTML</Button></div></div><div className="report-grid">{[['Session summary','42m 18s','18,432 packets analyzed'],['Traffic statistics','312.8 MB','6.24 Mbps current'],['Protocol breakdown','10 protocols','TCP is 62% of traffic'],['Security findings','12 alerts','3 high severity'],['Encryption findings','78.4%','14,450 encrypted payloads'],['Top communicating hosts','24 hosts','192.168.1.24 is most active']].map((x,i)=><Card key={x[0]}><div className="report-card"><span><Icon name={(['clock','activity','chart','shield','lock','server'] as IconName[])[i]} size={20}/></span><div><h3>{x[0]}</h3><b>{x[1]}</b><p>{x[2]}</p></div><Icon name="chevron" size={16}/></div></Card>)}</div><p className="page-note"><Icon name="clock" size={16}/> Reports summarize the active analysis session. NetScope does not store a cloud report history.</p></>
}

function CaptureConfig() {
  const [mode,setMode]=useState('Demo / Simulated Traffic')
  const modes=[['Live Capture','Capture directly from a network interface.','radio'],['Demo / Simulated Traffic','Generate realistic traffic for exploration.','activity'],['Offline PCAP Analysis','Analyze a local capture file.','upload']] as [string,string,IconName][]
  return <><div className="mode-grid">{modes.map(m=><button key={m[0]} className={`mode-card ${mode===m[0]?'active':''}`} onClick={()=>setMode(m[0])}><span><Icon name={m[2]} size={22}/></span><div><b>{m[0]}</b><p>{m[1]}</p></div><i className="radio-select"/></button>)}</div><div className="config-layout"><Card title={mode} className="config-form">{mode==='Live Capture'?<><Field label="Network interface" value="eth0"/><Field label="BPF packet filter" value="tcp or udp"/><div className="field-row"><Field label="Packet count" value="0 (unlimited)"/><Field label="Timeout" value="60 seconds"/></div><Toggle label="Save output PCAP" detail="Write captured packets to a local file"/><p className="callout warn"><Icon name="alert" size={16}/><span>Live packet capture requires appropriate operating-system permissions and explicit backend configuration.</span></p><Button icon="play" kind="primary">Start live capture</Button></>:mode==='Offline PCAP Analysis'?<><div className="dropzone"><Icon name="upload" size={28}/><b>Select a PCAP file</b><p>Choose a .pcap or .pcapng file available to the analysis engine.</p><Button>Choose file</Button></div><Field label="BPF analysis filter (optional)" value="No filter"/><Button icon="play" kind="primary">Start analysis</Button></>:<><Field label="Packets per second" value="42"/><Toggle label="Include simulated security events" detail="Generate representative heuristic findings"/><p className="callout info"><Icon name="activity" size={16}/><span>The standard hosted backend uses simulated traffic. All generated data is labeled as sample data.</span></p><div className="actions"><Button icon="x">Stop demo</Button><Button icon="play" kind="primary">Restart demo</Button></div></>}</Card><Card title="Capture status"><div className="capture-status"><span className="status-orb"><Icon name="activity" size={26}/></span><Badge tone="good">Running</Badge><h3>Demo capture active</h3><p>Simulated traffic at 42 packets per second.</p><div><span>Duration <b>00:42:18</b></span><span>Packets <b>18,432</b></span><span>Output <b>Not saved</b></span></div></div></Card></div></>
}

function Field({ label, value }: { label:string; value:string }) { return <label className="field"><span>{label}</span><input defaultValue={value}/></label> }
function Toggle({ label, detail, checked=true }: { label:string; detail:string; checked?:boolean }) { return <label className="toggle-row"><span><b>{label}</b><small>{detail}</small></span><input type="checkbox" defaultChecked={checked}/><i/></label> }

function Settings() {
  return <div className="settings-layout"><aside>{['Appearance','Connection','Display preferences','Charts','Accessibility','About NetScope'].map((x,i)=><button className={i===0?'active':''} key={x}>{x}</button>)}</aside><div><Card title="Appearance"><div className="theme-options"><button className="active"><span className="theme-preview dark"/><b>Dark</b><i/></button><button><span className="theme-preview light"/><b>Light</b><i/></button><button><span className="theme-preview system"/><b>System</b><i/></button></div></Card><Card title="Connection"><Field label="Backend WebSocket URL" value="wss://netscope-backend.onrender.com/ws"/><Toggle label="Reconnect automatically" detail="Retry if the backend connection is interrupted"/><Toggle label="Show connection notifications" detail="Display a message when status changes"/></Card><Card title="Display preferences"><div className="field-row"><Field label="Table density" value="Compact"/><Field label="Default time range" value="Last 1 hour"/></div><Toggle label="Show technical timestamps" detail="Use 24-hour timestamps with milliseconds"/><Toggle label="Reduced motion" detail="Minimize non-essential interface animation" checked={false}/></Card><div className="save-bar"><span><Icon name="check" size={16}/> Preferences saved locally</span><Button kind="primary">Save changes</Button></div></div></div>
}

function Docs() {
  return <div className="docs-layout"><Card title="NetScope documentation"><div className="docs-list">{['Getting started','Capture modes','Packet filters','Threat scoring','Detection reference','Encryption heuristics','Reports and exports'].map((x,i)=><button key={x} className={i===0?'active':''}><Icon name={i<3?'book':'chevron'} size={16}/>{x}<Icon name="chevron" size={14}/></button>)}</div></Card><Card><article><Badge tone="info">Getting started</Badge><h2>Understand your network activity</h2><p>NetScope combines packet capture, protocol dissection and heuristic security analysis in a single investigation workspace.</p><h3>Choose a capture mode</h3><p>Use simulated traffic to explore the interface, live capture when the backend has operating-system permissions, or analyze an existing PCAP file available to the engine.</p><h3>Interpret findings carefully</h3><p>Security alerts and host scores are heuristic indicators. They help prioritize investigation but do not confirm malicious activity or compromise.</p><div className="callout info"><Icon name="shield" size={18}/><span><b>Threat scoring thresholds</b><br/>Clean: below 25 · Suspicious: 25–69 · Malicious: 70 and above</span></div></article></Card></div>
}

function GenericPage({ id }: { id: PageId }) {
  if (id==='overview') return <Overview/>
  if (id==='live') return <LiveTraffic/>
  if (id==='packets') return <PacketExplorer/>
  if (id==='topology') return <TopologyPage/>
  if (id==='hosts') return <HostInventory/>
  if (id==='flows') return <Flows/>
  if (id==='threats') return <Threats/>
  if (id==='alerts') return <SecurityAlerts/>
  if (id==='encryption') return <Encryption/>
  if (id==='protocols') return <ProtocolAnalytics/>
  if (id==='reports') return <Reports/>
  if (id==='capture') return <CaptureConfig/>
  if (id==='settings') return <Settings/>
  return <Docs/>
}

export default function App() {
  const [page,setPage]=useState<PageId>('live')
  const [collapsed,setCollapsed]=useState(false)
  const [mobileOpen,setMobileOpen]=useState(false)
  const [theme,setTheme]=useState<'dark'|'light'>('dark')
  const current = useMemo(()=>nav.flatMap(n=>n.items).find(x=>x.id===page),[page])
  const navigate=(id:PageId)=>{setPage(id);setMobileOpen(false);window.scrollTo(0,0)}
  return <div className={`app ${theme} ${collapsed?'collapsed':''}`}>
    <aside className={`sidebar ${mobileOpen?'mobile-open':''}`}>
      <div className="brand" onClick={() => collapsed && setCollapsed(false)}>
        {collapsed ? (
          <img src={theme === 'dark' ? '/NetScope_Short_Icon_Dark_Mode.png' : '/NetScope_Short_Icon_Light_Mode.png'} alt="NetScope" width={32} height={32} style={{ objectFit: 'contain' }} />
        ) : (
          <img src={theme === 'dark' ? '/NetScope_Full_Logo_Dark_Mode.png' : '/NetScope_Full_Logo_Light_Mode.png'} alt="NetScope" height={28} style={{ objectFit: 'contain', maxWidth: 150 }} />
        )}
        <button className="collapse" onClick={(e) => { e.stopPropagation(); setCollapsed(!collapsed); }} aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}>
          <Icon name="chevron" size={16}/>
        </button>
      </div>
      <nav>{nav.map(group=><div className="nav-group" key={group.label}><label>{group.label}</label>{group.items.map(item=><button title={item.name} key={item.id} className={page===item.id?'active':''} onClick={()=>navigate(item.id)}><Icon name={item.icon}/><span>{item.name}</span>{item.id==='alerts'&&<em>12</em>}</button>)}</div>)}</nav>
      <div className="connection"><div><span className="online"/><b>Backend connected</b></div><p>Demo mode · 42 pps</p></div>
    </aside>
    {mobileOpen&&<button className="backdrop" onClick={()=>setMobileOpen(false)} aria-label="Close navigation"/>}
    <div className="main-shell">
      <header className="topbar"><div className="top-left"><button className="mobile-menu" onClick={()=>setMobileOpen(true)}><Icon name="grid"/></button><div className="current-icon"><Icon name={current?.icon||'grid'}/></div><b>{pageMeta[page][0]}</b></div><label className="global-search"><Icon name="search" size={16}/><input placeholder="Search packets, hosts or alerts"/><kbd>⌘ K</kbd></label><div className="top-actions"><Badge tone="good">Connected</Badge><Badge tone="purple">Demo mode</Badge><button aria-label="Notifications" className="icon-btn"><Icon name="bell"/><i/></button><button aria-label="Toggle theme" className="icon-btn" onClick={()=>setTheme(theme==='dark'?'light':'dark')}><Icon name="sun"/></button><button aria-label="Settings" className="icon-btn" onClick={()=>navigate('settings')}><Icon name="settings"/></button></div></header>
      <main><PageHeader id={page}/><GenericPage id={page}/><footer><span>NetScope · Network observability and packet analysis</span><span>Backend connected · v1.0</span></footer></main>
    </div>
  </div>
}
