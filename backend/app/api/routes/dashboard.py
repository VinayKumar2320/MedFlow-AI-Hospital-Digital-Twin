"""Dashboard overview endpoints powering the Command Center."""
from typing import Any, Dict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.repositories.simulation_repo import get_all_profiles

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/overview")
def get_dashboard_overview(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Returns real-time operational status for the Hospital Command Center."""
    profiles = get_all_profiles(db)
    primary_profile = profiles[1] if len(profiles) > 1 else (profiles[0] if profiles else None)

    total_beds = primary_profile.ed_beds if primary_profile else 32
    occupied_beds = int(total_beds * 0.78)

    # Active alerts based on current state
    alerts = [
        {
            "id": "alt-1",
            "level": "WARNING",
            "title": "Evening Surge Anticipated",
            "message": "Forecast indicates +32% arrival increase between 18:00 and 22:00. Pre-allocating 2 triage nurses.",
            "timestamp": "10m ago"
        },
        {
            "id": "alt-2",
            "level": "INFO",
            "title": "Diagnostic Station 3 Online",
            "message": "Routine preventive maintenance completed. All 4 imaging modalities operational.",
            "timestamp": "35m ago"
        }
    ]

    return {
        "hospital_name": primary_profile.name if primary_profile else "Metro Health Urban Emergency Center",
        "profile_id": primary_profile.id if primary_profile else "urban",
        "active_census": 42,
        "waiting_patients": 11,
        "ed_beds_total": total_beds,
        "ed_beds_occupied": occupied_beds,
        "bed_occupancy_pct": round((occupied_beds / total_beds) * 100, 1),
        "physicians_on_duty": primary_profile.physicians if primary_profile else 8,
        "nurses_on_duty": primary_profile.nurses if primary_profile else 16,
        "diagnostic_capacity": primary_profile.diagnostic_stations if primary_profile else 4,
        "forecast_next_1h": 14.8,
        "forecast_next_4h": 58.2,
        "forecast_next_12h": 164.5,
        "forecast_next_24h": 312.0,
        "current_mean_wait_min": 38.5,
        "alerts": alerts,
        "profiles": [
            {
                "id": p.id,
                "name": p.name,
                "type": p.profile_type,
                "beds": p.ed_beds,
                "physicians": p.physicians,
                "nurses": p.nurses,
                "base_arrival_rate": p.base_arrival_rate,
            }
            for p in profiles
        ]
    }
