import { useEffect, useMemo, useState, type Dispatch, type FormEvent, type ReactNode, type SetStateAction } from "react";
import { Link, NavLink, Route, Routes, useLocation, useNavigate } from "react-router-dom";
import {
  Activity, AlertTriangle, ArrowDownRight, ArrowUpRight, BarChart3, Bell, BrainCircuit, Calculator,
  Check, CheckCircle2, ChevronDown, CircleDollarSign, Download, Factory, FileText, Gauge, Leaf,
  Lightbulb, Menu, Plus, Recycle, Route as RouteIcon, Search, Settings, SlidersHorizontal, Sparkles,
  Target, Truck, Upload, X, Zap
} from "lucide-react";
import { initialRoadmap, formatINR, recommendations, sources, trend, type Recommendation, type RoadmapItem } from "./data";
import { calculateEmissionIntensity, calculateScenario } from "./utils";
import { clearAccessToken, createEnergyUsage, createFactory, createMaterialUsage, createReportingPeriod, createRoadmapAction, createTransportationActivity, createWasteRecord, downloadCalculationCsv, fetchAnomalies, fetchCalculation, fetchDashboard, fetchFactories, fetchHotspots, fetchRecommendations, fetchRoadmap, fetchRoadmapActions, login, register, simulateCalculation, updateFactory, updateRoadmapAction, type ApiCalculation, type ApiHotspot, type DashboardResponse, type Factory as ApiFactory, type ApiRoadmap } from "./api";

const pageNames: Record<string, string> = {
  "/dashboard": "Overview", "/factory-data": "Factory data", "/emissions": "Emissions analysis",
  "/hotspots": "Emission hotspots", "/recommendations": "Circular recommendations", "/simulator": "What-if simulator",
  "/roadmap": "Action roadmap", "/reports": "Reports", "/settings": "Settings",
};

function Button({ children, variant = "primary", onClick, type = "button" }: { children: ReactNode; variant?: "primary" | "secondary" | "ghost"; onClick?: () => void; type?: "button" | "submit" }) {
  return <button type={type} className={`button button-${variant}`} onClick={onClick}>{children}</button>;
}
function Card({ children, className = "" }: { children: ReactNode; className?: string }) { return <section className={`card ${className}`}>{children}</section>; }
function Badge({ children, tone = "neutral" }: { children: ReactNode; tone?: "neutral" | "red" | "amber" | "green" | "blue" }) { return <span className={`badge badge-${tone}`}>{children}</span>; }
function SectionTitle({ eyebrow, title, detail, action }: { eyebrow?: string; title: string; detail?: string; action?: ReactNode }) {
  return <div className="section-title"><div>{eyebrow && <div className="eyebrow">{eyebrow}</div>}<h2>{title}</h2>{detail && <p>{detail}</p>}</div>{action}</div>;
}
function MiniBars({ values, color = "#16845b" }: { values: number[]; color?: string }) {
  const max = Math.max(...values); return <div className="mini-bars" aria-hidden="true">{values.map((v, i) => <span key={i} style={{ height: `${Math.max(18, v / max * 100)}%`, background: color }} />)}</div>;
}
function Sparkline({ values, color = "#16845b" }: { values: number[]; color?: string }) {
  const max = Math.max(...values), min = Math.min(...values), points = values.map((v, i) => `${i * (100 / (values.length - 1))},${100 - ((v - min) / (max - min || 1)) * 82 - 9}`).join(" ");
  return <svg className="sparkline" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true"><polyline points={points} fill="none" stroke={color} strokeWidth="5" vectorEffect="non-scaling-stroke" /></svg>;
}

function Donut({ items = sources, selected, onSelect, totalLabel = "10,000" }: { items?: typeof sources; selected?: string; onSelect?: (name: string) => void; totalLabel?: string }) {
  const total = items.reduce((sum, item) => sum + item.value, 0); let offset = 0;
  return <div className="donut-wrap"><svg viewBox="0 0 42 42" className="donut" role="img" aria-label="Emissions by source">
    <circle cx="21" cy="21" r="15.9" fill="none" stroke="#e8eee9" strokeWidth="7" />
    {items.map((item) => { const dash = item.value / total * 100; const el = <circle key={item.name} className="donut-segment" cx="21" cy="21" r="15.9" fill="none" stroke={item.color} strokeWidth={selected === item.name ? 8 : 7} strokeDasharray={`${dash} ${100 - dash}`} strokeDashoffset={-offset} onClick={() => onSelect?.(item.name)} />; offset += dash; return el; })}
  </svg><div className="donut-center"><strong>{totalLabel}</strong><span>kg CO₂e</span></div></div>;
}
function TrendChart({ compact = false }: { compact?: boolean }) {
  const values = trend.map((item) => item.emissions), max = 11500, min = 9500;
  const line = (key: "emissions" | "target") => trend.map((item, i) => `${i * 20},${100 - ((item[key] - min) / (max - min)) * 88}`).join(" ");
  return <div className={`trend-chart ${compact ? "compact" : ""}`}><svg viewBox="0 0 100 100" preserveAspectRatio="none"><defs><linearGradient id="area" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stopColor="#16845b" stopOpacity=".22" /><stop offset="1" stopColor="#16845b" stopOpacity="0" /></linearGradient></defs><polygon points={`0,100 ${line("emissions")} 100,100`} fill="url(#area)" /><polyline points={line("target")} fill="none" stroke="#a7b6aa" strokeDasharray="2 2" vectorEffect="non-scaling-stroke" /><polyline points={line("emissions")} fill="none" stroke="#16845b" strokeWidth="2.5" vectorEffect="non-scaling-stroke" />{trend.map((item, i) => <circle key={item.month} cx={i * 20} cy={100 - ((item.emissions - min) / (max - min)) * 88} r="1.6" fill="#16845b" />)}</svg><div className="chart-labels">{trend.map((item) => <span key={item.month}>{item.month}</span>)}</div></div>;
}

function Shell({
  children,
  roadmap,
  setRoadmap,
  factoryOptions,
  selectedFactory,
  onSelectFactory,
}: {
  children: ReactNode;
  roadmap: RoadmapItem[];
  setRoadmap: Dispatch<SetStateAction<RoadmapItem[]>>;
  factoryOptions: ApiFactory[];
  selectedFactory: ApiFactory | null;
  onSelectFactory: (factoryId: number) => void;
}) {
  const [drawer, setDrawer] = useState(false); const [search, setSearch] = useState(""); const [notifications, setNotifications] = useState(false); const location = useLocation(); const navigate = useNavigate();
  const nav = [{ to: "/dashboard", label: "Overview", icon: Gauge }, { to: "/factory-data", label: "Factory data", icon: Factory }, { to: "/emissions", label: "Emissions", icon: BarChart3 }, { to: "/hotspots", label: "Hotspots", icon: AlertTriangle }, { to: "/recommendations", label: "Recommendations", icon: Lightbulb }, { to: "/simulator", label: "What-if simulator", icon: Calculator }, { to: "/roadmap", label: "Action roadmap", icon: RouteIcon }, { to: "/reports", label: "Reports", icon: FileText }];
  const close = () => setDrawer(false);
  const logout = () => { clearAccessToken(); navigate("/"); };
  const factoryLabel = selectedFactory ?? factoryOptions[0] ?? null;
  return <div className="app-shell"><aside className={`sidebar ${drawer ? "sidebar-open" : ""}`}><div className="brand"><span className="brand-mark"><Leaf size={19} /></span><span>EcoTrace <b>AI</b></span><button className="mobile-close" onClick={close}><X size={18} /></button></div><div className="demo-pill"><span className="status-dot" /> Demo mode</div><nav>{nav.map(({ to, label, icon: Icon }) => <NavLink key={to} to={to} onClick={close} className={({ isActive }) => isActive ? "active" : ""}><Icon size={17} /><span>{label}</span>{label === "Hotspots" && <i>5</i>}</NavLink>)}</nav><div className="sidebar-spacer" /><NavLink to="/settings" onClick={close} className={({ isActive }) => isActive ? "active" : ""}><Settings size={17} /><span>Settings</span></NavLink><button className="text-link" onClick={logout}>Sign out</button><div className="factory-mini"><div className="factory-icon"><Factory size={18} /></div><div><strong>{factoryLabel?.name ?? "No factory selected"}</strong><span>{factoryLabel?.location ?? "Select a factory"}</span><small><span className="status-dot" /> Updated 2h ago</small></div>{factoryOptions.length > 1 && <select value={factoryLabel?.id ?? ""} onChange={(e) => onSelectFactory(Number(e.target.value))} aria-label="Factory selector"><option value="">Select factory</option>{factoryOptions.map((factory) => <option key={factory.id} value={factory.id}>{factory.name}</option>)}</select>}<ChevronDown size={15} /></div></aside>{drawer && <div className="overlay" onClick={close} />}<main className="main"><header className="topbar"><button className="menu-button" onClick={() => setDrawer(true)}><Menu size={21} /></button><div className="crumb"><span>{factoryLabel?.name ?? "Factory"}</span><b>/</b><strong>{pageNames[location.pathname] ?? "Overview"}</strong></div><div className="top-actions"><label className="search-box"><Search size={17} /><input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search anything" aria-label="Search" /><kbd>⌘ K</kbd></label><button className="icon-button notification-button" onClick={() => setNotifications(!notifications)} aria-label="Notifications"><Bell size={18} /><span /></button><div className="avatar">AS</div></div>{notifications && <div className="notification-panel"><div className="panel-heading"><strong>Notifications</strong><Badge tone="green">3 new</Badge></div>{["New hotspot detected in electricity", "Monthly analysis completed", "Recommendation added to roadmap"].map((text, i) => <div className="notification" key={text}><span className={`notification-dot dot-${i}`} /><div><strong>{text}</strong><small>{i + 1}h ago</small></div></div>)}<Link to="/reports" className="panel-link">View all notifications <ArrowUpRight size={14} /></Link></div>}</header><div className="content">{children}</div></main></div>;
}

