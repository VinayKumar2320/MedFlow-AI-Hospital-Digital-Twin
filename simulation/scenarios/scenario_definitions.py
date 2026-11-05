"""Hospital operational profiles and canonical what-if scenario presets."""
from dataclasses import dataclass
from typing import Dict


@dataclass
class HospitalConfig:
    name: str
    profile_type: str
    ed_beds: int
    physicians: int
    nurses: int
    triage_nurses: int
    diagnostic_stations: int
    observation_beds: int
    registration_clerks: int
    base_arrival_rate: float
    description: str


PROFILES: Dict[str, HospitalConfig] = {
    "community": HospitalConfig(
        name="Valley Community Hospital",
        profile_type="community",
        ed_beds=15,
        physicians=3,
        nurses=7,
        triage_nurses=2,
        diagnostic_stations=2,
        observation_beds=4,
        registration_clerks=2,
        base_arrival_rate=5.5,
        description="Small rural community hospital with limited trauma and imaging capabilities."
    ),
    "urban": HospitalConfig(
        name="Metro Health Urban Emergency Center",
        profile_type="urban",
        ed_beds=32,
        physicians=8,
        nurses=16,
        triage_nurses=3,
        diagnostic_stations=4,
        observation_beds=10,
        registration_clerks=3,
        base_arrival_rate=12.5,
        description="Medium urban general hospital handling high patient volume with full diagnostic labs."
    ),
    "metropolitan": HospitalConfig(
        name="St. Jude Academic Medical Center",
        profile_type="metropolitan",
        ed_beds=75,
        physicians=18,
        nurses=42,
        triage_nurses=6,
        diagnostic_stations=8,
        observation_beds=24,
        registration_clerks=5,
        base_arrival_rate=28.0,
        description="Tier-1 academic trauma center operating 24/7 with specialized resuscitation bays."
    )
}


@dataclass
class ScenarioPreset:
    id: str
    name: str
    description: str
    profile_key: str
    arrival_surge_pct: float = 0.0
    physician_multiplier: float = 1.0
    nurse_multiplier: float = 1.0
    bed_delta: int = 0
    diagnostic_delta: int = 0
    duration_hours: int = 48


SCENARIO_PRESETS: Dict[str, ScenarioPreset] = {
    "baseline": ScenarioPreset(
        id="baseline",
        name="Baseline Operating Conditions",
        description="Standard operational tempo with nominal staffing and diurnal demand.",
        profile_key="urban",
        arrival_surge_pct=0.0,
    ),
    "surge_40": ScenarioPreset(
        id="surge_40",
        name="Scenario A: Sudden Patient Surge (+40%)",
        description="Sudden 40% influx in patient volume simulating an epidemic spike or mass gathering.",
        profile_key="urban",
        arrival_surge_pct=40.0,
    ),
    "nurse_shortage": ScenarioPreset(
        id="nurse_shortage",
        name="Scenario B: Nurse Shortage (-20%)",
        description="Unexpected 20% absenteeism in nursing staff resulting in treatment bottleneck.",
        profile_key="urban",
        nurse_multiplier=0.8,
    ),
    "bed_closure": ScenarioPreset(
        id="bed_closure",
        name="Scenario C: Treatment Bed Closure (-5 Beds)",
        description="Temporary physical closure of 5 treatment beds due to sanitation or maintenance.",
        profile_key="urban",
        bed_delta=-5,
    ),
    "seasonal_surge": ScenarioPreset(
        id="seasonal_surge",
        name="Scenario D: Seasonal Winter Respiratory Surge",
        description="Prolonged 25% surge with high volume of respiratory admissions.",
        profile_key="urban",
        arrival_surge_pct=25.0,
    ),
    "diagnostic_outage": ScenarioPreset(
        id="diagnostic_outage",
        name="Scenario E: Diagnostic Station Bottleneck (-2 CT/X-Ray)",
        description="Imaging equipment malfunction reducing diagnostic throughput by 50%.",
        profile_key="urban",
        diagnostic_delta=-2,
    ),
    "combined_disruption": ScenarioPreset(
        id="combined_disruption",
        name="Scenario G: Severe Compound Crisis",
        description="Simultaneous 30% patient surge, 20% nurse shortage, and 4 offline beds.",
        profile_key="urban",
        arrival_surge_pct=30.0,
        nurse_multiplier=0.8,
        bed_delta=-4,
    )
}
