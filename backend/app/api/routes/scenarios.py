"""Scenario management API for configuring what-if operational experiments."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models import HospitalProfile, Scenario
from backend.app.repositories.simulation_repo import get_all_scenarios, get_scenario_by_id
from backend.app.schemas import ScenarioCreate, ScenarioResponse

router = APIRouter(prefix="/scenarios", tags=["Scenarios"])


@router.get("", response_model=List[ScenarioResponse])
def list_scenarios(db: Session = Depends(get_db)):
    """Retrieves all precomputed and custom what-if scenarios."""
    return get_all_scenarios(db)


@router.post("", response_model=ScenarioResponse, status_code=status.HTTP_201_CREATED)
def create_scenario(payload: ScenarioCreate, db: Session = Depends(get_db)):
    """Registers a new what-if experimental scenario."""
    profile = db.query(HospitalProfile).filter(HospitalProfile.id == payload.hospital_profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Hospital profile not found.")

    scenario = Scenario(
        name=payload.name,
        description=payload.description,
        hospital_profile_id=payload.hospital_profile_id,
        arrival_surge_pct=payload.arrival_surge_pct,
        physician_multiplier=payload.physician_multiplier,
        nurse_multiplier=payload.nurse_multiplier,
        bed_delta=payload.bed_delta,
        diagnostic_delta=payload.diagnostic_delta,
        simulation_duration_hours=payload.simulation_duration_hours,
        random_seed=payload.random_seed,
        replications=payload.replications,
        is_precomputed=False,
    )
    db.add(scenario)
    db.commit()
    db.refresh(scenario)
    return scenario


@router.get("/{scenario_id}", response_model=ScenarioResponse)
def get_scenario(scenario_id: str, db: Session = Depends(get_db)):
    """Fetches details of a specific what-if scenario."""
    scenario = get_scenario_by_id(db, scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found.")
    return scenario
