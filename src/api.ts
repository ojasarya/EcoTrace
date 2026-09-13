export type DashboardCategory = {
  category: string;
  kg_co2e: string;
  percentage_of_total: string;
};

export type DashboardRecommendation = {
  id: number;
  name: string;
  category: string;
  target_source: string;
  description: string;
  estimated_reduction_kg_co2e: string;
  estimated_cost: string;
  carbon_roi_kg_co2e_per_cost: string | null;
  feasibility: string;
  urgency: string;
  priority_score: string | number | null;
  rationale?: string | null;
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
  recommendations: DashboardRecommendation[];
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

export type FactoryCreatePayload = {
  name: string;
  industry_type: string;
  location: string;
  production_unit: string;
};

export async function createFactory(payload: FactoryCreatePayload): Promise<Factory> {
  const response = await fetch(`${apiBaseUrl}/factories`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(getAccessToken() ? { Authorization: `Bearer ${getAccessToken()}` } : {}),
    },
    body: JSON.stringify(payload),
  });
  if (response.status === 401 && getAccessToken()) clearAccessToken();
  if (!response.ok) {
    throw new Error(`Factory creation failed (${response.status})`);
  }
  return response.json() as Promise<Factory>;
}

export type FactoryUpdatePayload = Partial<FactoryCreatePayload>;

