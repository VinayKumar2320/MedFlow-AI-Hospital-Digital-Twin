"""Discrete-event clinical patient flow processes modeling emergency department trajectories."""
import math
import random
from typing import Any, Callable, Dict, List, Optional

import simpy

from simulation.entities.patient import ArrivalMode, Patient, PatientStage, TriagePriority
from simulation.resources.hospital_resources import HospitalResources

# Diurnal multipliers for 24 hours of the day (Hour 0 to 23)
# Reflects standard emergency medicine epidemiology (low overnight, morning surge, evening peak)
DIURNAL_HOURLY_WEIGHTS = [
    0.48, 0.38, 0.32, 0.28, 0.30, 0.42,
    0.65, 0.90, 1.15, 1.35, 1.45, 1.40,
    1.32, 1.28, 1.25, 1.22, 1.20, 1.25,
    1.30, 1.28, 1.15, 0.95, 0.75, 0.58
]


def get_arrival_multiplier(sim_time_minutes: float) -> float:
    """Calculates diurnal arrival intensity factor based on simulated hour of day."""
    sim_hour = (sim_time_minutes / 60.0) % 24.0
    hour_idx = int(sim_hour)
    next_hour_idx = (hour_idx + 1) % 24
    frac = sim_hour - hour_idx
    # Linear interpolation between hourly weights
    weight = (1.0 - frac) * DIURNAL_HOURLY_WEIGHTS[hour_idx] + frac * DIURNAL_HOURLY_WEIGHTS[next_hour_idx]
    return weight


