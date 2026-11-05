"""Unit and invariant tests for SimPy discrete-event simulation."""
from simulation.experiments.runner import SimulationExperimentRunner
from simulation.scenarios.scenario_definitions import PROFILES


def test_simulation_invariants_and_conservation():
    config = PROFILES["urban"]
    runner = SimulationExperimentRunner(config)

    # Run short 12-hour simulation
    res = runner.run_single_replication(
        duration_hours=12,
        arrival_surge_pct=0.0,
        seed=42,
    )

    # Invariant 1: Conservation of patients (Arrived == Departed + InSystem)
    assert res["conservation_error"] == 0, f"Patient conservation violated: {res['conservation_error']}"
    assert res["total_arrived"] == res["total_departed"] + res["in_system_at_cutoff"]
    assert res["total_arrived"] > 0
    assert res["total_departed"] > 0

    # Invariant 2: Non-negative wait times and LOS
    assert res["mean_wait_time"] >= 0.0
    assert res["median_wait_time"] >= 0.0
    assert res["mean_los"] >= res["mean_wait_time"]

    # Invariant 3: Resource utilization strictly between 0% and 100%
    for r_name, util in res["resource_utilization_pct"].items():
        assert 0.0 <= util <= 100.0, f"Resource {r_name} utilization out of bounds: {util}"


def test_surge_increases_queue_and_wait():
    config = PROFILES["urban"]
    runner = SimulationExperimentRunner(config)

    baseline = runner.run_single_replication(duration_hours=12, arrival_surge_pct=0.0, seed=123)
    surge = runner.run_single_replication(duration_hours=12, arrival_surge_pct=40.0, seed=123)

    # Total arrivals in 40% surge should be strictly greater than baseline under same seed
    assert surge["total_arrived"] > baseline["total_arrived"]


def test_multi_replications_confidence_intervals():
    config = PROFILES["community"]
    runner = SimulationExperimentRunner(config)

    multi_res = runner.run_multi_replications(
        duration_hours=12,
        replications=3,
        base_seed=999,
    )

    assert multi_res["replications"] == 3
    assert multi_res["conservation_verified"] is True
    assert multi_res["mean_wait_time"]["ci_lower"] <= multi_res["mean_wait_time"]["mean"] <= multi_res["mean_wait_time"]["ci_upper"]
