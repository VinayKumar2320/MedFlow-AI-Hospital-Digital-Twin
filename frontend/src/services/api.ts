import {
  DashboardOverview,
  ForecastResponse,
  Scenario,
  SimulationResults,
  SimulationEvent,
  OptimizationResponse,
  Bottleneck,
} from '../types';

// Detect production API URL from Vite environment, falling back to local relative path
const rawApiUrl = import.meta.env.VITE_API_URL || '';
const API_BASE = rawApiUrl ? `${rawApiUrl.replace(/\/+$/, '')}/api/v1` : '/api/v1';

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errorDetail = res.statusText;
    try {
      const errorJson = await res.json();
      errorDetail = errorJson.detail || errorDetail;
    } catch {
      const errorText = await res.text();
      if (errorText) errorDetail = errorText;
    }
    throw new Error(`API Error [${res.status}]: ${errorDetail}`);
  }
  return res.json();
}

export const api = {
  async getDashboardOverview(): Promise<DashboardOverview> {
    const res = await fetch(`${API_BASE}/dashboard/overview`);
    return handleResponse<DashboardOverview>(res);
  },

  async getForecasts(horizonHours = 48, model = 'lightgbm'): Promise<ForecastResponse> {
    const res = await fetch(`${API_BASE}/forecasts?horizon_hours=${horizonHours}&model_name=${model}`);
    return handleResponse<ForecastResponse>(res);
  },

  async getForecastMetrics(): Promise<any> {
    const res = await fetch(`${API_BASE}/forecasts/metrics`);
    return handleResponse<any>(res);
  },

  async getScenarios(): Promise<Scenario[]> {
    const res = await fetch(`${API_BASE}/scenarios`);
    return handleResponse<Scenario[]>(res);
  },

  async runSimulation(payload: {
    scenario_id?: string;
    hospital_profile_id?: string;
    arrival_surge_pct?: number;
    physician_count?: number;
    nurse_count?: number;
    bed_count?: number;
    diagnostic_count?: number;
    duration_hours?: number;
    random_seed?: number;
    replications?: number;
  }): Promise<{ id: string; status: string; summary_metrics: SimulationResults; bottlenecks: Bottleneck[] }> {
    const res = await fetch(`${API_BASE}/simulations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse(res);
  },

  async getSimulation(id: string): Promise<any> {
    const res = await fetch(`${API_BASE}/simulations/${id}`);
    return handleResponse(res);
  },

  async getSimulationEvents(id: string, limit = 500): Promise<SimulationEvent[]> {
    const res = await fetch(`${API_BASE}/simulations/${id}/events?limit=${limit}`);
    return handleResponse<SimulationEvent[]>(res);
  },

  async runOptimization(payload: {
    scenario_id?: string;
    hospital_profile_id?: string;
    max_additional_budget?: number;
    service_target_wait_min?: number;
    replications_for_validation?: number;
  }): Promise<OptimizationResponse> {
    const res = await fetch(`${API_BASE}/optimizations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<OptimizationResponse>(res);
  },

  async getBottlenecks(profile = 'urban', surgePct = 0): Promise<any> {
    const res = await fetch(`${API_BASE}/analytics/bottlenecks?hospital_profile=${profile}&arrival_surge_pct=${surgePct}`);
    return handleResponse(res);
  },

  async getModelMetrics(): Promise<any> {
    const res = await fetch(`${API_BASE}/models/metrics`);
    return handleResponse(res);
  },
};