function Overview({ setRoadmap, factoryId }: { setRoadmap: Dispatch<SetStateAction<RoadmapItem[]>>; factoryId: number | null }) {
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null);
  const [factory, setFactory] = useState<ApiFactory | null>(null);
  const [dashboardError, setDashboardError] = useState<string | null>(null);
  const [exportError, setExportError] = useState<string | null>(null);
  const [anomaly, setAnomaly] = useState<{ explanation: string } | null>(null);
  useEffect(() => {
    let active = true;
    const targetFactoryId = factoryId ?? null;
    const load = async () => {
      try {
        const factories = await fetchFactories();
        const selected = targetFactoryId ? factories.find((item) => item.id === targetFactoryId) ?? factories[0] : factories[0];
        if (!selected) throw new Error("No accessible factories found");
        if (active) setFactory(selected);
        const result = await fetchDashboard(selected.id);
        if (active) setDashboard(result);
        const anomalies = await fetchAnomalies(selected.id);
        if (active) setAnomaly(anomalies.find((item) => item.is_anomaly) ?? null);
      } catch (error) {
        if (active) setDashboardError(error instanceof Error ? error.message : "Unable to load live dashboard");
      }
    };
    load();
    return () => { active = false; };
  }, [factoryId]);
  const exportReport = async () => {
    setExportError(null);
    if (dashboard?.calculation_id === null || dashboard?.calculation_id === undefined) {
      setExportError("No completed calculation is available for this factory yet");
      return;
    }
    try {
      await downloadCalculationCsv(dashboard.calculation_id);
    } catch (reason) {
      setExportError(reason instanceof Error ? reason.message : "Unable to export dashboard data");
    }
  };
  const [selected, setSelected] = useState("Electricity");
  const liveSources = dashboard?.hotspots.map((hotspot, index) => ({ name: hotspot.source, value: Number(hotspot.kg_co2e), color: sources[index % sources.length].color, severity: (hotspot.severity.charAt(0).toUpperCase() + hotspot.severity.slice(1)) as "High" | "Moderate" | "Low", trend: 0 })) ?? [];
  const displaySources = liveSources.length ? liveSources : sources;
  const selectedSource = displaySources.find((s) => s.name === selected) ?? displaySources[0];
  const totalEmissions = dashboard?.total_kg_co2e ?? "10,000";
  const reductionPotential = dashboard?.recommendations.length
    ? dashboard.recommendations.reduce((sum, item) => sum + Number(item.estimated_reduction_kg_co2e), 0)
    : 2100;
  const totalRecommendationCost = dashboard?.recommendations.reduce((sum, item) => sum + Number(item.estimated_cost), 0) ?? 0;
  const carbonRoi = totalRecommendationCost > 0 ? reductionPotential / totalRecommendationCost : 0.014;
  const topHotspot = dashboard?.hotspots[0] ?? null;
  const topRecommendation = dashboard?.recommendations[0] ?? null;
  const insightTitle = topHotspot ? `${topHotspot.source} is your largest emissions hotspot.` : "Electricity is your largest emissions hotspot.";
  const insightDescription = topHotspot
    ? topHotspot.explanation || "This source is contributing the largest share of emissions and is a strong candidate for immediate reduction work."
    : "Consumption increased 11% while production grew only 4%, indicating reduced energy efficiency in production operations.";
  const insightValue = topHotspot ? Number(topHotspot.kg_co2e).toLocaleString() : "4,200";
  return <><div className="page-header"><div><Badge tone={dashboard ? "green" : "neutral"}>{dashboard ? "Live API data" : dashboardError ? "Demo data" : "Loading API data"}</Badge><h1>Good morning, here’s your emissions overview.</h1><p>{factory?.name ?? "Acme Manufacturing"} <span>•</span> {factory?.location ?? "Ahmedabad Plant"} <span>•</span> {dashboard ? `${totalEmissions} kg CO₂e from backend` : "September 2026"}</p></div><div className="header-actions"><select defaultValue="This month" aria-label="Reporting period"><option>This month</option><option>Last month</option><option>Last 3 months</option></select><Button variant="secondary" onClick={exportReport}><Download size={16} /> Export</Button></div></div>{anomaly && <div className="toast"><AlertTriangle size={17} /> Unusual emissions pattern detected: {anomaly.explanation}</div>}{exportError && <div className="toast"><AlertTriangle size={17} /> {exportError} <button onClick={() => setExportError(null)}><X size={15} /></button></div>}<div className="kpi-grid">{[{ label: "Total emissions", value: dashboard ? totalEmissions : "10,000", unit: "kg CO₂e", change: "8.4%", positive: true, icon: Activity, color: "red" }, { label: "Emission intensity", value: "0.42", unit: "kg CO₂e / unit", change: "5.1%", positive: true, icon: Gauge, color: "blue" },   { label: "Reduction potential", value: reductionPotential.toLocaleString(), unit: "kg CO₂e / month", change: "Available through actions", positive: true, icon: Target, color: "green" }, { label: "Carbon ROI", value: carbonRoi.toFixed(3), unit: "kg CO₂e / ₹", change: "Based on recommendations", positive: true, icon: CircleDollarSign, color: "amber" }].map(({ label, value, unit, change, positive, icon: Icon, color }) => <Card className="kpi-card" key={label}><div className={`kpi-icon ${color}`}><Icon size={18} /></div><div className="kpi-label">{label}<span className="info">i</span></div><strong>{value}</strong><span className="kpi-unit">{unit}</span><div className={positive ? "trend-positive" : ""}><ArrowDownRight size={14} /> {change} {label === "Total emissions" ? "vs previous period" : ""}</div></Card>)}</div><div className="dashboard-grid"><Card className="chart-card emissions-card"><SectionTitle title="Emissions by source" detail={`${factory?.name ?? "September 2026"} · ${totalEmissions} kg CO₂e`} action={<Link to="/emissions" className="text-link">View analysis <ArrowUpRight size={14} /></Link>} /><div className="donut-layout"><Donut items={displaySources} totalLabel={Number(totalEmissions).toLocaleString()} selected={selected} onSelect={setSelected} /><div className="legend">{displaySources.map((source) => <button className={`legend-row ${selected === source.name ? "selected" : ""}`} key={source.name} onClick={() => setSelected(source.name)}><span className="legend-dot" style={{ background: source.color }} /><span>{source.name}</span><strong>{source.value.toLocaleString()} <small>{Math.round(source.value / Number(totalEmissions) * 100)}%</small></strong></button>)}</div></div><div className="selected-detail"><span className="legend-dot" style={{ background: selectedSource.color }} /> <strong>{selectedSource.name}</strong> contributes <b>{Math.round(selectedSource.value / Number(totalEmissions) * 100)}%</b> of the monthly footprint <Link to="/hotspots">Explore hotspot <ArrowUpRight size={13} /></Link></div></Card><Card className="chart-card trend-card"><SectionTitle title="Monthly emissions trend" detail="Actual vs. reduction target" action={<button className="segmented active">CO₂e <ChevronDown size={13} /></button>} /><div className="chart-summary"><strong>{totalEmissions} <small>kg CO₂e</small></strong><span className="trend-positive"><ArrowDownRight size={14} /> 8.4% lower</span></div><TrendChart /></Card></div><div className="dashboard-grid bottom-grid"><Card><SectionTitle title="Top emission hotspots" detail="Ranked by contribution" action={<Link to="/hotspots" className="text-link">View all <ArrowUpRight size={14} /></Link>} /><div className="hotspot-list">{displaySources.map((source, i) => <Link to="/hotspots" className="hotspot-row" key={source.name}><span className="rank">{String(i + 1).padStart(2, "0")}</span><span className="source-icon" style={{ color: source.color }}>{source.name === "Electricity" ? <Zap size={17} /> : source.name === "Transportation" ? <Truck size={17} /> : source.name === "Waste" ? <Recycle size={17} /> : <Factory size={17} />}</span><div className="hotspot-name"><strong>{source.name}</strong><div className="bar-line"><span style={{ width: `${source.value / Number(totalEmissions) * 100}%`, background: source.color }} /></div></div><span className={`severity severity-${source.severity.toLowerCase()}`}>{source.severity}</span><strong className="hotspot-value">{Math.round(source.value / Number(totalEmissions) * 100)}%</strong><ArrowUpRight size={15} className="row-arrow" /></Link>)}</div></Card><Card className="insight-card"><div className="insight-top"><span className="ai-icon"><Sparkles size={18} /></span><Badge tone="green">EcoTrace AI insight</Badge><span className="confidence">94% confidence</span></div><h3>{insightTitle}</h3><p>{insightDescription}</p><div className="insight-grid"><div><span>Why this matters</span><strong>{insightValue} kg CO₂e</strong></div><div><span>Recommended next step</span><strong>{topRecommendation ? topRecommendation.name : "Optimize energy use"}</strong></div></div><Link to="/recommendations" className="button button-primary">Explore recommendation <ArrowUpRight size={15} /></Link></Card></div><div className="quick-actions"><span>Quick actions</span><Link to="/factory-data"><Plus size={16} /> Enter factory data</Link><Link to="/hotspots"><AlertTriangle size={16} /> Explore hotspots</Link><Link to="/simulator"><Calculator size={16} /> Run a what-if scenario</Link><Link to="/roadmap"><RouteIcon size={16} /> View action roadmap</Link></div></>;
}

