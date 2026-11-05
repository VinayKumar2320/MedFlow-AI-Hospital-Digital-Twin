"""Monitored hospital operational resources with queuing dynamics and metrics."""
from typing import Dict, List, Tuple

import simpy


class MonitoredResource:
    """Wrapper around SimPy PriorityResource tracking utilization, queue length, and busy time."""
    def __init__(self, env: simpy.Environment, name: str, capacity: int):
        self.env = env
        self.name = name
        self.capacity = max(1, capacity)
        self.resource = simpy.PriorityResource(env, capacity=self.capacity)

        # Tracking metrics
        self.utilization_samples: List[Tuple[float, int, int]] = []  # (time, in_use, queue_len)
        self.cumulative_busy_time: float = 0.0
        self.last_update_time: float = 0.0
        self.currently_in_use: int = 0
        self.total_acquisitions: int = 0

    def record_state(self):
        now = self.env.now
        duration = now - self.last_update_time
        if duration > 0:
            self.cumulative_busy_time += self.currently_in_use * duration
        self.last_update_time = now
        in_use = self.resource.count
        q_len = len(self.resource.queue)
        self.currently_in_use = in_use
        self.utilization_samples.append((now, in_use, q_len))

    def request(self, priority: int = 5):
        self.record_state()
        self.total_acquisitions += 1
        return self.resource.request(priority=priority)

    def release(self, req):
        self.record_state()
        return self.resource.release(req)

    def get_average_utilization(self, total_time: float) -> float:
        if total_time <= 0 or self.capacity <= 0:
            return 0.0
        self.record_state()
        max_possible = self.capacity * total_time
        return min(1.0, max(0.0, self.cumulative_busy_time / max_possible))


class HospitalResources:
    """Container for all physical and human resources in the Emergency Department."""
    def __init__(
        self,
        env: simpy.Environment,
        registration_clerks: int = 3,
        triage_nurses: int = 3,
        ed_beds: int = 30,
        physicians: int = 8,
        nurses: int = 16,
        diagnostic_stations: int = 4,
        observation_beds: int = 10,
    ):
        self.env = env
        self.registration_clerks = MonitoredResource(env, "registration_clerks", registration_clerks)
        self.triage_nurses = MonitoredResource(env, "triage_nurses", triage_nurses)
        self.ed_beds = MonitoredResource(env, "ed_beds", ed_beds)
        self.physicians = MonitoredResource(env, "physicians", physicians)
        self.nurses = MonitoredResource(env, "nurses", nurses)
        self.diagnostic_stations = MonitoredResource(env, "diagnostic_stations", diagnostic_stations)
        self.observation_beds = MonitoredResource(env, "observation_beds", observation_beds)

    def get_all_resources(self) -> Dict[str, MonitoredResource]:
        return {
            "registration_clerks": self.registration_clerks,
            "triage_nurses": self.triage_nurses,
            "ed_beds": self.ed_beds,
            "physicians": self.physicians,
            "nurses": self.nurses,
            "diagnostic_stations": self.diagnostic_stations,
            "observation_beds": self.observation_beds,
        }