export async function updateFactory(factoryId: number, payload: FactoryUpdatePayload): Promise<Factory> {
  const response = await fetch(`${apiBaseUrl}/factories/${factoryId}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      ...(getAccessToken() ? { Authorization: `Bearer ${getAccessToken()}` } : {}),
    },
    body: JSON.stringify(payload),
  });
  if (response.status === 401 && getAccessToken()) clearAccessToken();
  if (!response.ok) {
    throw new Error(`Factory update failed (${response.status})`);
  }
  return response.json() as Promise<Factory>;
}

export type ReportingPeriodCreatePayload = {
  period_start: string;
  period_end: string;
  production_quantity: number;
  production_unit: string;
};

export type ReportingPeriod = {
  id: number;
  factory_id: number;
  period_start: string;
  period_end: string;
  production_quantity: number;
  production_unit: string;
};

export async function createReportingPeriod(factoryId: number, payload: ReportingPeriodCreatePayload): Promise<ReportingPeriod> {
  const response = await fetch(`${apiBaseUrl}/factories/${factoryId}/periods`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(getAccessToken() ? { Authorization: `Bearer ${getAccessToken()}` } : {}),
    },
    body: JSON.stringify(payload),
  });
  if (response.status === 401 && getAccessToken()) clearAccessToken();
  if (!response.ok) {
    throw new Error(`Reporting period creation failed (${response.status})`);
  }
  return response.json() as Promise<ReportingPeriod>;
}

export type ActivityPayload = {
  source: string;
  quantity: number;
  unit: string;
  renewable_percentage?: number;
};

export async function createEnergyUsage(factoryId: number, periodId: number, payload: ActivityPayload): Promise<unknown> {
  const response = await fetch(`${apiBaseUrl}/factories/${factoryId}/periods/${periodId}/energy`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(getAccessToken() ? { Authorization: `Bearer ${getAccessToken()}` } : {}),
    },
    body: JSON.stringify(payload),
  });
  if (response.status === 401 && getAccessToken()) clearAccessToken();
  if (!response.ok) {
    throw new Error(`Energy usage creation failed (${response.status})`);
  }
  return response.json();
}

export async function createMaterialUsage(factoryId: number, periodId: number, payload: {
  material_name: string;
  material_type: string;
  quantity: number;
  unit: string;
  recycled_content_percentage?: number;
}): Promise<unknown> {
  const response = await fetch(`${apiBaseUrl}/factories/${factoryId}/periods/${periodId}/materials`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(getAccessToken() ? { Authorization: `Bearer ${getAccessToken()}` } : {}),
    },
    body: JSON.stringify(payload),
  });
  if (response.status === 401 && getAccessToken()) clearAccessToken();
  if (!response.ok) {
    throw new Error(`Material usage creation failed (${response.status})`);
  }
  return response.json();
}

export async function createWasteRecord(factoryId: number, periodId: number, payload: {
  waste_type: string;
  quantity: number;
  unit: string;
  disposal_method: string;
  recycled_quantity?: number;
}): Promise<unknown> {
  const response = await fetch(`${apiBaseUrl}/factories/${factoryId}/periods/${periodId}/waste`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(getAccessToken() ? { Authorization: `Bearer ${getAccessToken()}` } : {}),
    },
    body: JSON.stringify(payload),
  });
  if (response.status === 401 && getAccessToken()) clearAccessToken();
  if (!response.ok) {
    throw new Error(`Waste record creation failed (${response.status})`);
  }
  return response.json();
}

export async function createTransportationActivity(factoryId: number, periodId: number, payload: {
  mode: string;
  direction: string;
  distance: number;
  distance_unit: string;
  load_quantity: number;
  load_unit: string;
}): Promise<unknown> {
  const response = await fetch(`${apiBaseUrl}/factories/${factoryId}/periods/${periodId}/transportation`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(getAccessToken() ? { Authorization: `Bearer ${getAccessToken()}` } : {}),
    },
    body: JSON.stringify(payload),
  });
  if (response.status === 401 && getAccessToken()) clearAccessToken();
  if (!response.ok) {
    throw new Error(`Transportation activity creation failed (${response.status})`);
  }
  return response.json();
}

export async function fetchDashboard(selectedFactoryId = factoryId): Promise<DashboardResponse> {
  const response = await authorizedFetch(`/factories/${selectedFactoryId}/dashboard`);
  if (!response.ok) {
    throw new Error(`Dashboard request failed (${response.status})`);
  }
  return response.json() as Promise<DashboardResponse>;
}

export type ApiAnomaly = {
  calculation_id: number;
  total_kg_co2e: string;
  is_anomaly: boolean;
  anomaly_score: string;
  explanation: string;
};

export async function fetchAnomalies(selectedFactoryId: number): Promise<ApiAnomaly[]> {
  const response = await authorizedFetch(`/factories/${selectedFactoryId}/anomalies`);
  if (!response.ok) {
    throw new Error(`Anomaly request failed (${response.status})`);
  }
  return response.json() as Promise<ApiAnomaly[]>;
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

export type ApiPersistedRoadmapAction = {
  id: number;
  factory_id: number;
  calculation_id: number;
  intervention_id: number;
  status: string;
  planned_start_date: string | null;
  owner: string | null;
  actual_cost: string | null;
  actual_reduction_kg_co2e: string | null;
};

export async function fetchRoadmapActions(factoryId: number): Promise<ApiPersistedRoadmapAction[]> {
  const response = await authorizedFetch(`/factories/${factoryId}/roadmap-actions`);
  if (!response.ok) {
    throw new Error(`Roadmap action request failed (${response.status})`);
  }
  return response.json() as Promise<ApiPersistedRoadmapAction[]>;
}

export async function createRoadmapAction(factoryId: number, payload: {
  calculation_id: number;
  intervention_id: number;
  status?: string;
}): Promise<ApiPersistedRoadmapAction> {
  const response = await fetch(`${apiBaseUrl}/factories/${factoryId}/roadmap-actions`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(getAccessToken() ? { Authorization: `Bearer ${getAccessToken()}` } : {}),
    },
    body: JSON.stringify(payload),
  });
  if (response.status === 401 && getAccessToken()) clearAccessToken();
  if (!response.ok) {
    throw new Error(`Roadmap action creation failed (${response.status})`);
  }
  return response.json() as Promise<ApiPersistedRoadmapAction>;
}

export async function updateRoadmapAction(factoryId: number, actionId: number, status: string): Promise<ApiPersistedRoadmapAction> {
  const response = await fetch(`${apiBaseUrl}/factories/${factoryId}/roadmap-actions/${actionId}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      ...(getAccessToken() ? { Authorization: `Bearer ${getAccessToken()}` } : {}),
    },
    body: JSON.stringify({ status }),
  });
  if (response.status === 401 && getAccessToken()) clearAccessToken();
  if (!response.ok) {
    throw new Error(`Roadmap action update failed (${response.status})`);
  }
  return response.json() as Promise<ApiPersistedRoadmapAction>;
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
