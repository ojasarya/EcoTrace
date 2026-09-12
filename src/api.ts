export type DashboardCategory = {
  category: string;
  kg_co2e: string;
  percentage_of_total: string;
};

export type DashboardResponse = {
  factory_id: number;
  calculation_id: number | null;
  total_kg_co2e: string;
  categories: DashboardCategory[];
  hotspots: Array<{
    category: string;
    source: string;
    kg_co2e: string;
    percentage_of_total: string;
    severity: string;
    rank: number;
    explanation: string;
  }>;
  recommendations: unknown[];
  roadmap: unknown[];
};

const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1").replace(/\/$/, "");
const factoryId = import.meta.env.VITE_FACTORY_ID ?? "1";

export async function fetchDashboard(): Promise<DashboardResponse> {
  const response = await fetch(`${apiBaseUrl}/factories/${factoryId}/dashboard`);
  if (!response.ok) {
    throw new Error(`Dashboard request failed (${response.status})`);
  }
  return response.json() as Promise<DashboardResponse>;
}