function FactoryData({ onCalculate, onFactorySaved, factoryId }: { onCalculate: () => void; onFactorySaved: (factory: ApiFactory) => void; factoryId: number | null }) {
  const navigate = useNavigate();
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [factory, setFactory] = useState<ApiFactory | null>(null);
  const [factoryName, setFactoryName] = useState("Acme Manufacturing");
  const [industry, setIndustry] = useState("Industrial manufacturing");
  const [location, setLocation] = useState("Ahmedabad, Gujarat");
  const [reportingPeriod, setReportingPeriod] = useState("2026-09");
  const [productionVolume, setProductionVolume] = useState("24000");
  const [electricity, setElectricity] = useState("24000");
  const [renewable, setRenewable] = useState("20");
  const [naturalGas, setNaturalGas] = useState("1200");
  const [diesel, setDiesel] = useState("620");
  const [materials, setMaterials] = useState([{ name: "Steel", quantity: "12000", type: "Primary" }, { name: "Aluminium", quantity: "4500", type: "Primary" }, { name: "Plastic", quantity: "2000", type: "Mixed" }]);
  const [transportation, setTransportation] = useState({
    inboundDistance: "18400",
    outboundDistance: "12800",
    primaryMode: "Road freight",
    shipmentVolume: "320",
  });
  const [wasteStreams, setWasteStreams] = useState([
    { name: "Metal scrap", quantity: "800", disposal: "Recycling", recycled: "800" },
    { name: "Plastic waste", quantity: "300", disposal: "Landfill", recycled: "0" },
    { name: "Packaging", quantity: "200", disposal: "Recycling", recycled: "200" },
  ]);

  useEffect(() => {
    fetchFactories()
      .then((factories) => {
        const selected = factoryId !== null ? factories.find((item) => item.id === factoryId) ?? factories[0] : factories[0];
        if (!selected) return;
        setFactory(selected);
        setFactoryName(selected.name);
        setIndustry(selected.industry_type);
        setLocation(selected.location);
      })
      .catch(() => setFactory(null));
  }, [factoryId]);

  const saveFactoryData = async (): Promise<boolean> => {
    setError(null);
    try {
      let selectedFactory = factory;
      if (!selectedFactory) {
        selectedFactory = await createFactory({
          name: factoryName,
          industry_type: industry,
          location,
          production_unit: "units",
        });
        setFactory(selectedFactory);
        onFactorySaved(selectedFactory);
      }

      const [year, month] = reportingPeriod.split("-").map(Number);
      const periodStart = new Date(year, month - 1, 1);
      const periodEnd = new Date(year, month, 0);
      const period = await createReportingPeriod(selectedFactory.id, {
        period_start: periodStart.toISOString().slice(0, 10),
        period_end: periodEnd.toISOString().slice(0, 10),
        production_quantity: Number(productionVolume.replace(/,/g, "")),
        production_unit: "units",
      });

      await Promise.all([
        createEnergyUsage(selectedFactory.id, period.id, {
          source: "grid electricity",
          quantity: Number(electricity.replace(/,/g, "")),
          unit: "kWh",
          renewable_percentage: Number(renewable),
        }),
        Number(naturalGas) > 0 ? createEnergyUsage(selectedFactory.id, period.id, {
          source: "natural gas",
          quantity: Number(naturalGas.replace(/,/g, "")),
          unit: "m³",
        }) : Promise.resolve(),
        Number(diesel) > 0 ? createEnergyUsage(selectedFactory.id, period.id, {
          source: "diesel",
          quantity: Number(diesel.replace(/,/g, "")),
          unit: "litres",
        }) : Promise.resolve(),
      ]);

      await Promise.all(
        materials.filter((material) => material.name && Number(material.quantity || 0) > 0).map((material) =>
          createMaterialUsage(selectedFactory.id, period.id, {
            material_name: material.name,
            material_type: material.type,
            quantity: Number(material.quantity.replace(/,/g, "")),
            unit: "kg",
            recycled_content_percentage: material.type === "Recycled" ? 50 : 0,
          }),
        )
      );

      const transportationCalls = [
        Number(transportation.inboundDistance.replace(/,/g, "")) > 0 ? createTransportationActivity(selectedFactory.id, period.id, {
          mode: transportation.primaryMode,
          direction: "inbound",
          distance: Number(transportation.inboundDistance.replace(/,/g, "")),
          distance_unit: "km",
          load_quantity: Number(transportation.shipmentVolume.replace(/,/g, "")),
          load_unit: "tonnes",
        }) : Promise.resolve(),
        Number(transportation.outboundDistance.replace(/,/g, "")) > 0 ? createTransportationActivity(selectedFactory.id, period.id, {
          mode: transportation.primaryMode,
          direction: "outbound",
          distance: Number(transportation.outboundDistance.replace(/,/g, "")),
          distance_unit: "km",
          load_quantity: Number(transportation.shipmentVolume.replace(/,/g, "")),
          load_unit: "tonnes",
        }) : Promise.resolve(),
      ];
      await Promise.all(transportationCalls);

      await Promise.all(
        wasteStreams
          .filter((stream) => stream.name && Number(stream.quantity || 0) > 0)
          .map((stream) =>
            createWasteRecord(selectedFactory.id, period.id, {
              waste_type: stream.name,
              quantity: Number(stream.quantity.replace(/,/g, "")),
              unit: "kg",
              disposal_method: stream.disposal || "Recycling",
              recycled_quantity: Number(stream.recycled.replace(/,/g, "") || 0),
            }),
          ),
      );

      setSaved(true);
      onCalculate();
      return true;
    } catch (reason) {
      setSaved(false);
      setError(reason instanceof Error ? reason.message : "Unable to save factory data");
      return false;
    }
  };

  const calculate = async () => {
    if (await saveFactoryData()) {
      window.setTimeout(() => navigate("/emissions"), 700);
    }
  };

  return <><div className="page-header"><div><div className="eyebrow">Measure</div><h1>Factory data</h1><p>Provide operational data to estimate your factory’s carbon footprint.</p></div><div className="header-actions"><Badge tone="blue">{factory ? "Live factory synced" : "Draft mode"}</Badge><Button variant="secondary" onClick={saveFactoryData}>Save draft</Button><Button onClick={calculate}><Calculator size={16} /> Calculate emissions</Button></div></div>{saved && <div className="toast"><CheckCircle2 size={17} /> Factory data saved successfully <button onClick={() => setSaved(false)}><X size={15} /></button></div>}{error && <div className="toast"><AlertTriangle size={17} /> {error} <button onClick={() => setError(null)}><X size={15} /></button></div>}<div className="form-grid"><Card><SectionTitle eyebrow="01 · Factory profile" title="Factory information" /><div className="input-grid"><label>Factory name<input value={factoryName} onChange={(e) => setFactoryName(e.target.value)} /></label><label>Industry<select value={industry} onChange={(e) => setIndustry(e.target.value)}><option>Industrial manufacturing</option><option>Food processing</option><option>Textiles</option></select></label><label>Location<input value={location} onChange={(e) => setLocation(e.target.value)} /></label><label>Reporting period<input type="month" value={reportingPeriod} onChange={(e) => setReportingPeriod(e.target.value)} /></label><label>Production volume<input value={productionVolume} onChange={(e) => setProductionVolume(e.target.value)} /><small>units / month</small></label></div></Card><Card><SectionTitle eyebrow="02 · Energy" title="Energy consumption" detail="Use monthly totals from utility bills where possible." /><div className="input-grid"><label>Electricity consumption<input value={electricity} onChange={(e) => setElectricity(e.target.value)} /><small>kWh / month</small></label><label>Renewable electricity<input value={renewable} onChange={(e) => setRenewable(e.target.value)} /><small>% of total</small></label><label>Natural gas<input value={naturalGas} onChange={(e) => setNaturalGas(e.target.value)} /><small>m³ / month</small></label><label>Diesel<input value={diesel} onChange={(e) => setDiesel(e.target.value)} /><small>litres / month</small></label></div></Card><Card className="full-width"><SectionTitle eyebrow="03 · Materials" title="Material inputs" detail="Add the materials used during this reporting period." action={<Button variant="secondary" onClick={() => setMaterials([...materials, { name: "", quantity: "", type: "Primary" }])}><Plus size={15} /> Add material</Button>} /><div className="data-table"><div className="table-head"><span>Material</span><span>Quantity</span><span>Type</span><span>Recycled content</span><span /></div>{materials.map((material, index) => <div className="table-row" key={index}><input value={material.name} onChange={(e) => setMaterials(materials.map((m, i) => i === index ? { ...m, name: e.target.value } : m))} placeholder="Material name" /><input value={material.quantity} onChange={(e) => setMaterials(materials.map((m, i) => i === index ? { ...m, quantity: e.target.value } : m))} placeholder="0" /><select value={material.type} onChange={(e) => setMaterials(materials.map((m, i) => i === index ? { ...m, type: e.target.value } : m))}><option>Primary</option><option>Mixed</option><option>Recycled</option></select><div className="range-with-value"><input type="range" min="0" max="100" defaultValue={index * 10} /><span>{index * 10}%</span></div><button className="icon-button" onClick={() => setMaterials(materials.filter((_, i) => i !== index))}><X size={15} /></button></div>)}</div></Card><Card><SectionTitle eyebrow="04 · Logistics" title="Transportation" /><div className="input-grid"><label>Inbound distance<input value={transportation.inboundDistance} onChange={(e) => setTransportation((current) => ({ ...current, inboundDistance: e.target.value }))} /><small>km / month</small></label><label>Outbound distance<input value={transportation.outboundDistance} onChange={(e) => setTransportation((current) => ({ ...current, outboundDistance: e.target.value }))} /><small>km / month</small></label><label>Primary mode<select value={transportation.primaryMode} onChange={(e) => setTransportation((current) => ({ ...current, primaryMode: e.target.value }))}><option>Road freight</option><option>Rail</option><option>Mixed</option></select></label><label>Shipment volume<input value={transportation.shipmentVolume} onChange={(e) => setTransportation((current) => ({ ...current, shipmentVolume: e.target.value }))} /><small>tonnes / month</small></label></div></Card><Card><SectionTitle eyebrow="05 · Waste" title="Waste streams" action={<Button variant="secondary" onClick={() => setWasteStreams((current) => [...current, { name: "", quantity: "", disposal: "Recycling", recycled: "0" }])}><Plus size={15} /> Add waste stream</Button>} /><div className="waste-lines">{wasteStreams.map((stream, index) => <div key={index} className="waste-row"><input value={stream.name} onChange={(e) => setWasteStreams((current) => current.map((item, itemIndex) => itemIndex === index ? { ...item, name: e.target.value } : item))} placeholder="Waste type" /><input value={stream.quantity} onChange={(e) => setWasteStreams((current) => current.map((item, itemIndex) => itemIndex === index ? { ...item, quantity: e.target.value } : item))} placeholder="0" /><select value={stream.disposal} onChange={(e) => setWasteStreams((current) => current.map((item, itemIndex) => itemIndex === index ? { ...item, disposal: e.target.value } : item))}><option>Recycling</option><option>Landfill</option><option>Incineration</option><option>Recovery</option></select><input value={stream.recycled} onChange={(e) => setWasteStreams((current) => current.map((item, itemIndex) => itemIndex === index ? { ...item, recycled: e.target.value } : item))} placeholder="Recycled kg" /><button className="icon-button" onClick={() => setWasteStreams((current) => current.filter((_, itemIndex) => itemIndex !== index))}><X size={15} /></button></div>)}</div></Card></div></>;
}

