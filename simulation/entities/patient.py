"""Patient entity definition and clinical trajectory metadata."""
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Dict, Optional


class TriagePriority(IntEnum):
    ESI_1 = 1  # Resuscitation (immediate, life-threatening)
    ESI_2 = 2  # Emergent (high risk, severe pain/confusion)
    ESI_3 = 3  # Urgent (requires multiple resources, stable vitals)
    ESI_4 = 4  # Less Urgent (requires 1 resource)
    ESI_5 = 5  # Non-Urgent (no resources required, prescription refill/minor)


class PatientStage(str, Enum):
    ARRIVED = "ARRIVED"
    REGISTRATION = "REGISTRATION"
    TRIAGE = "TRIAGE"
    WAITING_FOR_BED = "WAITING_FOR_BED"
    ASSESSMENT = "ASSESSMENT"
    DIAGNOSTICS = "DIAGNOSTICS"
    TREATMENT = "TREATMENT"
    OBSERVATION = "OBSERVATION"
    DEPARTED = "DEPARTED"


class ArrivalMode(str, Enum):
    AMBULANCE = "AMBULANCE"
    WALK_IN = "WALK_IN"
    HELICOPTER = "HELICOPTER"


class ServiceCategory(str, Enum):
    MEDICAL = "MEDICAL"
    SURGICAL = "SURGICAL"
    PEDIATRIC = "PEDIATRIC"
    TRAUMA = "TRAUMA"


@dataclass
class Patient:
    id: str
    arrival_time: float  # In simulation minutes
    priority: TriagePriority
    arrival_mode: ArrivalMode = ArrivalMode.WALK_IN
    age_group: str = "adult"  # pediatric, adult, geriatric
    service_category: ServiceCategory = ServiceCategory.MEDICAL

    # Pathway flags determined at triage
    requires_bed: bool = True
    requires_imaging: bool = False
    requires_observation: bool = False

    # State tracking
    current_stage: PatientStage = PatientStage.ARRIVED
    departure_time: Optional[float] = None
    outcome: Optional[str] = None  # DISCHARGED, ADMITTED, LEFT_WITHOUT_BEING_SEEN

    # Timestamp records (in simulation minutes)
    timestamps: Dict[str, float] = field(default_factory=dict)

    # Wait times calculated per stage (in simulation minutes)
    wait_times: Dict[str, float] = field(default_factory=dict)
    service_times: Dict[str, float] = field(default_factory=dict)

    def record_stage_enter(self, stage: PatientStage, sim_time: float):
        self.current_stage = stage
        self.timestamps[f"{stage.value}_ENTER"] = sim_time

    def record_service_start(self, stage: PatientStage, sim_time: float):
        enter_time = self.timestamps.get(f"{stage.value}_ENTER", sim_time)
        wait = max(0.0, sim_time - enter_time)
        self.wait_times[stage.value] = wait
        self.timestamps[f"{stage.value}_SERVICE_START"] = sim_time

    def record_service_end(self, stage: PatientStage, sim_time: float):
        start_time = self.timestamps.get(f"{stage.value}_SERVICE_START", sim_time)
        duration = max(0.0, sim_time - start_time)
        self.service_times[stage.value] = duration
        self.timestamps[f"{stage.value}_SERVICE_END"] = sim_time

    @property
    def total_wait_time(self) -> float:
        return sum(self.wait_times.values())

    @property
    def length_of_stay(self) -> float:
        if self.departure_time is not None:
            return max(0.0, self.departure_time - self.arrival_time)
        return 0.0
