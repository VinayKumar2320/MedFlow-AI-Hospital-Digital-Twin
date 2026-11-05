"""Simulation API endpoints executing SimPy discrete-event runs and serving results."""
import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models import HospitalProfile, SimulationEvent, SimulationRun
from backend.app.repositories.simulation_repo import get_profile_by_id, get_scenario_by_id
from backend.app.schemas import SimulationRunRequest
from simulation.experiments.runner import SimulationExperimentRunner
from simulation.scenarios.scenario_definitions import PROFILES, HospitalConfig

router = APIRouter(prefix="/simulations", tags=["Simulations"])


def _build_runner_config(profile: Optional[HospitalProfile]) -> HospitalConfig:
    if profile:
        return HospitalConfig(
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
    return PROFILES["urban"]


@router.post("", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
def run_simulation(
    payload: SimulationRunRequest,
    db: Session = Depends(get_db),
):
    """Executes a SimPy discrete-event simulation run and returns statistical metrics."""
    scenario = None
    profile = None

    if payload.scenario_id:
        scenario = get_scenario_by_id(db, payload.scenario_id)
        if scenario:
            profile = scenario.hospital_profile

    if not profile and payload.hospital_profile_id:
        profile = get_profile_by_id(db, payload.hospital_profile_id)

    config = _build_runner_config(profile)
    runner = SimulationExperimentRunner(config)

    # Calculate effective capacity overrides
    surge_pct = payload.arrival_surge_pct
    physician_override = payload.physician_count
    nurse_override = payload.nurse_count
    bed_override = payload.bed_count
    diag_override = payload.diagnostic_count

    if scenario:
        surge_pct = scenario.arrival_surge_pct if surge_pct == 0.0 else surge_pct
        if physician_override is None:
            physician_override = max(1, int(round(config.physicians * scenario.physician_multiplier)))
        if nurse_override is None:
            nurse_override = max(2, int(round(config.nurses * scenario.nurse_multiplier)))
        if bed_override is None:
            bed_override = max(5, config.ed_beds + scenario.bed_delta)
        if diag_override is None:
            diag_override = max(1, config.diagnostic_stations + scenario.diagnostic_delta)

    sim_run = SimulationRun(
        scenario_id=scenario.id if scenario else None,
        status="RUNNING",
        duration_hours=payload.duration_hours,
        random_seed=payload.random_seed,
        replications=payload.replications,
        config_snapshot={
            "hospital": config.name,
            "surge_pct": surge_pct,
            "physicians": physician_override or config.physicians,
            "nurses": nurse_override or config.nurses,
            "beds": bed_override or config.ed_beds,
            "diagnostics": diag_override or config.diagnostic_stations,
        }
    )
    db.add(sim_run)
    db.commit()
    db.refresh(sim_run)

    # Run simulation
    try:
        results = runner.run_multi_replications(
            duration_hours=payload.duration_hours,
            arrival_surge_pct=surge_pct,
            physician_override=physician_override,
            nurse_override=nurse_override,
            bed_override=bed_override,
            diagnostic_override=diag_override,
            replications=payload.replications,
            base_seed=payload.random_seed,
        )

        sim_run.status = "COMPLETED"
        sim_run.finished_at = datetime.datetime.utcnow()
        sim_run.summary_metrics = results
        sim_run.bottlenecks = results.get("bottlenecks", [])

        # Save a sample of events for frontend playback
        events_sample = results.get("events_sample", [])
        for evt in events_sample[:400]:
            event_record = SimulationEvent(
                run_id=sim_run.id,
                timestamp_min=evt["timestamp_min"],
                patient_id=evt["patient_id"],
                priority=evt["priority"],
                stage=evt["stage"],
                event_type=evt["event_type"],
                resource_id=evt.get("resource_id"),
                wait_time_min=evt.get("wait_time_min"),
                queue_length=evt.get("queue_length"),
                active_in_system=evt.get("active_in_system"),
            )
            db.add(event_record)

        db.commit()
        db.refresh(sim_run)

        return {
            "id": sim_run.id,
            "scenario_id": sim_run.scenario_id,
            "status": sim_run.status,
            "duration_hours": sim_run.duration_hours,
            "replications": sim_run.replications,
            "config_snapshot": sim_run.config_snapshot,
            "summary_metrics": sim_run.summary_metrics,
            "bottlenecks": sim_run.bottlenecks,
            "created_at": sim_run.created_at.isoformat(),
            "finished_at": sim_run.finished_at.isoformat() if sim_run.finished_at else None,
        }
    except Exception as e:
        sim_run.status = "FAILED"
        sim_run.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")


@router.get("/{run_id}")
def get_simulation_run(run_id: str, db: Session = Depends(get_db)):
    """Retrieves simulation results and aggregated metrics."""
    run = db.query(SimulationRun).filter(SimulationRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Simulation run not found.")
    return {
        "id": run.id,
        "scenario_id": run.scenario_id,
        "status": run.status,
        "duration_hours": run.duration_hours,
        "replications": run.replications,
        "config_snapshot": run.config_snapshot,
        "summary_metrics": run.summary_metrics,
        "bottlenecks": run.bottlenecks,
        "created_at": run.created_at.isoformat(),
        "finished_at": run.finished_at.isoformat() if run.finished_at else None,
    }


@router.get("/{run_id}/events")
def get_simulation_events(run_id: str, limit: int = 500, db: Session = Depends(get_db)):
    """Retrieves time-ordered simulation events for animated digital twin visualization."""
    events = (
        db.query(SimulationEvent)
        .filter(SimulationEvent.run_id == run_id)
        .order_by(SimulationEvent.timestamp_min.asc())
        .limit(limit)
        .all()
    )
    return [
        {
            "timestamp_min": e.timestamp_min,
            "patient_id": e.patient_id,
            "priority": e.priority,
            "stage": e.stage,
            "event_type": e.event_type,
            "resource_id": e.resource_id,
            "wait_time_min": e.wait_time_min,
            "queue_length": e.queue_length,
            "active_in_system": e.active_in_system,
        }
        for e in events
    ]