function Emissions({ factoryId }: { factoryId: number | null }) {
  const [expanded, setExpanded] = useState<string | null>(null);
  const [calculation, setCalculation] = useState<ApiCalculation | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [exportError, setExportError] = useState<string | null>(null);
  useEffect(() => {
    let active = true;
    setCalculation(null);
    setError(null);
    fetchFactories()
      .then((factories) => {
        const selected = factoryId !== null ? factories.find((item) => item.id === factoryId) ?? factories[0] : factories[0];
        if (!selected) throw new Error("No accessible factories found");
        return fetchDashboard(selected.id);
      })
      .then((dashboard) => dashboard.calculation_id === null ? null : fetchCalculation(dashboard.calculation_id))
      .then((result) => { if (active && result) setCalculation(result); })
      .catch((reason: unknown) => { if (active) setError(reason instanceof Error ? reason.message : "Unable to load live emissions"); });
    return () => { active = false; };
  }, [factoryId]);
  const exportAnalysis = async () => {
    setExportError(null);
    if (calculation === null) {
      setExportError("No completed calculation is available for this factory yet");
      return;
    }
    try {
      await downloadCalculationCsv(calculation.id);
    } catch (reason) {
      setExportError(reason instanceof Error ? reason.message : "Unable to export emissions analysis");
    }
  };
  const liveSources = calculation?.breakdown.map((item, index) => ({
    name: item.source,
    value: Number(item.kg_co2e),
    color: sources[index % sources.length].color,
    trend: 0,
    severity: "Moderate" as const,
  })) ?? [];
  const displaySources = liveSources.length ? liveSources : sources;
  const total = calculation ? Number(calculation.total_kg_co2e) : 10000;
  const formatQuantity = (value: string, unit: string) => `${Number(value).toLocaleString()} ${unit}`;
  const breakdown = calculation?.breakdown ?? [];
  return <><div className="page-header"><div><div className="eyebrow">Identify</div><h1>Emissions analysis</h1><p>Understand the sources behind your {total.toLocaleString()} kg CO₂e monthly footprint.</p></div><Button variant="secondary" onClick={exportAnalysis}><Download size={16} /> Export analysis</Button></div>{error && <div className="toast"><AlertTriangle size={17} /> Showing demo analysis: {error}</div>}{exportError && <div className="toast"><AlertTriangle size={17} /> {exportError} <button onClick={() => setExportError(null)}><X size={15} /></button></div>}<div className="analysis-summary"><Card><span>Total emissions</span><strong>{total.toLocaleString()} <small>kg CO₂e</small></strong><div className="trend-positive"><ArrowDownRight size={14} /> 8.4% vs previous period</div></Card><Card><span>Production volume</span><strong>24,000 <small>units</small></strong><span>+4.0% vs previous period</span></Card><Card><span>Emission intensity</span><strong>0.42 <small>kg / unit</small></strong><div className="trend-positive"><ArrowDownRight size={14} /> 5.1% improvement</div></Card></div><div className="dashboard-grid"><Card className="chart-card"><SectionTitle title="Source breakdown" detail="Click a source to inspect its activity data." /><div className="donut-layout"><Donut items={displaySources} /><div className="legend">{displaySources.map((s) => <div className="legend-row" key={s.name}><span className="legend-dot" style={{ background: s.color }} /><span>{s.name}</span><strong>{s.value.toLocaleString()} <small>{Math.round(s.value / total * 100)}%</small></strong></div>)}</div></div></Card><Card className="chart-card"><SectionTitle title="Monthly trend" detail="Actual emissions compared with target." /><TrendChart /></Card></div><Card><SectionTitle title="Source details" detail="Activity data and emission factors used in this estimate." /><div className="data-table emissions-table"><div className="table-head"><span>Source</span><span>Activity</span><span>Emission factor</span><span>CO₂e</span><span>Share</span></div>{displaySources.map((source) => { const item = breakdown.find((entry) => entry.source === source.name); return <div key={source.name}><button className="table-row clickable" onClick={() => setExpanded(expanded === source.name ? null : source.name)}><strong>{source.name}</strong><span>{item ? formatQuantity(item.activity_quantity, item.activity_unit) : "—"}</span><span>{item ? `${Number(item.applied_factor).toLocaleString()} kg / ${item.activity_unit}` : "Calculated factor"}</span><strong>{source.value.toLocaleString()} kg</strong><span>{Math.round(source.value / total * 100)}% <ChevronDown size={14} /></span></button>{expanded === source.name && <div className="expanded-row"><BrainCircuit size={16} /><span><strong>How this is calculated:</strong> {item?.explanation ?? "activity quantity × verified emission factor, adjusted for the reporting period."}</span></div>}</div>; })}</div></Card></>;
}

