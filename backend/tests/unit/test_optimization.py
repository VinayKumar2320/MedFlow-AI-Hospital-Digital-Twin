"""Unit tests for Google OR-Tools CP-SAT staffing optimization and simulation evaluation."""
from optimization.evaluation.evaluator import OptimizationEvaluator
from optimization.solvers.staffing_optimizer import StaffingOptimizerCPSAT
from simulation.scenarios.scenario_definitions import PROFILES


def test_ortools_cpsat_solver_generates_feasible_plans():
    config = PROFILES["urban"]
    optimizer = StaffingOptimizerCPSAT(config)

    candidates = optimizer.solve_candidate_plans(
        max_additional_daily_budget=5000.0,
        arrival_surge_pct=20.0,
        num_candidates=3,
    )

    assert len(candidates) > 0, "Optimizer should return feasible candidate plans."
    for cand in candidates:
        staff = cand["staffing"]
        # Nurse to MD ratio verified (rn >= md * 1.6)
        assert staff["nurses_morning"] >= int(staff["physicians_morning"] * 1.6)
        assert staff["nurses_evening"] >= int(staff["physicians_evening"] * 1.6)
        assert staff["nurses_night"] >= int(staff["physicians_night"] * 1.6)
        assert cand["constraints_verified"]["budget_satisfied"] is True


def test_optimization_evaluator_runs_crn_simulation():
    config = PROFILES["community"]
    evaluator = OptimizationEvaluator(config)

    res = evaluator.evaluate_optimization(
        max_additional_daily_budget=3000.0,
        arrival_surge_pct=0.0,
        replications=2,
        duration_hours=12,
        base_seed=42,
    )

    assert res["status"] == "COMPLETED"
    assert "recommended_plan" in res
    assert len(res["tradeoff_frontier"]) >= 2
    assert "baseline_metrics" in res
