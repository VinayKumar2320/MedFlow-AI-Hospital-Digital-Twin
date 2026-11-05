"""Analytics and bottleneck diagnostic API endpoints."""
from typing import Any, Dict

from fastapi import APIRouter, Query

from simulation.experiments.runner import SimulationExperimentRunner
from simulation.scenarios.scenario_definitions import PROFILES

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/bottlenecks")
def get_bottleneck_analytics(
    hospital_profile: str = Query("urban"),
    arrival_surge_pct: float = Query(0.0),
) -> Dict[str, Any]:
    """Computes operational bottlenecks, queue decomposition, and counterfactual sensitivities."""
    config = PROFILES.get(hospital_profile, PROFILES["urban"])
    runner = SimulationExperimentRunner(config)

    # Run short evaluation simulation
    res = runner.run_single_replication(
        duration_hours=24,
        arrival_surge_pct=arrival_surge_pct,
        seed=42,
    )

    bottlenecks = runner._analyze_bottlenecks(
        {k: {"mean_pct": v} for k, v in res["resource_utilization_pct"].items()},
        res["stage_waits_min"],
        duration_hours=24,
        arrival_surge_pct=arrival_surge_pct,
        seed=42,
    )

    return {
        "hospital_profile": hospital_profile,
        "arrival_surge_pct": arrival_surge_pct,
        "bottlenecks": bottlenecks,
        "stage_wait_decomposition": res["stage_waits_min"],
        "resource_utilization": res["resource_utilization_pct"],
        "waits_by_priority": res["waits_by_priority"],
        "throughput_hourly": res["throughput_per_hour"],
    }