function Hotspots({ factoryId }: { factoryId: number | null }) {
  const [hotspots, setHotspots] = useState<ApiHotspot[]>([]);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    let active = true;
    setHotspots([]);
    setError(null);
    fetchFactories()
      .then((factories) => {
        const selected = factoryId !== null ? factories.find((item) => item.id === factoryId) ?? factories[0] : factories[0];
        if (!selected) throw new Error("No accessible factories found");
        return fetchDashboard(selected.id);
      })
      .then((dashboard) => dashboard.calculation_id === null ? [] : fetchHotspots(dashboard.calculation_id))
      .then((result) => { if (active && result.length) setHotspots(result); })
      .catch((reason: unknown) => { if (active) setError(reason instanceof Error ? reason.message : "Unable to load live hotspots"); });
    return () => { active = false; };
  }, [factoryId]);
  const liveSources = hotspots.length ? hotspots : sources.map((source, index) => ({
    category: source.name,
    source: source.name,
    kg_co2e: String(source.value),
    percentage_of_total: String(source.value / 100),
    severity: source.severity.toLowerCase(),
    rank: index + 1,
    explanation: source.name === "Electricity" ? "Consumption rose 11% while production rose 4%, indicating lower energy efficiency in production operations." : "This source remains material to your footprint and is a good candidate for a focused reduction intervention.",
  }));
  const iconFor = (source: string) => source === "Electricity" ? <Zap /> : source === "Transportation" ? <Truck /> : source === "Waste" ? <Recycle /> : <Factory />;
  return <><div className="page-header"><div><div className="eyebrow">Identify · Explain</div><h1>Emission hotspots</h1><p>Identify the processes contributing most to your footprint.</p></div><Button variant="secondary"><SlidersHorizontal size={16} /> Filter hotspots</Button></div>{error && <div className="toast"><AlertTriangle size={17} /> Showing demo hotspots: {error}</div>}<div className="hotspot-hero"><div><Badge tone="red">{liveSources.length} hotspots identified</Badge><h2>{liveSources[0].source} needs attention first.</h2><p>{liveSources[0].explanation}</p><Link to="/recommendations" className="button button-primary">See recommendations <ArrowUpRight size={15} /></Link></div><div className="hero-stat"><strong>{Math.round(Number(liveSources[0].percentage_of_total))}%</strong><span>of total emissions</span><div className="trend-negative"><ArrowUpRight size={14} /> Priority {liveSources[0].rank}</div></div></div><div className="hotspot-cards">{liveSources.map((hotspot) => { const percentage = Number(hotspot.percentage_of_total); const severity = hotspot.severity.charAt(0).toUpperCase() + hotspot.severity.slice(1); return <Card key={`${hotspot.category}-${hotspot.source}`} className="hotspot-card"><div className="hotspot-card-head"><span className="rank large">{String(hotspot.rank).padStart(2, "0")}</span><div className="source-icon large" style={{ color: sources[(hotspot.rank - 1) % sources.length].color }}>{iconFor(hotspot.source)}</div><Badge tone={severity === "High" ? "red" : severity === "Moderate" ? "amber" : "green"}>{severity}</Badge><span className="confidence">Ranked by contribution</span></div><h3>{hotspot.source}</h3><div className="hotspot-number"><strong>{Number(hotspot.kg_co2e).toLocaleString()}</strong><span>kg CO₂e / month <b>· {Math.round(percentage)}%</b></span></div><div className="hotspot-card-body"><div><span>AI explanation</span><p>{hotspot.explanation}</p></div><div><span>Primary drivers</span><div className="driver"><em>{hotspot.category} activity</em><b style={{ width: `${Math.max(20, Math.min(100, percentage))}%` }} /></div><div className="driver"><em>Other operational activity</em><b style={{ width: `${Math.max(20, 100 - percentage)}%` }} /></div></div></div><Link to="/recommendations" className="text-link">See recommended action <ArrowUpRight size={14} /></Link></Card>; })}</div></>;
}

function RecommendationModal({ item, onClose, onAdd }: { item: Recommendation; onClose: () => void; onAdd: () => void }) { return <div className="modal-backdrop" onClick={onClose}><div className="modal" onClick={(e) => e.stopPropagation()}><button className="modal-close" onClick={onClose}><X size={18} /></button><div className="modal-kicker"><Sparkles size={16} /> EcoTrace AI recommendation</div><h2>{item.title}</h2><p>{item.description}</p><div className="modal-metrics"><div><span>CO₂ reduction</span><strong>{item.reduction.toLocaleString()} kg<span>/month</span></strong></div><div><span>Implementation cost</span><strong>{formatINR(item.cost)}</strong></div><div><span>Payback period</span><strong>{item.payback}</strong></div></div><h4>Why EcoTrace recommends this</h4><p>It combines a high reduction potential with {item.feasibility.toLowerCase()} feasibility and a strong carbon return. This action directly addresses one of your measured hotspots.</p><h4>Implementation steps</h4><ol><li>Validate supplier availability and material specifications.</li><li>Run a 30-day production pilot with quality checks.</li><li>Scale the substitution and track the monthly reduction.</li></ol><div className="modal-actions"><Button variant="secondary" onClick={onClose}>Close</Button><Button onClick={onAdd}><RouteIcon size={15} /> Add to roadmap</Button></div></div></div> }
function Recommendations({ addToRoadmap, factoryId }: { addToRoadmap: (item: Recommendation) => void; factoryId: number | null }) { const [sort, setSort] = useState("Priority"); const [filter, setFilter] = useState("All"); const [active, setActive] = useState<Recommendation | null>(null); const [liveItems, setLiveItems] = useState<Recommendation[] | null>(null); useEffect(() => { setLiveItems(null); fetchFactories().then((factories) => {
  const selected = factoryId !== null ? factories.find((item) => item.id === factoryId) ?? factories[0] : factories[0];
  return selected ? fetchDashboard(selected.id) : null;
}).then((dashboard) => dashboard?.calculation_id ? fetchRecommendations(dashboard.calculation_id) : null).then((items) => items && setLiveItems(items.map((item) => ({ id: item.id, title: item.name, category: item.category.charAt(0).toUpperCase() + item.category.slice(1), reduction: Number(item.estimated_reduction_kg_co2e), cost: Number(item.estimated_cost), roi: Number(item.carbon_roi_kg_co2e_per_cost ?? 0), feasibility: item.feasibility, payback: `${item.urgency} urgency`, priority: Math.round(Number(item.priority_score)), difficulty: item.feasibility, waste: "Tracked in roadmap", description: item.description })))).catch(() => setLiveItems(null)); }, [factoryId]); const items = useMemo(() => [...(liveItems ?? recommendations)].filter((i) => filter === "All" || i.category === filter).sort((a, b) => sort === "Lowest cost" ? a.cost - b.cost : sort === "Highest reduction" ? b.reduction - a.reduction : sort === "Highest ROI" ? b.roi - a.roi : b.priority - a.priority), [sort, filter, liveItems]); return <><div className="page-header"><div><div className="eyebrow">Recommend</div><h1>Circular recommendations</h1><p>Practical interventions ranked by carbon impact, cost, and feasibility.</p></div><Link to="/simulator" className="button button-primary"><Calculator size={16} /> Test a scenario</Link></div><div className="toolbar"><div className="filter-tabs">{["All", "Materials", "Energy", "Waste", "Transportation"].map((x) => <button className={filter === x ? "active" : ""} key={x} onClick={() => setFilter(x)}>{x}</button>)}</div><label className="sort-select">Sort by <select value={sort} onChange={(e) => setSort(e.target.value)}><option>Priority</option><option>Highest reduction</option><option>Lowest cost</option><option>Highest ROI</option></select></label></div><div className="recommendation-grid">{items.map((item) => <Card className="recommendation-card" key={item.id}><div className="recommendation-top"><Badge tone="blue">{item.category}</Badge><div className="priority-score"><strong>{item.priority}</strong><span>priority</span></div></div><h3>{item.title}</h3><p>{item.description}</p><div className="recommendation-metrics"><div><span>Reduction</span><strong>{item.reduction.toLocaleString()} <small>kg/mo</small></strong></div><div><span>Cost</span><strong>{formatINR(item.cost)}</strong></div><div><span>Carbon ROI</span><strong>{item.roi} <small>kg/₹</small></strong></div></div><div className="rec-details"><span><CheckCircle2 size={14} /> {item.feasibility} feasibility</span><span><ClockIcon /> {item.payback}</span><span><Recycle size={14} /> {item.waste}</span></div><div className="card-actions"><Button variant="secondary" onClick={() => setActive(item)}>View details <ArrowUpRight size={14} /></Button><Button onClick={() => addToRoadmap(item)}><Plus size={15} /> Add to roadmap</Button></div></Card>)}</div>{active && <RecommendationModal item={active} onClose={() => setActive(null)} onAdd={() => { addToRoadmap(active); setActive(null); }} />}</> }
function ClockIcon() { return <span className="clock-icon">◷</span>; }

