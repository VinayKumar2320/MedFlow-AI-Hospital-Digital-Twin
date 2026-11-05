"""Google OR-Tools CP-SAT constraint solver for multi-shift hospital staffing and capacity allocation."""
from typing import Any, Dict, List

from ortools.sat.python import cp_model

from simulation.scenarios.scenario_definitions import HospitalConfig


class StaffingOptimizerCPSAT:
    def __init__(
        self,
        config: HospitalConfig,
        cost_physician_hourly: float = 180.0,
        cost_nurse_hourly: float = 65.0,
        cost_diagnostic_hourly: float = 80.0,
        cost_bed_hourly: float = 25.0,
    ):
        self.config = config
        self.cost_md = cost_physician_hourly
        self.cost_rn = cost_nurse_hourly
        self.cost_diag = cost_diagnostic_hourly
        self.cost_bed = cost_bed_hourly

    def calculate_daily_cost(
        self,
        md_morning: int, md_evening: int, md_night: int,
        rn_morning: int, rn_evening: int, rn_night: int,
        diagnostic_stations: int,
        additional_beds: int = 0,
    ) -> float:
        """Computes total 24-hour operational labor and capacity expenditure."""
        md_hours = (md_morning + md_evening + md_night) * 8
        rn_hours = (rn_morning + rn_evening + rn_night) * 8
        diag_hours = diagnostic_stations * 24
        bed_hours = (self.config.ed_beds + additional_beds) * 24

        total = (
            md_hours * self.cost_md +
            rn_hours * self.cost_rn +
            diag_hours * self.cost_diag +
            bed_hours * self.cost_bed
        )
        return round(total, 2)

    def solve_candidate_plans(
        self,
        max_additional_daily_budget: float = 8000.0,
        arrival_surge_pct: float = 0.0,
        time_limit_seconds: float = 10.0,
        num_candidates: int = 3,
    ) -> List[Dict[str, Any]]:
        """Solves CP-SAT model generating feasible candidate configurations respecting all hard constraints."""
        surge_factor = 1.0 + (arrival_surge_pct / 100.0)

        # Calculate baseline nominal shift staffing from config
        base_md = self.config.physicians
        base_rn = self.config.nurses

        # Nominal 3-shift distribution (Morning 40%, Evening 40%, Night 20%)
        base_md_m = max(2, int(round(base_md * 0.40)))
        base_md_e = max(2, int(round(base_md * 0.40)))
        base_md_n = max(1, base_md - base_md_m - base_md_e)

        base_rn_m = max(4, int(round(base_rn * 0.40)))
        base_rn_e = max(4, int(round(base_rn * 0.40)))
        base_rn_n = max(2, base_rn - base_rn_m - base_rn_e)

        baseline_cost = self.calculate_daily_cost(
            base_md_m, base_md_e, base_md_n,
            base_rn_m, base_rn_e, base_rn_n,
            self.config.diagnostic_stations,
            0
        )

        candidates = []

        # Target optimization levels: Budget-Conservative, Balanced-Efficiency, High-Resilience
        budget_fractions = [0.40, 0.75, 1.00]

        for idx, b_frac in enumerate(budget_fractions[:num_candidates]):
            allowed_budget = baseline_cost + (max_additional_daily_budget * b_frac)

            model = cp_model.CpModel()

            # Decision Variables
            # Physicians per shift
            md_m = model.NewIntVar(base_md_m, base_md_m + 8, "md_m")
            md_e = model.NewIntVar(base_md_e, base_md_e + 8, "md_e")
            md_n = model.NewIntVar(base_md_n, base_md_n + 4, "md_n")

            # Nurses per shift
            rn_m = model.NewIntVar(base_rn_m, base_rn_m + 16, "rn_m")
            rn_e = model.NewIntVar(base_rn_e, base_rn_e + 16, "rn_e")
            rn_n = model.NewIntVar(base_rn_n, base_rn_n + 8, "rn_n")

            # Diagnostics & Beds
            diag = model.NewIntVar(self.config.diagnostic_stations, self.config.diagnostic_stations + 4, "diag")
            extra_beds = model.NewIntVar(0, 10, "extra_beds")

            # Safety Constraint 1: Nurse-to-Physician ratio >= 1.6 in all shifts
            model.Add(rn_m * 10 >= md_m * 16)
            model.Add(rn_e * 10 >= md_e * 16)
            model.Add(rn_n * 10 >= md_n * 16)

            # Safety Constraint 2: Peak coverage during morning and evening surges
            min_peak_rn = int(base_rn_m * min(1.8, surge_factor * 0.9))
            model.Add(rn_m >= min_peak_rn)
            model.Add(rn_e >= min_peak_rn)

            # Budget Constraint (in integer cents for CP-SAT)
            # Cost = ((md_m + md_e + md_n) * 8 * 180 + (rn_m + rn_e + rn_n) * 8 * 65 + diag * 24 * 80 + (base_beds + extra_beds) * 24 * 25)
            md_cost = (md_m + md_e + md_n) * int(8 * self.cost_md)
            rn_cost = (rn_m + rn_e + rn_n) * int(8 * self.cost_rn)
            diag_cost = diag * int(24 * self.cost_diag)
            bed_cost = (self.config.ed_beds + extra_beds) * int(24 * self.cost_bed)

            total_cost_expr = md_cost + rn_cost + diag_cost + bed_cost
            model.Add(total_cost_expr <= int(allowed_budget))

            # Objective: Maximize clinical coverage across peak hours while respecting budget
            # Priority weights: morning 40, evening 40, night 20, diagnostics 30
            coverage_score = (
                (md_m * 40 + md_e * 40 + md_n * 20) * 3 +
                (rn_m * 40 + rn_e * 40 + rn_n * 20) * 2 +
                diag * 150 +
                extra_beds * 80
            )
            model.Maximize(coverage_score)

            solver = cp_model.CpSolver()
            solver.parameters.max_time_in_seconds = time_limit_seconds
            status = solver.Solve(model)

            if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
                res_md_m = solver.Value(md_m)
                res_md_e = solver.Value(md_e)
                res_md_n = solver.Value(md_n)
                res_rn_m = solver.Value(rn_m)
                res_rn_e = solver.Value(rn_e)
                res_rn_n = solver.Value(rn_n)
                res_diag = solver.Value(diag)
                res_beds = solver.Value(extra_beds)

                plan_cost = self.calculate_daily_cost(
                    res_md_m, res_md_e, res_md_n,
                    res_rn_m, res_rn_e, res_rn_n,
                    res_diag, res_beds
                )

                strategy_names = ["Conservative Lean Allocation", "Balanced High-Throughput", "Maximum Resilience Allocation"]
                candidates.append({
                    "plan_id": f"plan_{idx+1}",
                    "strategy_name": strategy_names[idx],
                    "budget_tier": f"{int(b_frac * 100)}% Budget Utilization",
                    "daily_cost": plan_cost,
                    "cost_delta": round(plan_cost - baseline_cost, 2),
                    "staffing": {
                        "physicians_morning": res_md_m,
                        "physicians_evening": res_md_e,
                        "physicians_night": res_md_n,
                        "nurses_morning": res_rn_m,
                        "nurses_evening": res_rn_e,
                        "nurses_night": res_rn_n,
                        "effective_total_physicians": round((res_md_m + res_md_e + res_md_n) / 3.0, 1),
                        "effective_total_nurses": round((res_rn_m + res_rn_e + res_rn_n) / 3.0, 1),
                        "diagnostic_stations": res_diag,
                        "additional_beds": res_beds,
                        "total_ed_beds": self.config.ed_beds + res_beds,
                    },
                    "constraints_verified": {
                        "budget_satisfied": plan_cost <= allowed_budget + 1e-2,
                        "nurse_to_md_ratio_satisfied": (
                            res_rn_m >= res_md_m * 1.6 and
                            res_rn_e >= res_md_e * 1.6 and
                            res_rn_n >= res_md_n * 1.6
                        ),
                        "coverage_minimums_satisfied": True,
                    }
                })

        return candidates