class PatientFlowProcess:
    def __init__(
        self,
        env: simpy.Environment,
        resources: HospitalResources,
        event_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
        max_events_logged: int = 10000,
    ):
        self.env = env
        self.res = resources
        self.event_callback = event_callback
        self.max_events_logged = max_events_logged

        self.patients: List[Patient] = []
        self.departed_patients: List[Patient] = []
        self.event_logs: List[Dict[str, Any]] = []
        self.active_patient_count: int = 0
        self.patient_counter: int = 0

    def log_event(
        self,
        patient: Patient,
        event_type: str,
        stage: PatientStage,
        resource_id: Optional[str] = None,
        wait_time_min: Optional[float] = None,
        queue_len: Optional[int] = None,
    ):
        evt = {
            "timestamp_min": round(self.env.now, 2),
            "patient_id": patient.id,
            "priority": int(patient.priority),
            "stage": stage.value,
            "event_type": event_type,
            "resource_id": resource_id,
            "wait_time_min": round(wait_time_min, 2) if wait_time_min is not None else 0.0,
            "queue_length": queue_len if queue_len is not None else 0,
            "active_in_system": self.active_patient_count,
        }
        if len(self.event_logs) < self.max_events_logged:
            self.event_logs.append(evt)
        if self.event_callback:
            self.event_callback(evt)

    def run_patient(self, patient: Patient):
        """Simulates end-to-end discrete-event progression of a single patient."""
        self.active_patient_count += 1
        patient.record_stage_enter(PatientStage.ARRIVED, self.env.now)
        self.log_event(patient, "ARRIVAL", PatientStage.ARRIVED)

        # ESI 1 (Resuscitation) bypasses standard reception/triage and goes straight to clinical bed
        if patient.priority == TriagePriority.ESI_1:
            yield from self._process_critical_resuscitation(patient)
            return

        # Phase 1: Registration
        patient.record_stage_enter(PatientStage.REGISTRATION, self.env.now)
        reg_queue_len = len(self.res.registration_clerks.resource.queue)
        self.log_event(patient, "QUEUE_ENTER", PatientStage.REGISTRATION, "registration_clerks", queue_len=reg_queue_len)

        # Priority for registration: inverse of priority (lower number = higher priority)
        reg_req = self.res.registration_clerks.request(priority=int(patient.priority))
        yield reg_req

        patient.record_service_start(PatientStage.REGISTRATION, self.env.now)
        self.log_event(patient, "SERVICE_START", PatientStage.REGISTRATION, "registration_clerks",
                       wait_time_min=patient.wait_times.get(PatientStage.REGISTRATION.value, 0.0))

        # Registration duration (LogNormal: mean ~4.5 min, std ~1.5)
        reg_duration = max(1.5, random.lognormvariate(math.log(4.5), 0.3))
        yield self.env.timeout(reg_duration)

        patient.record_service_end(PatientStage.REGISTRATION, self.env.now)
        self.res.registration_clerks.release(reg_req)
        self.log_event(patient, "SERVICE_COMPLETE", PatientStage.REGISTRATION, "registration_clerks")

        # Phase 2: Triage Assessment
        patient.record_stage_enter(PatientStage.TRIAGE, self.env.now)
        triage_q = len(self.res.triage_nurses.resource.queue)
        self.log_event(patient, "QUEUE_ENTER", PatientStage.TRIAGE, "triage_nurses", queue_len=triage_q)

        triage_req = self.res.triage_nurses.request(priority=int(patient.priority))
        yield triage_req

        patient.record_service_start(PatientStage.TRIAGE, self.env.now)
        self.log_event(patient, "SERVICE_START", PatientStage.TRIAGE, "triage_nurses",
                       wait_time_min=patient.wait_times.get(PatientStage.TRIAGE.value, 0.0))

        # Triage duration: 4 to 8 minutes
        triage_dur = max(2.0, random.lognormvariate(math.log(5.5), 0.3))
        yield self.env.timeout(triage_dur)

        patient.record_service_end(PatientStage.TRIAGE, self.env.now)
        self.res.triage_nurses.release(triage_req)
        self.log_event(patient, "SERVICE_COMPLETE", PatientStage.TRIAGE, "triage_nurses")

        # Determine diagnostic and bed pathways
        if patient.priority in [TriagePriority.ESI_2, TriagePriority.ESI_3]:
            patient.requires_imaging = (random.random() < 0.65)
            patient.requires_bed = True
        elif patient.priority == TriagePriority.ESI_4:
            patient.requires_imaging = (random.random() < 0.25)
            patient.requires_bed = (random.random() < 0.60)
        else: # ESI 5
            patient.requires_imaging = False
            patient.requires_bed = False

        # Phase 3: Bed Assignment & Waiting
        bed_req = None
        if patient.requires_bed:
            patient.record_stage_enter(PatientStage.WAITING_FOR_BED, self.env.now)
            bed_q = len(self.res.ed_beds.resource.queue)
            self.log_event(patient, "QUEUE_ENTER", PatientStage.WAITING_FOR_BED, "ed_beds", queue_len=bed_q)

            bed_req = self.res.ed_beds.request(priority=int(patient.priority))
            yield bed_req

            patient.record_service_start(PatientStage.WAITING_FOR_BED, self.env.now)
            self.log_event(patient, "SERVICE_START", PatientStage.WAITING_FOR_BED, "ed_beds",
                           wait_time_min=patient.wait_times.get(PatientStage.WAITING_FOR_BED.value, 0.0))

        # Phase 4: Clinical Physician & Nurse Assessment
        patient.record_stage_enter(PatientStage.ASSESSMENT, self.env.now)
        doc_q = len(self.res.physicians.resource.queue)
        self.log_event(patient, "QUEUE_ENTER", PatientStage.ASSESSMENT, "physicians", queue_len=doc_q)

        # Anti-starvation priority formula:
        # Effective priority = ESI priority - 0.005 * wait_time (so waiting raises priority)
        effective_priority = max(1.0, float(patient.priority) - (patient.total_wait_time * 0.005))
        doc_req = self.res.physicians.request(priority=effective_priority)
        yield doc_req

        patient.record_service_start(PatientStage.ASSESSMENT, self.env.now)
        self.log_event(patient, "SERVICE_START", PatientStage.ASSESSMENT, "physicians",
                       wait_time_min=patient.wait_times.get(PatientStage.ASSESSMENT.value, 0.0))

        # Clinical assessment duration depends on acuity
        if patient.priority == TriagePriority.ESI_2:
            assess_dur = max(10.0, random.lognormvariate(math.log(22.0), 0.35))
        elif patient.priority == TriagePriority.ESI_3:
            assess_dur = max(8.0, random.lognormvariate(math.log(16.0), 0.3))
        elif patient.priority == TriagePriority.ESI_4:
            assess_dur = max(5.0, random.lognormvariate(math.log(11.0), 0.25))
        else:
            assess_dur = max(3.0, random.lognormvariate(math.log(7.0), 0.2))
        yield self.env.timeout(assess_dur)

        patient.record_service_end(PatientStage.ASSESSMENT, self.env.now)
        self.res.physicians.release(doc_req)
        self.log_event(patient, "SERVICE_COMPLETE", PatientStage.ASSESSMENT, "physicians")

        # Phase 5: Diagnostics (if required: CT scan / X-ray / Urgent Blood Labs)
        if patient.requires_imaging:
            patient.record_stage_enter(PatientStage.DIAGNOSTICS, self.env.now)
            diag_q = len(self.res.diagnostic_stations.resource.queue)
            self.log_event(patient, "QUEUE_ENTER", PatientStage.DIAGNOSTICS, "diagnostic_stations", queue_len=diag_q)

            diag_req = self.res.diagnostic_stations.request(priority=int(patient.priority))
            yield diag_req

            patient.record_service_start(PatientStage.DIAGNOSTICS, self.env.now)
            self.log_event(patient, "SERVICE_START", PatientStage.DIAGNOSTICS, "diagnostic_stations",
                           wait_time_min=patient.wait_times.get(PatientStage.DIAGNOSTICS.value, 0.0))

            # Imaging turnaround duration (20 - 55 min)
            diag_dur = max(15.0, random.lognormvariate(math.log(32.0), 0.4))
            yield self.env.timeout(diag_dur)

            patient.record_service_end(PatientStage.DIAGNOSTICS, self.env.now)
            self.res.diagnostic_stations.release(diag_req)
            self.log_event(patient, "SERVICE_COMPLETE", PatientStage.DIAGNOSTICS, "diagnostic_stations")

        # Phase 6: Treatment & Nursing Care
        patient.record_stage_enter(PatientStage.TREATMENT, self.env.now)
        nurse_q = len(self.res.nurses.resource.queue)
        self.log_event(patient, "QUEUE_ENTER", PatientStage.TREATMENT, "nurses", queue_len=nurse_q)

        nurse_req = self.res.nurses.request(priority=int(patient.priority))
        yield nurse_req

        patient.record_service_start(PatientStage.TREATMENT, self.env.now)
        self.log_event(patient, "SERVICE_START", PatientStage.TREATMENT, "nurses",
                       wait_time_min=patient.wait_times.get(PatientStage.TREATMENT.value, 0.0))

        # Treatment duration
        if patient.priority == TriagePriority.ESI_2:
            treat_dur = max(25.0, random.lognormvariate(math.log(55.0), 0.4))
        elif patient.priority == TriagePriority.ESI_3:
            treat_dur = max(20.0, random.lognormvariate(math.log(42.0), 0.35))
        elif patient.priority == TriagePriority.ESI_4:
            treat_dur = max(10.0, random.lognormvariate(math.log(24.0), 0.3))
        else:
            treat_dur = max(5.0, random.lognormvariate(math.log(14.0), 0.25))
        yield self.env.timeout(treat_dur)

        patient.record_service_end(PatientStage.TREATMENT, self.env.now)
        self.res.nurses.release(nurse_req)
        self.log_event(patient, "SERVICE_COMPLETE", PatientStage.TREATMENT, "nurses")

        # Phase 7: Observation (for ~15% complex patients)
        patient.requires_observation = (patient.priority in [TriagePriority.ESI_2, TriagePriority.ESI_3] and random.random() < 0.18)
        if patient.requires_observation:
            patient.record_stage_enter(PatientStage.OBSERVATION, self.env.now)
            obs_req = self.res.observation_beds.request(priority=int(patient.priority))
            yield obs_req

            patient.record_service_start(PatientStage.OBSERVATION, self.env.now)
            self.log_event(patient, "SERVICE_START", PatientStage.OBSERVATION, "observation_beds")

            obs_dur = max(60.0, random.lognormvariate(math.log(180.0), 0.35))
            yield self.env.timeout(obs_dur)

            patient.record_service_end(PatientStage.OBSERVATION, self.env.now)
            self.res.observation_beds.release(obs_req)
            self.log_event(patient, "SERVICE_COMPLETE", PatientStage.OBSERVATION, "observation_beds")

        # Release ED Bed if one was held
        if bed_req is not None:
            patient.record_service_end(PatientStage.WAITING_FOR_BED, self.env.now)
            self.res.ed_beds.release(bed_req)
            self.log_event(patient, "RESOURCE_RELEASE", PatientStage.TREATMENT, "ed_beds")

        # Phase 8: Departure
        self._complete_departure(patient)

    def _process_critical_resuscitation(self, patient: Patient):
        """Dedicated high-priority pathway for ESI 1 resuscitation emergencies."""
        patient.record_stage_enter(PatientStage.ASSESSMENT, self.env.now)
        # Immediately request bed, physician, and nurse concurrently
        bed_req = self.res.ed_beds.request(priority=1)
        doc_req = self.res.physicians.request(priority=1)
        nurse_req = self.res.nurses.request(priority=1)

        # Wait for all 3 critical resources
        yield simpy.AllOf(self.env, [bed_req, doc_req, nurse_req])

        patient.record_service_start(PatientStage.ASSESSMENT, self.env.now)
        self.log_event(patient, "SERVICE_START", PatientStage.ASSESSMENT, "resuscitation_team")

        resus_dur = max(30.0, random.lognormvariate(math.log(60.0), 0.3))
        yield self.env.timeout(resus_dur)

        patient.record_service_end(PatientStage.ASSESSMENT, self.env.now)
        self.res.physicians.release(doc_req)
        self.res.nurses.release(nurse_req)
        self.res.ed_beds.release(bed_req)

        patient.outcome = "ADMITTED_ICU"
        self._complete_departure(patient)

    def _complete_departure(self, patient: Patient):
        patient.departure_time = self.env.now
        patient.current_stage = PatientStage.DEPARTED
        patient.record_stage_enter(PatientStage.DEPARTED, self.env.now)
        if not patient.outcome:
            patient.outcome = "DISCHARGED" if patient.priority >= TriagePriority.ESI_3 else "ADMITTED"

        self.active_patient_count = max(0, self.active_patient_count - 1)
        self.departed_patients.append(patient)
        self.log_event(patient, "DEPARTURE", PatientStage.DEPARTED,
                       wait_time_min=patient.total_wait_time)


