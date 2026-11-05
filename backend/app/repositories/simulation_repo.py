"""Database repository functions for profiles, scenarios, simulation runs, and optimizations."""
from typing import List, Optional

from sqlalchemy.orm import Session

from backend.app.models import HospitalProfile, Scenario
from simulation.scenarios.scenario_definitions import PROFILES, SCENARIO_PRESETS


def seed_initial_data(db: Session):
    """Seeds default hospital profiles and scenario presets if the database is empty."""
    if db.query(HospitalProfile).count() == 0:
        created_profiles = {}
        for key, p in PROFILES.items():
            profile_model = HospitalProfile(
                name=p.name,
                profile_type=p.profile_type,
                description=p.description,
                ed_beds=p.ed_beds,
                physicians=p.physicians,
                nurses=p.nurses,
                triage_nurses=p.triage_nurses,
                diagnostic_stations=p.diagnostic_stations,
                observation_beds=p.observation_beds,
                registration_clerks=p.registration_clerks,
                base_arrival_rate=p.base_arrival_rate,
            )
            db.add(profile_model)
            db.flush()
            created_profiles[key] = profile_model.id

        # Seed scenario presets attached to urban profile
        urban_id = created_profiles.get("urban")
        if urban_id:
            for s_key, s in SCENARIO_PRESETS.items():
                scen = Scenario(
                    name=s.name,
                    description=s.description,
                    hospital_profile_id=urban_id,
                    arrival_surge_pct=s.arrival_surge_pct,
                    physician_multiplier=s.physician_multiplier,
                    nurse_multiplier=s.nurse_multiplier,
                    bed_delta=s.bed_delta,
                    diagnostic_delta=s.diagnostic_delta,
                    simulation_duration_hours=s.duration_hours,
                    is_precomputed=True,
                )
                db.add(scen)
        db.commit()


def get_all_profiles(db: Session) -> List[HospitalProfile]:
    return db.query(HospitalProfile).all()


def get_profile_by_id(db: Session, profile_id: str) -> Optional[HospitalProfile]:
    return db.query(HospitalProfile).filter(HospitalProfile.id == profile_id).first()


def get_all_scenarios(db: Session) -> List[Scenario]:
    return db.query(Scenario).all()


def get_scenario_by_id(db: Session, scenario_id: str) -> Optional[Scenario]:
    return db.query(Scenario).filter(Scenario.id == scenario_id).first()
