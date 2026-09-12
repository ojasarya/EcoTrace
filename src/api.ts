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
const tokenKey = "ecotrace_access_token";

export type AuthUser = {
  id: number;
  email: string;
  is_active: boolean;
};

export type Factory = {
  id: number;
  name: string;
  industry_type: string;
  location: string;
  production_unit: string;
};

export function getAccessToken(): string | null {
  return window.localStorage.getItem(tokenKey);
}

export function clearAccessToken(): void {
  window.localStorage.removeItem(tokenKey);
}

export async function login(email: string, password: string): Promise<AuthUser> {
  const response = await fetch(`${apiBaseUrl}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!response.ok) {
    throw new Error(response.status === 401 ? "Invalid email or password" : `Login failed (${response.status})`);
  }
  const result = await response.json() as { access_token: string; user: AuthUser };
  window.localStorage.setItem(tokenKey, result.access_token);
  return result.user;
}

export async function register(email: string, password: string): Promise<AuthUser> {
  const response = await fetch(`${apiBaseUrl}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!response.ok) {
    throw new Error(response.status === 409 ? "An account with this email already exists" : `Registration failed (${response.status})`);
  }
  return login(email, password);
}

async function authorizedFetch(path: string): Promise<Response> {
  const token = getAccessToken();
  const response = await fetch(`${apiBaseUrl}${path}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (response.status === 401 && token) {
    clearAccessToken();
  }
  return response;
}

export async function fetchFactories(): Promise<Factory[]> {
  const response = await authorizedFetch("/factories");
  if (!response.ok) {
    throw new Error(`Factory request failed (${response.status})`);
  }
  return response.json() as Promise<Factory[]>;
}

export async function fetchDashboard(selectedFactoryId = factoryId): Promise<DashboardResponse> {
  const response = await authorizedFetch(`/factories/${selectedFactoryId}/dashboard`);
  if (!response.ok) {
    throw new Error(`Dashboard request failed (${response.status})`);
  }
  return response.json() as Promise<DashboardResponse>;
}

export type ApiCalculationBreakdown = {
  id: number;
  calculation_id: number;
  category: string;
  source: string;
  activity_quantity: string;
  activity_unit: string;
  applied_factor: string;
  kg_co2e: string;
  percentage_of_total: string;
  explanation: string | null;
};

export type ApiCalculation = {
  id: number;
  reporting_period_id: number;
  total_kg_co2e: string;
  calculation_version: string;
  status: string;
  breakdown: ApiCalculationBreakdown[];
};

export async function fetchCalculation(calculationId: number): Promise<ApiCalculation> {
  const response = await authorizedFetch(`/calculations/${calculationId}`);
  if (!response.ok) {
    throw new Error(`Calculation request failed (${response.status})`);
  }
  return response.json() as Promise<ApiCalculation>;
}

export type ApiHotspot = DashboardResponse["hotspots"][number];

export async function fetchHotspots(calculationId: number): Promise<ApiHotspot[]> {
  const response = await authorizedFetch(`/calculations/${calculationId}/hotspots`);
  if (!response.ok) {
    throw new Error(`Hotspot request failed (${response.status})`);
  }
  return response.json() as Promise<ApiHotspot[]>;
}

export type ApiRoadmapAction = {
  sequence: number;
  recommendation_rank: number;
  intervention_id: number;
  intervention_name: string;
  target_source: string;
  phase: string;
  estimated_cost: string;
  estimated_reduction_kg_co2e: string;
  cumulative_cost: string;
  cumulative_reduction_kg_co2e: string;
  rationale: string;
};

export type ApiRoadmap = {
  calculation_id: number;
  total_actions: number;
  total_estimated_cost: string;
  total_estimated_reduction_kg_co2e: string;
  actions: ApiRoadmapAction[];
};

export async function fetchRoadmap(calculationId: number): Promise<ApiRoadmap> {
  const response = await authorizedFetch(`/calculations/${calculationId}/roadmap`);
  if (!response.ok) {
    throw new Error(`Roadmap request failed (${response.status})`);
  }
  return response.json() as Promise<ApiRoadmap>;
}

export type ApiSimulation = {
  calculation_id: number;
  baseline_kg_co2e: string;
  simulated_kg_co2e: string;
  reduction_kg_co2e: string;
  reduction_percentage: string;
  breakdown: Array<{ category: string; source: string; simulated_kg_co2e: string }>;
};

export async function simulateCalculation(
  calculationId: number,
  adjustments: Array<{ category: string; source: string; reduction_percentage: number }>,
): Promise<ApiSimulation> {
  const response = await fetch(`${apiBaseUrl}/calculations/${calculationId}/simulate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(getAccessToken() ? { Authorization: `Bearer ${getAccessToken()}` } : {}),
    },
    body: JSON.stringify({ adjustments }),
  });
  if (response.status === 401 && getAccessToken()) clearAccessToken();
  if (!response.ok) {
    throw new Error(`Simulation request failed (${response.status})`);
  }
  return response.json() as Promise<ApiSimulation>;
}

export type ApiRecommendation = {
  id: number;
  name: string;
  category: string;
  description: string;
  estimated_cost: string;
  estimated_reduction_kg_co2e: string;
  carbon_roi_kg_co2e_per_cost: string | null;
  feasibility: string;
  urgency: string;
  priority_score: string;
};

export async function fetchRecommendations(calculationId: number): Promise<ApiRecommendation[]> {
  const response = await authorizedFetch(`/calculations/${calculationId}/recommendations`);
  if (!response.ok) {
    throw new Error(`Recommendation request failed (${response.status})`);
  }
  return response.json() as Promise<ApiRecommendation[]>;
}

export async function downloadCalculationCsv(calculationId: number): Promise<void> {
  const response = await authorizedFetch(`/calculations/${calculationId}/export.csv`);
  if (!response.ok) {
    throw new Error(`Report request failed (${response.status})`);
  }
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `ecotrace-calculation-${calculationId}.csv`;
  link.click();
  URL.revokeObjectURL(url);
}
