export interface HospitalProfile {
  id: string;
  name: string;
  type: string;
  beds: number;
  physicians: number;
  nurses: number;
  base_arrival_rate: number;
}

export interface DashboardOverview {
  hospital_name: string;
  profile_id: string;
  active_census: number;
  waiting_patients: number;
  ed_beds_total: number;
  ed_beds_occupied: number;
  bed_occupancy_pct: number;
  physicians_on_duty: number;
  nurses_on_duty: number;
  diagnostic_capacity: number;
  forecast_next_1h: number;
  forecast_next_4h: number;
  forecast_next_12h: number;
  forecast_next_24h: number;
  current_mean_wait_min: number;
  alerts: Array<{
    id: string;
    level: string;
    title: string;
    message: string;
    timestamp: string;
  }>;
  profiles: HospitalProfile[];
}

export interface ForecastPoint {
  timestamp: string;
  horizon_step: number;
  predicted: number;
  lower_80: number;
  upper_80: number;
  lower_95: number;
  upper_95: number;
  historical?: number;
}

export interface ForecastResponse {
  model_name: string;
  horizon_hours: number;
  points: ForecastPoint[];
  metrics: {
    mae: number;
    rmse: number;
    wape: number;
    bias: number;
    coverage_80_pct?: number;
    coverage_95_pct?: number;
    avg_width_80?: number;
  };
  feature_importance: Array<{
    feature: string;
    importance: number;
  }>;
}

export interface Scenario {
  id: string;
  name: string;
  description: string;
  hospital_profile_id: string;
  arrival_surge_pct: number;
  physician_multiplier: number;
  nurse_multiplier: number;
  bed_delta: number;
  diagnostic_delta: number;
  simulation_duration_hours: number;
  is_precomputed: boolean;
}

export interface SimulationEvent {
  timestamp_min: number;
  patient_id: string;
  priority: number;
  stage: string;
  event_type: string;
  resource_id?: string;
  wait_time_min?: number;
  queue_length?: number;
  active_in_system?: number;
}

export interface MetricCI {
  mean: number;
  ci_lower: number;
  ci_upper: number;
}

export interface Bottleneck {
  resource: string;
  utilization_pct: number;
  average_wait_min: number;
  severity: string;
  counterfactual_wait_reduction_min: number;
  recommendation: string;
}

export interface SimulationResults {
  replications: number;
  duration_hours: number;
  total_arrived: number;
  total_departed: number;
  in_system_at_cutoff: number;
  conservation_verified: boolean;
  throughput_per_hour: MetricCI;
  mean_wait_time: MetricCI;
  median_wait_time: MetricCI;
  p95_wait_time: MetricCI;
  mean_los: MetricCI;
  resource_utilization: Record<string, { mean_pct: number; ci_lower: number; ci_upper: number }>;
  stage_waits: Record<string, number>;
  waits_by_priority: Record<string, { count: number; mean_wait: number; p95_wait: number }>;
  bottlenecks: Bottleneck[];
}

export interface StaffingDetail {
  physicians_morning: number;
  physicians_evening: number;
  physicians_night: number;
  nurses_morning: number;
  nurses_evening: number;
  nurses_night: number;
  effective_total_physicians: number;
  effective_total_nurses: number;
  diagnostic_stations: number;
  additional_beds: number;
  total_ed_beds: number;
}

export interface OptimizationCandidate {
  plan_id: string;
  strategy_name: string;
  budget_tier: string;
  daily_cost: number;
  cost_delta: number;
  staffing: StaffingDetail;
  wait_reduction_minutes: number;
  wait_reduction_pct: number;
  throughput_increase_pct: number;
  cost_effectiveness: number;
}

export interface OptimizationResponse {
  id: string;
  status: string;
  scenario_id?: string;
  target_budget: number;
  current_cost: number;
  recommended_cost: number;
  cost_delta: number;
  wait_reduction_minutes: number;
  wait_reduction_pct: number;
  throughput_increase_pct: number;
  recommended_staffing: StaffingDetail;
  alternative_plans: OptimizationCandidate[];
  tradeoff_frontier: Array<{
    plan_name: string;
    daily_cost: number;
    cost_delta: number;
    mean_wait_min: number;
    p95_wait_min: number;
    throughput_hourly: number;
  }>;
  baseline_metrics: SimulationResults;
}