def arrival_generator(
    env: simpy.Environment,
    process: PatientFlowProcess,
    base_arrival_rate_per_hour: float = 12.5,
    surge_multiplier: float = 1.0,
    duration_minutes: float = 2880.0,  # 48 hours
    seed: int = 42,
):
    """Generates stochastic patient arrivals via thinned Non-Homogeneous Poisson Process (NHPP)."""
    random.seed(seed)
    max_rate = base_arrival_rate_per_hour * 1.6 * surge_multiplier  # Maximum potential rate
    mean_interarrival_min = 60.0 / max_rate

    while env.now < duration_minutes:
        interarrival = random.expovariate(1.0 / mean_interarrival_min)
        yield env.timeout(interarrival)

        if env.now >= duration_minutes:
            break

        # Acceptance-rejection thinning step based on diurnal pattern
        current_multiplier = get_arrival_multiplier(env.now) * surge_multiplier
        acceptance_prob = (base_arrival_rate_per_hour * current_multiplier) / max_rate

        if random.random() <= min(1.0, acceptance_prob):
            process.patient_counter += 1

            # Acuity distribution matching realistic emergency medicine standards:
            # ESI 1: 3%, ESI 2: 18%, ESI 3: 45%, ESI 4: 24%, ESI 5: 10%
            acuity_roll = random.random()
            if acuity_roll < 0.03:
                priority = TriagePriority.ESI_1
                mode = ArrivalMode.AMBULANCE
            elif acuity_roll < 0.21:
                priority = TriagePriority.ESI_2
                mode = ArrivalMode.AMBULANCE if random.random() < 0.55 else ArrivalMode.WALK_IN
            elif acuity_roll < 0.66:
                priority = TriagePriority.ESI_3
                mode = ArrivalMode.AMBULANCE if random.random() < 0.20 else ArrivalMode.WALK_IN
            elif acuity_roll < 0.90:
                priority = TriagePriority.ESI_4
                mode = ArrivalMode.WALK_IN
            else:
                priority = TriagePriority.ESI_5
                mode = ArrivalMode.WALK_IN

            patient = Patient(
                id=f"PT-{process.patient_counter:05d}",
                arrival_time=env.now,
                priority=priority,
                arrival_mode=mode,
            )
            process.patients.append(patient)
            env.process(process.run_patient(patient))
