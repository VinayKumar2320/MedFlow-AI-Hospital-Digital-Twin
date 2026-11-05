"""Pydantic schemas for request validation and response serialization."""
import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# --- Hospital Profile Schemas ---
class HospitalProfileBase(BaseModel):
    name: str
    profile_type: str = "urban"
    description: Optional[str] = None
    ed_beds: int = Field(ge=5, le=200, default=30)
    physicians: int = Field(ge=1, le=50, default=8)
    nurses: int = Field(ge=2, le=100, default=16)
    triage_nurses: int = Field(ge=1, le=20, default=3)
    diagnostic_stations: int = Field(ge=1, le=20, default=4)
    observation_beds: int = Field(ge=0, le=50, default=10)
    registration_clerks: int = Field(ge=1, le=15, default=3)
    base_arrival_rate: float = Field(gt=0, default=12.5)


class HospitalProfileCreate(HospitalProfileBase):
    pass


class HospitalProfileResponse(HospitalProfileBase):
    id: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True


# --- Scenario Schemas ---
class ScenarioBase(BaseModel):
    name: str
    description: Optional[str] = None
    hospital_profile_id: str
    arrival_surge_pct: float = Field(default=0.0, ge=-50.0, le=200.0)
    physician_multiplier: float = Field(default=1.0, ge=0.1, le=3.0)
    nurse_multiplier: float = Field(default=1.0, ge=0.1, le=3.0)
    bed_delta: int = Field(default=0, ge=-50, le=50)
    diagnostic_delta: int = Field(default=0, ge=-10, le=10)
    simulation_duration_hours: int = Field(default=48, ge=6, le=168)
    random_seed: int = Field(default=42)
    replications: int = Field(default=5, ge=1, le=20)


class ScenarioCreate(ScenarioBase):
    pass


class ScenarioResponse(ScenarioBase):
    id: str
    is_precomputed: bool
    created_at: datetime.datetime

    class Config:
        from_attributes = True


# --- Simulation Schemas ---
class SimulationRunRequest(BaseModel):
    scenario_id: Optional[str] = None
    hospital_profile_id: Optional[str] = None
    # Ad-hoc overrides
    arrival_surge_pct: float = 0.0
    physician_count: Optional[int] = None
    nurse_count: Optional[int] = None
    bed_count: Optional[int] = None
    diagnostic_count: Optional[int] = None
    duration_hours: int = Field(default=48, ge=6, le=168)
    random_seed: int = 42
    replications: int = Field(default=5, ge=1, le=20)


class MetricDetail(BaseModel):
    mean: float
    median: float
    p90: float
    p95: float
    ci_lower: float
    ci_upper: float
    unit: str


class BottleneckResource(BaseModel):
    resource: str
    utilization_pct: float
    average_wait_min: float
    queue_p95: float
    severity: str  # CRITICAL, ELEVATED, NORMAL
    counterfactual_wait_reduction_min: float
    recommendation: str


class SimulationRunResponse(BaseModel):
    id: str
    scenario_id: Optional[str]
    status: str
    duration_hours: int
    random_seed: int
    replications: int
    summary_metrics: Optional[Dict[str, Any]] = None
    bottlenecks: Optional[List[Dict[str, Any]]] = None
    created_at: datetime.datetime
    finished_at: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True


class SimulationEventResponse(BaseModel):
    id: str
    timestamp_min: float
    patient_id: str
    priority: int
    stage: str
    event_type: str
    resource_id: Optional[str] = None
    wait_time_min: Optional[float] = None
    queue_length: Optional[int] = None
    active_in_system: Optional[int] = None

    class Config:
        from_attributes = True


# --- Optimization Schemas ---
class OptimizationRequest(BaseModel):
    scenario_id: Optional[str] = None
    hospital_profile_id: Optional[str] = None
    max_additional_budget: float = Field(default=10000.0, ge=0.0)
    service_target_wait_min: float = Field(default=60.0, ge=15.0)
    shift_hours: int = 8
    replications_for_validation: int = Field(default=5, ge=2, le=15)


class StaffingRecommendation(BaseModel):
    physicians_morning: int
    physicians_evening: int
    physicians_night: int
    nurses_morning: int
    nurses_evening: int
    nurses_night: int
    diagnostic_stations: int
    additional_beds: int
    hourly_cost_est: float
    budget_utilized: float


class OptimizationResponse(BaseModel):
    id: str
    status: str
    scenario_id: Optional[str]
    target_budget: float
    current_cost: float
    recommended_cost: float
    cost_delta: float
    wait_reduction_minutes: float
    wait_reduction_pct: float
    throughput_increase_pct: float
    baseline_metrics: Dict[str, Any]
    optimized_metrics: Dict[str, Any]
    recommended_staffing: Dict[str, Any]
    alternative_plans: List[Dict[str, Any]]
    tradeoff_frontier: List[Dict[str, Any]]
    confidence_intervals: Dict[str, Any]
    created_at: datetime.datetime


# --- Forecast Schemas ---
class ForecastRequest(BaseModel):
    horizon_hours: int = Field(default=24, ge=1, le=72)
    model_name: str = "lightgbm"  # seasonal_naive, poisson, lightgbm, xgboost


class ForecastPoint(BaseModel):
    timestamp: str
    horizon_step: int
    predicted: float
    lower_80: float
    upper_80: float
    lower_95: float
    upper_95: float
    historical: Optional[float] = None


class ForecastResponse(BaseModel):
    model_name: str
    generated_at: str
    horizon_hours: int
    points: List[ForecastPoint]
    metrics: Dict[str, Any]
    feature_importance: List[Dict[str, Any]]
