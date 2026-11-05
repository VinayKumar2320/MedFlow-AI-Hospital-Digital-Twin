"""Simulation-based validation and evaluation for OR-Tools optimization candidates."""
from typing import Any, Dict

from optimization.solvers.staffing_optimizer import StaffingOptimizerCPSAT
from simulation.experiments.runner import SimulationExperimentRunner
from simulation.scenarios.scenario_definitions import HospitalConfig


class OptimizationEvaluator:
    def __init__(self, config: HospitalConfig):
        self.config = config
        self.runner = SimulationExperimentRunner(config)
        self.optimizer = StaffingOptimizerCPSAT(config)

    def evaluate_optimization(
        self,
        max_additional_daily_budget: float = 6000.0,
        arrival_surge_pct: float = 0.0,
        replications: int = 5,
        duration_hours: int = 48,
        base_seed: int = 42,
    ) -> Dict[str, Any]:
        """Runs end-to-end optimization: CP-SAT candidate generation -> SimPy validation with CRN."""
        # 1. Run baseline simulation
        baseline_sim = self.runner.run_multi_replications(
            duration_hours=duration_hours,
            arrival_surge_pct=arrival_surge_pct,
            replications=replications,
            base_seed=base_seed,
        )

        # 2. Solve candidate configurations via OR-Tools
        candidates = self.optimizer.solve_candidate_plans(
            max_additional_daily_budget=max_additional_daily_budget,
            arrival_surge_pct=arrival_surge_pct,
            num_candidates=3,
        )

        evaluated_plans = []
        tradeoff_frontier = []

        # Base daily cost
        base_md = self.config.physicians
        base_rn = self.config.nurses
        base_cost = self.optimizer.calculate_daily_cost(
            int(base_md * 0.4), int(base_md * 0.4), base_md - int(base_md * 0.8),
            int(base_rn * 0.4), int(base_rn * 0.4), base_rn - int(base_rn * 0.8),
            self.config.diagnostic_stations, 0
        )

        # Add baseline point to tradeoff frontier
        tradeoff_frontier.append({
            "plan_name": "Baseline (Current)",
            "daily_cost": base_cost,
            "cost_delta": 0.0,
            "mean_wait_min": baseline_sim["mean_wait_time"]["mean"],
            "p95_wait_min": baseline_sim["p95_wait_time"]["mean"],
            "throughput_hourly": baseline_sim["throughput_per_hour"]["mean"],
        })

        best_plan = None
        max_wait_reduction = -999.0

        for cand in candidates:
            staff = cand["staffing"]
            # Map shift staffing to effective operational capacity for the SimPy runner
            # We take the mean across 24 hours as operational baseline
            eff_md = int(round(staff["effective_total_physicians"]))
            eff_rn = int(round(staff["effective_total_nurses"]))
            eff_diag = staff["diagnostic_stations"]
            eff_beds = staff["total_ed_beds"]

            # Run simulation using exact same seeds (CRN)
            plan_sim = self.runner.run_multi_replications(
                duration_hours=duration_hours,
                arrival_surge_pct=arrival_surge_pct,
                physician_override=eff_md,
                nurse_override=eff_rn,
                bed_override=eff_beds,
                diagnostic_override=eff_diag,
                replications=replications,
                base_seed=base_seed,
            )

            base_wait = baseline_sim["mean_wait_time"]["mean"]
            opt_wait = plan_sim["mean_wait_time"]["mean"]
            wait_red_min = max(0.0, round(base_wait - opt_wait, 2))
            wait_red_pct = round((wait_red_min / (base_wait + 1e-4)) * 100.0, 1)

            base_tp = baseline_sim["throughput_per_hour"]["mean"]
            opt_tp = plan_sim["throughput_per_hour"]["mean"]
            tp_delta_pct = round(((opt_tp - base_tp) / (base_tp + 1e-4)) * 100.0, 1)

            evaluated = {
                **cand,
                "simulation_results": {
                    "mean_wait_time": plan_sim["mean_wait_time"],
                    "p95_wait_time": plan_sim["p95_wait_time"],
                    "throughput_per_hour": plan_sim["throughput_per_hour"],
                    "mean_los": plan_sim["mean_los"],
                    "resource_utilization": plan_sim["resource_utilization"],
                },
                "wait_reduction_minutes": wait_red_min,
                "wait_reduction_pct": wait_red_pct,
                "throughput_increase_pct": tp_delta_pct,
                "cost_effectiveness": round(cand["cost_delta"] / max(0.1, wait_red_min), 2),
            }
            evaluated_plans.append(evaluated)

            tradeoff_frontier.append({
                "plan_name": cand["strategy_name"],
                "daily_cost": cand["daily_cost"],
                "cost_delta": cand["cost_delta"],
                "mean_wait_min": opt_wait,
                "p95_wait_min": plan_sim["p95_wait_time"]["mean"],
                "throughput_hourly": opt_tp,
            })

            if wait_red_min > max_wait_reduction:
                max_wait_reduction = wait_red_min
                best_plan = evaluated

        if not best_plan and evaluated_plans:
            best_plan = evaluated_plans[0]

        return {
            "status": "COMPLETED",
            "target_budget": max_additional_daily_budget,
            "baseline_daily_cost": base_cost,
            "recommended_plan": best_plan,
            "all_evaluated_plans": evaluated_plans,
            "baseline_metrics": baseline_sim,
            "tradeoff_frontier": tradeoff_frontier,
        }
