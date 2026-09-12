export type Source = { name: string; value: number; color: string; trend: number; severity: "High" | "Moderate" | "Low" };
export type Recommendation = { id: number; title: string; category: string; reduction: number; cost: number; roi: number; feasibility: string; payback: string; priority: number; difficulty: string; waste: string; description: string };
export type RoadmapItem = Recommendation & { status: "Not Started" | "Planned" | "In Progress" | "Completed"; timeline: string };

export const sources: Source[] = [
  { name: "Electricity", value: 4200, color: "#ef765e", trend: 11, severity: "High" },
  { name: "Raw materials", value: 2500, color: "#e4a340", trend: 4, severity: "High" },
  { name: "Transportation", value: 1500, color: "#5688bd", trend: -2, severity: "Moderate" },
  { name: "Processes", value: 1000, color: "#7f8f9b", trend: 1, severity: "Moderate" },
  { name: "Waste", value: 800, color: "#68a77d", trend: -8, severity: "Low" },
];

export const trend = [
  { month: "Apr", emissions: 11200, intensity: 0.49, target: 10500 },
  { month: "May", emissions: 10800, intensity: 0.47, target: 10400 },
  { month: "Jun", emissions: 10600, intensity: 0.45, target: 10300 },
  { month: "Jul", emissions: 10300, intensity: 0.44, target: 10200 },
  { month: "Aug", emissions: 10100, intensity: 0.43, target: 10100 },
  { month: "Sep", emissions: 10000, intensity: 0.42, target: 9900 },
];

export const recommendations: Recommendation[] = [
  { id: 1, title: "30% recycled material substitution", category: "Materials", reduction: 2100, cost: 150000, roi: 0.014, feasibility: "High", payback: "~2 years", priority: 92, difficulty: "Medium", waste: "1.2 t / month", description: "Replace a portion of primary steel and aluminium feedstock with verified recycled inputs without changing product specifications." },
  { id: 2, title: "Energy efficiency optimization", category: "Energy", reduction: 1400, cost: 90000, roi: 0.016, feasibility: "High", payback: "14 months", priority: 87, difficulty: "Low", waste: "—", description: "Tune compressed-air set points, add variable speed drives and schedule high-load machinery around production demand." },
  { id: 3, title: "Transport route optimization", category: "Transportation", reduction: 620, cost: 42000, roi: 0.015, feasibility: "Medium", payback: "18 months", priority: 76, difficulty: "Low", waste: "0.3 t / month", description: "Consolidate inbound shipments and shift two recurring lanes to a lower-carbon carrier." },
  { id: 4, title: "Segregate and monetize metal scrap", category: "Waste", reduction: 480, cost: 28000, roi: 0.017, feasibility: "High", payback: "9 months", priority: 73, difficulty: "Low", waste: "0.8 t / month", description: "Create a clean scrap stream for a local secondary raw-material buyer and avoid mixed-waste disposal." },
];

export const initialRoadmap: RoadmapItem[] = recommendations.map((item, index) => ({
  ...item,
  status: index === 0 ? "Planned" : index === 1 ? "In Progress" : "Not Started",
  timeline: index === 0 ? "0–3 months" : index === 1 ? "1–6 months" : index === 2 ? "0–2 months" : "0–1 month",
}));

export const formatINR = (value: number) => `₹${value.toLocaleString("en-IN")}`;