function Simulator({ onSave, factoryId }: { onSave: (message: string) => void; factoryId: number | null }) {
  const [controls, setControls] = useState({ recycled: 30, renewable: 20, transport: 10, waste: 35, efficiency: 15 });
  const [live, setLive] = useState<{ baseline: number; emissions: number; reduction: number; reductionPercent: number } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fallback = calculateScenario(controls);
  useEffect(() => {
    let active = true;
    setLive(null);
    setError(null);
    fetchFactories().then((factories) => {
      const selected = factoryId !== null ? factories.find((item) => item.id === factoryId) ?? factories[0] : factories[0];
      if (!selected) throw new Error("No accessible factories found");
      return fetchDashboard(selected.id);
    }).then((dashboard) => {
      if (dashboard.calculation_id === null) throw new Error("No completed calculation found");
      const adjustments = dashboard.hotspots.map((hotspot) => ({
        category: hotspot.category,
        source: hotspot.source,
        reduction_percentage: hotspot.category.toLowerCase().includes("material") ? controls.recycled : hotspot.category.toLowerCase().includes("energy") ? Math.min(100, controls.renewable + controls.efficiency) : hotspot.category.toLowerCase().includes("transport") ? controls.transport : hotspot.category.toLowerCase().includes("waste") ? controls.waste : 0,
      })).filter((adjustment) => adjustment.reduction_percentage > 0);
      if (!adjustments.length) throw new Error("Add an intervention to simulate");
      return simulateCalculation(dashboard.calculation_id, adjustments);
    }).then((result) => { if (active) { setLive({ baseline: Number(result.baseline_kg_co2e), emissions: Number(result.simulated_kg_co2e), reduction: Number(result.reduction_kg_co2e), reductionPercent: Number(result.reduction_percentage) }); setError(null); } }).catch((reason: unknown) => { if (active) { setLive(null); setError(reason instanceof Error ? reason.message : "Unable to load live simulation"); } });
    return () => { active = false; };
  }, [controls, factoryId]);
  const result = live ?? { baseline: 10000, emissions: fallback.emissions, reduction: fallback.reduction, reductionPercent: fallback.reductionPercent };
  const set = (key: keyof typeof controls, value: number) => setControls({ ...controls, [key]: value });
  return <><div className="page-header"><div><div className="eyebrow">Simulate</div><h1>What-if simulator</h1><p>Test sustainability interventions before changing your operations.</p></div><div className="header-actions"><Button variant="secondary" onClick={() => setControls({ recycled: 0, renewable: 0, transport: 0, waste: 0, efficiency: 0 })}>Reset scenario</Button><Button onClick={() => onSave("Scenario saved successfully")}><Check size={16} /> Save scenario</Button></div></div>{error && <div className="toast"><AlertTriangle size={17} /> Showing local scenario estimate: {error}</div>}<div className="simulator-layout"><Card className="control-card"><div className="card-heading"><div><Badge tone="green">Scenario builder</Badge><h2>Adjust the levers</h2><p>Results update instantly from your {result.baseline.toLocaleString()} kg CO₂e baseline.</p></div><SlidersHorizontal size={20} /></div>{[{ key: "recycled", label: "Recycled material substitution", max: 100, unit: "%" }, { key: "renewable", label: "Renewable electricity", max: 100, unit: "%" }, { key: "transport", label: "Transport optimization", max: 50, unit: "%" }, { key: "waste", label: "Waste recycling", max: 100, unit: "%" }, { key: "efficiency", label: "Energy efficiency improvement", max: 40, unit: "%" }].map(({ key, label, max, unit }) => <label className="slider-control" key={key}><div><span>{label}</span><strong>{controls[key as keyof typeof controls]}{unit}</strong></div><input type="range" min="0" max={max} value={controls[key as keyof typeof controls]} onChange={(e) => set(key as keyof typeof controls, Number(e.target.value))} /></label>)}<div className="scenario-note"><Sparkles size={16} /><span>Try combining material substitution with energy efficiency for a balanced intervention plan.</span></div></Card><div className="sim-results"><div className="sim-kpis"><Card><span>Baseline emissions</span><strong>{result.baseline.toLocaleString()}</strong><small>kg CO₂e / month</small></Card><Card className="highlight"><span>Scenario emissions</span><strong>{result.emissions.toLocaleString()}</strong><small>kg CO₂e / month</small></Card><Card><span>CO₂ reduction</span><strong className="green-text">{result.reduction.toLocaleString()}</strong><small>kg CO₂e / month</small></Card><Card><span>Reduction</span><strong className="green-text">{result.reductionPercent}%</strong><small>of baseline</small></Card></div><Card className="comparison-card"><SectionTitle title="Scenario comparison" detail="Monthly emissions · lower is better" /><div className="compare-bars"><div><span>Current baseline</span><strong>{result.baseline.toLocaleString()} kg</strong><div className="compare-track"><i style={{ width: "100%" }} /></div></div><div><span>Simulated scenario</span><strong>{result.emissions.toLocaleString()} kg</strong><div className="compare-track"><i className="green-bar" style={{ width: `${result.emissions / result.baseline * 100}%` }} /></div></div></div><TrendChart compact /></Card><Card className="scenario-summary"><div className="summary-icon"><Sparkles size={18} /></div><div><Badge tone="green">Scenario summary</Badge><h3>Estimated monthly emissions could decrease by {result.reductionPercent}%.</h3><p>This intervention set saves <b>{result.reduction.toLocaleString()} kg CO₂e</b> at an estimated investment based on the selected levers.</p></div><div className="summary-actions"><Button onClick={() => onSave("Scenario added to roadmap")}><RouteIcon size={15} /> Add to roadmap</Button></div></Card></div></div></>;
}

