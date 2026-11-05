"""Optimization API endpoints executing Google OR-Tools CP-SAT and SimPy validation."""
import datetime
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models import OptimizationRun
from backend.app.repositories.simulation_repo import get_profile_by_id, get_scenario_by_id
from backend.app.schemas import OptimizationRequest
from optimization.evaluation.evaluator import OptimizationEvaluator
from simulation.scenarios.scenario_definitions import PROFILES, HospitalConfig

router = APIRouter(prefix="/optimizations", tags=["Optimization"])


@router.post("", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
def run_optimization(
    payload: OptimizationRequest,
    db: Session = Depends(get_db),
):
    """Executes OR-Tools CP-SAT multi-shift solver and evaluates candidate plans with SimPy."""
    scenario = None
    profile = None

    if payload.scenario_id:
        scenario = get_scenario_by_id(db, payload.scenario_id)
        if scenario:
            profile = scenario.hospital_profile

    if not profile and payload.hospital_profile_id:
        profile = get_profile_by_id(db, payload.hospital_profile_id)

    config = PROFILES["urban"]
    if profile:
        config = HospitalConfig(
            name=profile.name,
            profile_type=profile.profile_type,
            ed_beds=profile.ed_beds,
            physicians=profile.physicians,
            nurses=profile.nurses,
            triage_nurses=profile.triage_nurses,
            diagnostic_stations=profile.diagnostic_stations,
            observation_beds=profile.observation_beds,
            registration_clerks=profile.registration_clerks,
            base_arrival_rate=profile.base_arrival_rate,
            description=profile.description or "",
        )

    evaluator = OptimizationEvaluator(config)
    surge_pct = scenario.arrival_surge_pct if scenario else 0.0

    opt_run = OptimizationRun(
        scenario_id=scenario.id if scenario else None,
        status="SOLVING",
        target_budget=payload.max_additional_budget,
    )
    db.add(opt_run)
    db.commit()
    db.refresh(opt_run)

    try:
        results = evaluator.evaluate_optimization(
            max_additional_daily_budget=payload.max_additional_budget,
            arrival_surge_pct=surge_pct,
            replications=payload.replications_for_validation,
            duration_hours=24,
            base_seed=42,
        )

        best = results["recommended_plan"]
        opt_run.status = "COMPLETED"
        opt_run.current_cost = results["baseline_daily_cost"]
        opt_run.recommended_cost = best["daily_cost"]
        opt_run.cost_delta = best["cost_delta"]
        opt_run.wait_reduction_minutes = best["wait_reduction_minutes"]
        opt_run.wait_reduction_pct = best["wait_reduction_pct"]
        opt_run.throughput_increase_pct = best["throughput_increase_pct"]
        opt_run.baseline_metrics = results["baseline_metrics"]
        opt_run.optimized_metrics = best["simulation_results"]
        opt_run.recommended_staffing = best["staffing"]
        opt_run.alternative_plans = results["all_evaluated_plans"]
        opt_run.tradeoff_frontier = results["tradeoff_frontier"]
        opt_run.finished_at = datetime.datetime.utcnow()

        db.commit()
        db.refresh(opt_run)

        return {
            "id": opt_run.id,
            "status": opt_run.status,
            "scenario_id": opt_run.scenario_id,
            "target_budget": opt_run.target_budget,
            "current_cost": opt_run.current_cost,
            "recommended_cost": opt_run.recommended_cost,
            "cost_delta": opt_run.cost_delta,
            "wait_reduction_minutes": opt_run.wait_reduction_minutes,
            "wait_reduction_pct": opt_run.wait_reduction_pct,
            "throughput_increase_pct": opt_run.throughput_increase_pct,
            "recommended_staffing": opt_run.recommended_staffing,
            "alternative_plans": opt_run.alternative_plans,
            "tradeoff_frontier": opt_run.tradeoff_frontier,
            "baseline_metrics": opt_run.baseline_metrics,
            "created_at": opt_run.created_at.isoformat(),
        }
    except Exception as e:
        opt_run.status = "FAILED"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")


@router.get("/{opt_id}")
def get_optimization_run(opt_id: str, db: Session = Depends(get_db)):
    """Retrieves optimization recommendations and comparison details."""
    run = db.query(OptimizationRun).filter(OptimizationRun.id == opt_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Optimization run not found.")
    return {
        "id": run.id,
        "status": run.status,
        "scenario_id": run.scenario_id,
        "target_budget": run.target_budget,
        "current_cost": run.current_cost,
        "recommended_cost": run.recommended_cost,
        "cost_delta": run.cost_delta,
        "wait_reduction_minutes": run.wait_reduction_minutes,
        "wait_reduction_pct": run.wait_reduction_pct,
        "throughput_increase_pct": run.throughput_increase_pct,
        "recommended_staffing": run.recommended_staffing,
        "alternative_plans": run.alternative_plans,
        "tradeoff_frontier": run.tradeoff_frontier,
        "baseline_metrics": run.baseline_metrics,
        "created_at": run.created_at.isoformat(),
    }
