"""SQLAlchemy models for MedFlow."""
import datetime
import uuid

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from backend.app.core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class HospitalProfile(Base):
    __tablename__ = "hospital_profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    profile_type = Column(String(50), nullable=False)  # community, urban, metropolitan
    description = Column(Text, nullable=True)

    # Capacity Configuration
    ed_beds = Column(Integer, nullable=False, default=30)
    physicians = Column(Integer, nullable=False, default=8)
    nurses = Column(Integer, nullable=False, default=16)
    triage_nurses = Column(Integer, nullable=False, default=3)
    diagnostic_stations = Column(Integer, nullable=False, default=4)
    observation_beds = Column(Integer, nullable=False, default=10)
    registration_clerks = Column(Integer, nullable=False, default=3)

    # Baseline arrival rate (patients per hour)
    base_arrival_rate = Column(Float, nullable=False, default=12.5)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    scenarios = relationship("Scenario", back_populates="hospital_profile", cascade="all, delete-orphan")


class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    hospital_profile_id = Column(String(36), ForeignKey("hospital_profiles.id"), nullable=False)

    # Disruption / What-If Multipliers & Deltas
    arrival_surge_pct = Column(Float, default=0.0)      # e.g., +40%
    physician_multiplier = Column(Float, default=1.0)   # e.g., 0.8 for 20% shortage
    nurse_multiplier = Column(Float, default=1.0)       # e.g., 0.8
    bed_delta = Column(Integer, default=0)              # e.g., -5 beds
    diagnostic_delta = Column(Integer, default=0)       # e.g., -1 station

    simulation_duration_hours = Column(Integer, default=48)
    random_seed = Column(Integer, default=42)
    replications = Column(Integer, default=5)
    is_precomputed = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    hospital_profile = relationship("HospitalProfile", back_populates="scenarios")
    simulation_runs = relationship("SimulationRun", back_populates="scenario", cascade="all, delete-orphan")
    optimizations = relationship("OptimizationRun", back_populates="scenario", cascade="all, delete-orphan")


class SimulationRun(Base):
    __tablename__ = "simulation_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    scenario_id = Column(String(36), ForeignKey("scenarios.id"), nullable=True)
    status = Column(String(30), default="PENDING")  # PENDING, RUNNING, COMPLETED, FAILED

    duration_hours = Column(Integer, default=48)
    random_seed = Column(Integer, default=42)
    replications = Column(Integer, default=5)

    # Full config snapshot stored as JSON
    config_snapshot = Column(JSON, nullable=True)

    # Summary Metrics JSON cache
    summary_metrics = Column(JSON, nullable=True)

    # Bottleneck Analysis JSON cache
    bottlenecks = Column(JSON, nullable=True)

    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)

    scenario = relationship("Scenario", back_populates="simulation_runs")
    events = relationship("SimulationEvent", back_populates="simulation_run", cascade="all, delete-orphan")


class SimulationEvent(Base):
    __tablename__ = "simulation_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    run_id = Column(String(36), ForeignKey("simulation_runs.id"), nullable=False, index=True)
    timestamp_min = Column(Float, nullable=False, index=True)
    patient_id = Column(String(50), nullable=False)
    priority = Column(Integer, nullable=False)  # ESI 1 to 5
    stage = Column(String(50), nullable=False)  # ARRIVAL, REGISTRATION, TRIAGE, ASSESSMENT, DIAGNOSTICS, TREATMENT, OBSERVATION, DEPARTURE
    event_type = Column(String(50), nullable=False)  # QUEUE_ENTER, SERVICE_START, SERVICE_COMPLETE, TRANSFER, DEPARTURE
    resource_id = Column(String(50), nullable=True)
    wait_time_min = Column(Float, nullable=True)
    queue_length = Column(Integer, nullable=True)
    active_in_system = Column(Integer, nullable=True)

    simulation_run = relationship("SimulationRun", back_populates="events")


class OptimizationRun(Base):
    __tablename__ = "optimization_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    scenario_id = Column(String(36), ForeignKey("scenarios.id"), nullable=True)
    status = Column(String(30), default="PENDING")  # PENDING, SOLVING, EVALUATING, COMPLETED, FAILED

    target_budget = Column(Float, nullable=False, default=15000.0)
    current_cost = Column(Float, nullable=True)
    recommended_cost = Column(Float, nullable=True)
    cost_delta = Column(Float, nullable=True)

    # Expected improvements verified via SimPy replications
    wait_reduction_minutes = Column(Float, nullable=True)
    wait_reduction_pct = Column(Float, nullable=True)
    throughput_increase_pct = Column(Float, nullable=True)
    baseline_metrics = Column(JSON, nullable=True)
    optimized_metrics = Column(JSON, nullable=True)

    # Detailed staffing recommendation
    recommended_staffing = Column(JSON, nullable=True)
    alternative_plans = Column(JSON, nullable=True)
    tradeoff_frontier = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)

    scenario = relationship("Scenario", back_populates="optimizations")


class ForecastModelRun(Base):
    __tablename__ = "forecast_model_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    model_name = Column(String(50), nullable=False)  # seasonal_naive, poisson, lightgbm, xgboost
    dataset_records = Column(Integer, default=0)

    # Metrics across horizons
    mae_1h = Column(Float, nullable=True)
    rmse_1h = Column(Float, nullable=True)
    wape_1h = Column(Float, nullable=True)
    coverage_80_1h = Column(Float, nullable=True)

    mae_4h = Column(Float, nullable=True)
    mae_12h = Column(Float, nullable=True)
    mae_24h = Column(Float, nullable=True)

    feature_importance = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
