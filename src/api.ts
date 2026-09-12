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