function Roadmap({ roadmap, setRoadmap, factoryId }: { roadmap: RoadmapItem[]; setRoadmap: Dispatch<SetStateAction<RoadmapItem[]>>; factoryId: number | null }) {
  const [liveItems, setLiveItems] = useState<RoadmapItem[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [calculationId, setCalculationId] = useState<number | null>(null);
  const [persistedActions, setPersistedActions] = useState<Record<number, number>>({});
  useEffect(() => {
    let active = true;
    setLiveItems(null);
    setError(null);
    fetchFactories().then((factories) => {
      const selected = factoryId !== null ? factories.find((item) => item.id === factoryId) ?? factories[0] : factories[0];
      if (!selected) throw new Error("No accessible factories found");
      return fetchDashboard(selected.id);
    }).then((dashboard) => {
      if (dashboard.calculation_id === null) throw new Error("No roadmap data available");
      setCalculationId(dashboard.calculation_id);
      return Promise.all([fetchRoadmap(dashboard.calculation_id), fetchRoadmapActions(dashboard.factory_id)]);
    }).then(([result, persisted]) => {
      if (!active) return;
      const mapped = result.actions.map((action, index) => ({
        id: action.intervention_id,
        title: action.intervention_name,
        category: action.target_source,
        reduction: Number(action.estimated_reduction_kg_co2e),
        cost: Number(action.estimated_cost),
        roi: Number(action.estimated_reduction_kg_co2e) / Number(action.estimated_cost || 1),
        feasibility: action.phase,
        payback: `${action.phase} phase`,
        priority: action.recommendation_rank * 10,
        difficulty: action.phase,
        waste: action.target_source,
        description: action.rationale,
        status: (index === 0 ? "Planned" : index === 1 ? "In Progress" : "Not Started") as RoadmapItem["status"],
        timeline: index === 0 ? "0–3 months" : index === 1 ? "1–6 months" : "0–2 months",
      }));
      const currentActions = persisted.filter((action) => action.calculation_id === result.calculation_id);
      const actionByIntervention = Object.fromEntries(currentActions.map((action) => [action.intervention_id, action]));
      setPersistedActions(Object.fromEntries(currentActions.map((action) => [action.intervention_id, action.id])));
      setLiveItems(mapped.map((item) => {
        const action = actionByIntervention[item.id];
        if (!action) return item;
        const status = action.status.replace("_", " ");
        return { ...item, status: (status.charAt(0).toUpperCase() + status.slice(1)) as RoadmapItem["status"] };
      }));
      setError(null);
    }).catch((reason: unknown) => {
      if (active) {
        setLiveItems(null);
        setError(reason instanceof Error ? reason.message : "Unable to load live roadmap");
      }
    });
    return () => { active = false; };
  }, [factoryId]);

  const items = liveItems ?? roadmap;
  const total = items.reduce((sum, i) => sum + i.reduction, 0);
  const done = items.filter((i) => i.status === "Completed").length;
  const updateStatus = async (id: number, status: RoadmapItem["status"]) => {
    setRoadmap((prev) => prev.map((r) => r.id === id ? { ...r, status } : r));
    setLiveItems((prev) => prev ? prev.map((r) => r.id === id ? { ...r, status } : r) : null);
    if (factoryId === null || calculationId === null) return;
    try {
      const apiStatus = status.toLowerCase().replace(" ", "_");
      const actionId = persistedActions[id];
      const action = actionId
        ? await updateRoadmapAction(factoryId, actionId, apiStatus)
        : await createRoadmapAction(factoryId, { calculation_id: calculationId, intervention_id: id, status: apiStatus });
      setPersistedActions((current) => ({ ...current, [id]: action.id }));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to save roadmap status");
    }
  };
  return <><div className="page-header"><div><div className="eyebrow">Prioritize · Act</div><h1>Action roadmap</h1><p>Your prioritized path from emissions insight to implementation.</p></div><Button onClick={() => { const next = items.find((item) => item.status !== "Completed"); if (next) void updateStatus(next.id, "Completed"); }}><Check size={15} /> Mark next action complete</Button></div>{error && <div className="toast"><AlertTriangle size={17} /> Showing local roadmap: {error}</div>}<div className="roadmap-summary"><div><span>Total potential reduction</span><strong>{total.toLocaleString()} <small>kg CO₂e / month</small></strong></div><div><span>Potential reduction</span><strong>{Math.round(total / 100)}%</strong></div><div><span>Actions completed</span><strong>{done} <small>/ {items.length}</small></strong></div><div className="progress-summary"><span>Overall progress</span><div className="progress"><i style={{ width: `${items.length ? done / items.length * 100 : 0}%` }} /></div><strong>{items.length ? Math.round(done / items.length * 100) : 0}%</strong></div></div><Card className="roadmap-card"><div className="roadmap-line" />{items.map((item, index) => <div className="roadmap-item" key={item.id}><div className={`roadmap-node status-${item.status.toLowerCase().replace(" ", "-")}`}>{item.status === "Completed" ? <Check size={15} /> : String(index + 1).padStart(2, "0")}</div><div className="roadmap-content"><div className="roadmap-item-top"><div><Badge tone={item.status === "In Progress" ? "blue" : item.status === "Completed" ? "green" : "neutral"}>{item.status}</Badge><h3>{item.title}</h3><p>{item.category} · {item.timeline}</p></div><select value={item.status} onChange={(e) => void updateStatus(item.id, e.target.value as RoadmapItem["status"])}><option>Not Started</option><option>Planned</option><option>In Progress</option><option>Completed</option></select></div><div className="roadmap-metrics"><span><strong>{item.priority}/100</strong> priority</span><span><strong>{item.reduction.toLocaleString()}</strong> kg CO₂e/month</span><span><strong>{formatINR(item.cost)}</strong> investment</span></div></div></div>)}</Card></> }

function Reports({ factoryId }: { factoryId: number | null }) {
  const [exported, setExported] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [calculationId, setCalculationId] = useState<number | null>(null);
  const [reportTotal, setReportTotal] = useState<number | null>(null);
  const [reportFactory, setReportFactory] = useState<string | null>(null);
  const files = [{ title: "Monthly emissions report", date: "September 2026", icon: BarChart3, tone: "green" }, { title: "Hotspot analysis", date: "September 2026", icon: AlertTriangle, tone: "red" }, { title: "Circular opportunity report", date: "Q3 2026", icon: Recycle, tone: "blue" }, { title: "Action roadmap", date: "Updated today", icon: RouteIcon, tone: "amber" }];
  useEffect(() => {
    setCalculationId(null);
    setReportTotal(null);
    setReportFactory(null);
    setError(null);
    fetchFactories().then((factories) => {
      const selected = factoryId !== null ? factories.find((item) => item.id === factoryId) ?? factories[0] : factories[0];
      if (!selected) return null;
      setReportFactory(selected.name);
      return fetchDashboard(selected.id);
    }).then((dashboard) => {
      if (!dashboard) return;
      setCalculationId(dashboard.calculation_id);
      setReportTotal(Number(dashboard.total_kg_co2e));
    }).catch((reason: unknown) => {
      setCalculationId(null);
      setError(reason instanceof Error ? reason.message : "Unable to load report data");
    });
  }, [factoryId]);
  const download = async () => {
    setError(null);
    if (calculationId === null) {
      setExported(true);
      return;
    }
    try {
      await downloadCalculationCsv(calculationId);
      setExported(true);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to download report");
    }
  };
  const reportValue = reportTotal === null ? "10,000" : reportTotal.toLocaleString();
  return <><div className="page-header"><div><div className="eyebrow">Decision support</div><h1>Reports</h1><p>Share-ready analysis for your team, consultants, and stakeholders.</p></div><Button onClick={download}><Download size={16} /> Export report</Button></div>{exported && <div className="toast"><CheckCircle2 size={17} /> {calculationId === null ? "Demo report ready to download" : "Report downloaded successfully"} <button onClick={() => setExported(false)}><X size={15} /></button></div>}{error && <div className="toast"><AlertTriangle size={17} /> Showing demo report: {error}</div>}<div className="report-feature"><div><Badge tone="green">Latest report</Badge><h2>{reportFactory ?? "September"} emissions overview</h2><p>A clear view of your footprint, hotspots, and highest-value actions for the month.</p><div><Button onClick={download}><Download size={15} /> Download CSV</Button><Button variant="secondary">View report <ArrowUpRight size={15} /></Button></div></div><div className="report-preview"><div className="report-preview-head"><Leaf size={14} /> EcoTrace AI <span>SEP 2026</span></div><div className="report-preview-title">Emissions overview</div><div className="report-preview-number">{reportValue} <small>kg CO₂e</small></div><div className="report-preview-bars"><i /><i /><i /><i /></div></div></div><div className="report-grid">{files.map(({ title, date, icon: Icon, tone }) => <Card key={title}><div className={`report-icon ${tone}`}><Icon size={19} /></div><h3>{title}</h3><p>{date} · PDF and CSV available</p><div className="card-actions"><Button variant="secondary">View report</Button><button className="icon-button" onClick={download} aria-label={`Download ${title}`}><Download size={16} /></button></div></Card>)}</div></>;
}
function SettingsPage({ factoryId, onFactorySaved }: { factoryId: number | null; onFactorySaved: (factory: ApiFactory) => void }) {
  const [factory, setFactory] = useState<ApiFactory | null>(null);
  const [factoryName, setFactoryName] = useState("");
  const [industry, setIndustry] = useState("");
  const [location, setLocation] = useState("");
  const [unitSystem, setUnitSystem] = useState("Metric");
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setSaved(false);
    setError(null);
    fetchFactories()
      .then((factories) => {
        const selected = factoryId !== null ? factories.find((item) => item.id === factoryId) ?? factories[0] : factories[0];
        if (!selected) throw new Error("No accessible factories found");
        setFactory(selected);
        setFactoryName(selected.name);
        setIndustry(selected.industry_type);
        setLocation(selected.location);
      })
      .catch((reason: unknown) => setError(reason instanceof Error ? reason.message : "Unable to load factory settings"));
  }, [factoryId]);

  const save = async () => {
    setSaved(false);
    setError(null);
    if (!factory) {
      setError("Select a factory before saving settings");
      return;
    }
    try {
      const updated = await updateFactory(factory.id, {
        name: factoryName,
        industry_type: industry,
        location,
        production_unit: factory.production_unit,
      });
      setFactory(updated);
      onFactorySaved(updated);
      setSaved(true);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to save factory settings");
    }
  };

  return <><div className="page-header"><div><div className="eyebrow">Workspace</div><h1>Settings</h1><p>Keep your factory profile and analysis preferences up to date.</p></div><Button onClick={save}>Save changes</Button></div>{saved && <div className="toast"><CheckCircle2 size={17} /> Factory settings saved</div>}{error && <div className="toast"><AlertTriangle size={17} /> {error}</div>}<div className="settings-grid"><Card><SectionTitle title="Factory profile" detail="Used to personalize calculations and reports." /><div className="input-grid"><label>Factory name<input value={factoryName} onChange={(e) => setFactoryName(e.target.value)} /></label><label>Industry<select value={industry} onChange={(e) => setIndustry(e.target.value)}><option>Industrial manufacturing</option><option>Food processing</option><option>Textiles</option></select></label><label>Location<input value={location} onChange={(e) => setLocation(e.target.value)} /></label><label>Default unit system<select value={unitSystem} onChange={(e) => setUnitSystem(e.target.value)}><option>Metric</option><option>Imperial</option></select></label></div></Card><Card><SectionTitle title="Analysis preferences" /><div className="settings-lines"><label><span><strong>Monthly analysis reminders</strong><small>Get notified when it’s time to refresh your data.</small></span><input type="checkbox" defaultChecked /></label><label><span><strong>Include estimated factors</strong><small>Use modeled factors when measured data is missing.</small></span><input type="checkbox" defaultChecked /></label><label><span><strong>Compact chart labels</strong><small>Prefer cleaner charts for presentations.</small></span><input type="checkbox" /></label></div></Card><Card><SectionTitle title="Emission factors" detail="India · 2026 factor set" /><div className="factor-row"><span>Grid electricity</span><strong>0.70 kg CO₂e / kWh</strong><button className="text-link">Edit</button></div><div className="factor-row"><span>Diesel</span><strong>2.68 kg CO₂e / litre</strong><button className="text-link">Edit</button></div><div className="factor-row"><span>Transport average</span><strong>0.12 kg CO₂e / tonne-km</strong><button className="text-link">Edit</button></div></Card></div></>;
}

function Landing() { const navigate = useNavigate(); return <div className="landing"><header className="landing-nav"><Link to="/" className="brand"><span className="brand-mark"><Leaf size={19} /></span><span>EcoTrace <b>AI</b></span></Link><div><a href="#how">How it works</a><a href="#capabilities">Capabilities</a><a href="#impact">Example impact</a><Link to="/login" className="text-link">Sign in</Link></div><Button variant="secondary" onClick={() => navigate("/dashboard")}>Explore dashboard <ArrowUpRight size={15} /></Button></header><main><section className="landing-hero"><div className="hero-copy"><Badge tone="green"><span className="status-dot" /> Industrial emissions intelligence</Badge><h1>Find the emissions.<br /><em>Fix the process.</em><br />Close the carbon loop.</h1><p>Turn industrial data into actionable carbon reduction decisions. EcoTrace AI shows factory operators what to change first—and why.</p><div className="hero-actions"><Button onClick={() => navigate("/dashboard")}>Analyze my factory <ArrowUpRight size={16} /></Button><a href="#how" className="button button-secondary">See how it works <ChevronDown size={16} /></a></div><div className="hero-meta"><span><CheckCircle2 size={15} /> Explainable insights</span><span><CheckCircle2 size={15} /> Circular alternatives</span><span><CheckCircle2 size={15} /> What-if decisions</span></div></div><div className="hero-dashboard"><div className="hero-dash-top"><div><span className="eyebrow">Acme Manufacturing · Live demo</span><strong>Emissions overview</strong></div><span className="status-dot" /></div><div className="hero-dash-metrics"><div><span>Total emissions</span><strong>10,000 <small>kg CO₂e</small></strong><b>↓ 8.4%</b></div><div><span>Reduction potential</span><strong>2,100 <small>kg / mo</small></strong><b>Action-ready</b></div></div><div className="hero-dash-chart"><div><span>Monthly trend</span><strong>10,000 kg</strong></div><TrendChart compact /></div><div className="hero-dash-bottom"><div><span>Largest hotspot</span><strong><span className="legend-dot red-dot" /> Electricity <small>42%</small></strong></div><div><span>Top recommendation</span><strong><span className="legend-dot green-dot" /> Recycled material</strong></div></div></div></section><section className="trust-strip"><span>Built for teams making the next operational decision</span><b>SMEs</b><b>Factory operators</b><b>Sustainability consultants</b><b>Regulators</b></section><section id="how" className="landing-section"><div className="center-heading"><div className="eyebrow">Measure → Act</div><h2>From raw factory data to <em>clear next steps.</em></h2><p>The intelligence layer that turns a footprint into a practical operating plan.</p></div><div className="steps">{["Measure", "Identify", "Explain", "Recommend", "Simulate", "Prioritize", "Act"].map((step, i) => <div key={step} className={i === 0 ? "active" : ""}><span>0{i + 1}</span><strong>{step}</strong>{i < 6 && <ArrowUpRight size={14} />}</div>)}</div></section><section id="impact" className="landing-section impact-section"><div className="center-heading"><div className="eyebrow">Illustrative impact</div><h2>Decisions backed by <em>carbon and cost.</em></h2></div><div className="impact-grid"><div><span>Total monthly emissions</span><strong>10,000 <small>kg CO₂e</small></strong></div><div><span>Largest hotspot</span><strong>Raw materials <small>25%</small></strong></div><div><span>Potential reduction</span><strong>2,100 <small>kg / month</small></strong></div><div><span>Carbon ROI</span><strong>0.014 <small>kg CO₂ / ₹</small></strong></div></div></section><section id="capabilities" className="landing-section capabilities"><div className="center-heading"><div className="eyebrow">One connected workflow</div><h2>Industrial sustainability, <em>without the guesswork.</em></h2></div><div className="capability-grid">{[{ icon: AlertTriangle, title: "Hotspot detection", text: "See which process is responsible for the largest share of your emissions." }, { icon: BrainCircuit, title: "Explainable AI", text: "Understand what changed, why it matters, and how confident the signal is." }, { icon: Recycle, title: "Circular alternatives", text: "Find waste-to-value opportunities and practical material substitutions." }, { icon: Calculator, title: "What-if simulation", text: "Test an intervention before investing in equipment, suppliers, or process changes." }].map(({ icon: Icon, title, text }) => <Card key={title}><div className="capability-icon"><Icon size={20} /></div><h3>{title}</h3><p>{text}</p><ArrowUpRight size={16} /></Card>)}</div></section><section className="landing-cta"><div><span className="eyebrow">Your next decision is already in the data.</span><h2>Start understanding your factory’s emissions.</h2><p>See the demo workspace and find your highest-value action in under 10 seconds.</p></div><Button onClick={() => navigate("/dashboard")}>Open demo workspace <ArrowUpRight size={16} /></Button></section></main><footer><Link to="/" className="brand"><span className="brand-mark"><Leaf size={17} /></span><span>EcoTrace <b>AI</b></span></Link><span>Measure better. Operate smarter. Close the loop.</span><span>© 2026 EcoTrace AI</span></footer></div> }

function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isRegistering, setIsRegistering] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await (isRegistering ? register(email, password) : login(email, password));
      navigate("/dashboard");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to authenticate");
    } finally {
      setLoading(false);
    }
  };
  return <div className="auth-page"><header className="auth-header"><Link to="/" className="brand"><span className="brand-mark"><Leaf size={19} /></span><span>EcoTrace <b>AI</b></span></Link><span className="auth-header-note">Industrial emissions intelligence</span></header><main className="auth-layout"><section className="auth-intro"><Badge tone="green"><span className="status-dot" /> Secure workspace access</Badge><h1>Turn your factory data into your next best decision.</h1><p>Sign in to continue to live emissions analysis, hotspot insights, and circular action planning.</p><div className="auth-benefits"><div><span><CheckCircle2 size={16} /></span><strong>Live emissions intelligence<small>Track your latest calculated footprint.</small></strong></div><div><span><CheckCircle2 size={16} /></span><strong>Explainable recommendations<small>Know what to change and why it matters.</small></strong></div><div><span><CheckCircle2 size={16} /></span><strong>Protected factory data<small>Your owned workspaces stay private.</small></strong></div></div></section><section className="auth-card"><div className="auth-card-heading"><div className="eyebrow">EcoTrace workspace</div><h2>{isRegistering ? "Create your account" : "Welcome back"}</h2><p>{isRegistering ? "Create an account to manage your factory workspace." : "Sign in to access your factory workspace."}</p></div><form onSubmit={submit} className="auth-form"><label>Email address<input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required autoComplete="email" placeholder="you@company.com" /></label><label>Password<input type="password" value={password} onChange={(event) => setPassword(event.target.value)} required autoComplete={isRegistering ? "new-password" : "current-password"} minLength={8} placeholder="At least 8 characters" /></label>{error && <p className="auth-error" role="alert">{error}</p>}<Button type="submit">{loading ? "Please wait..." : isRegistering ? "Create account" : "Sign in"} <ArrowUpRight size={15} /></Button></form><button className="auth-switch" onClick={() => { setIsRegistering(!isRegistering); setError(null); }}>{isRegistering ? "Already have an account? Sign in" : "New to EcoTrace? Create an account"}</button><Link to="/" className="auth-back">Back to home</Link><small className="auth-security"><CheckCircle2 size={13} /> Your session is protected with secure authentication</small></section></main></div>;
}

export default function App() {
  const [roadmap, setRoadmap] = useState<RoadmapItem[]>(initialRoadmap);
  const [toast, setToast] = useState("");
  const [factoryOptions, setFactoryOptions] = useState<ApiFactory[]>([]);
  const [selectedFactoryId, setSelectedFactoryId] = useState<number | null>(null);
  const refreshFactories = (updatedFactory?: ApiFactory) => {
    fetchFactories().then((factories) => {
      setFactoryOptions(factories);
      if (updatedFactory && factories.some((factory) => factory.id === updatedFactory.id)) {
        setSelectedFactoryId(updatedFactory.id);
      }
      if (factories.length > 0 && selectedFactoryId === null) {
        setSelectedFactoryId(factories[0].id);
      }
      if (selectedFactoryId !== null && !factories.some((factory) => factory.id === selectedFactoryId)) {
        setSelectedFactoryId(factories[0]?.id ?? null);
      }
    }).catch(() => {
      setFactoryOptions([]);
      setSelectedFactoryId(null);
    });
  };
  useEffect(() => {
    refreshFactories();
  }, []);
  const showToast = (message: string) => { setToast(message); window.setTimeout(() => setToast(""), 3200); };
  const addToRoadmap = async (item: Recommendation) => {
    if (roadmap.some((r) => r.id === item.id)) {
      showToast(`${item.title} is already on the roadmap`);
      return;
    }
    try {
      if (selectedFactoryId !== null) {
        const dashboard = await fetchDashboard(selectedFactoryId);
        if (dashboard.calculation_id !== null) {
          await createRoadmapAction(selectedFactoryId, {
            calculation_id: dashboard.calculation_id,
            intervention_id: item.id,
            status: "planned",
          });
        }
      }
      setRoadmap((current) => [...current, { ...item, status: "Planned", timeline: "0–3 months" }]);
      showToast(`${item.title} added to roadmap`);
    } catch (reason) {
      showToast(reason instanceof Error ? reason.message : "Unable to add recommendation to roadmap");
    }
  };
  const selectedFactory = factoryOptions.find((factory) => factory.id === selectedFactoryId) ?? factoryOptions[0] ?? null;
  return <Routes><Route path="/" element={<Landing />} /><Route path="/login" element={<Login />} /><Route path="*" element={<Shell
    roadmap={roadmap}
    setRoadmap={setRoadmap}
    factoryOptions={factoryOptions}
    selectedFactory={selectedFactory}
    onSelectFactory={setSelectedFactoryId}
  ><Routes><Route path="/dashboard" element={<Overview setRoadmap={setRoadmap} factoryId={selectedFactoryId} />} /><Route path="/factory-data" element={<FactoryData onCalculate={() => showToast("Emissions calculated successfully")} onFactorySaved={(factory) => refreshFactories(factory)} factoryId={selectedFactoryId} />} /><Route path="/emissions" element={<Emissions factoryId={selectedFactoryId} />} /><Route path="/hotspots" element={<Hotspots factoryId={selectedFactoryId} />} /><Route path="/recommendations" element={<Recommendations addToRoadmap={addToRoadmap} factoryId={selectedFactoryId} />} /><Route path="/simulator" element={<Simulator onSave={showToast} factoryId={selectedFactoryId} />} /><Route path="/roadmap" element={<Roadmap roadmap={roadmap} setRoadmap={setRoadmap} factoryId={selectedFactoryId} />} /><Route path="/reports" element={<Reports factoryId={selectedFactoryId} />} /><Route path="/settings" element={<SettingsPage factoryId={selectedFactoryId} onFactorySaved={(factory) => refreshFactories(factory)} />} /></Routes>{toast && <div className="toast global-toast"><CheckCircle2 size={17} /> {toast}</div>}</Shell>} /></Routes>;
}
