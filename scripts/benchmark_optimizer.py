"""Benchmark script evaluating Google OR-Tools CP-SAT solver and SimPy evaluation runtime."""
import argparse
import time

from optimization.evaluation.evaluator import OptimizationEvaluator
from simulation.scenarios.scenario_definitions import PROFILES


def main():
    parser = argparse.ArgumentParser(description="Benchmark OR-Tools CP-SAT and SimPy evaluation.")
    parser.add_argument("--profile", type=str, default="urban", choices=["community", "urban", "metropolitan"])
    parser.add_argument("--budget", type=float, default=6000.0, help="Max additional daily budget ($)")
    parser.add_argument("--surge", type=float, default=30.0, help="Arrival surge %")
    parser.add_argument("--reps", type=int, default=3, help="SimPy replications for evaluation")
    args = parser.parse_args()

    config = PROFILES[args.profile]
    evaluator = OptimizationEvaluator(config)

    print(f"Benchmarking Optimization for '{config.name}' (Budget: ${args.budget}, Surge: +{args.surge}%)...")
    start_time = time.time()

    results = evaluator.evaluate_optimization(
        max_additional_daily_budget=args.budget,
        arrival_surge_pct=args.surge,
        replications=args.reps,
        duration_hours=24,
        base_seed=42,
    )

    elapsed = time.time() - start_time
    best = results["recommended_plan"]

    print(f"\nOptimization completed in {elapsed:.2f} seconds.")
    print(f"Strategy:              {best['strategy_name']}")
    print(f"Baseline Daily Cost:   ${results['baseline_daily_cost']:,.2f}")
    print(f"Optimized Daily Cost:  ${best['daily_cost']:,.2f} (+${best['cost_delta']:,.2f})")
    print(f"Wait Reduction:        -{best['wait_reduction_minutes']} min (-{best['wait_reduction_pct']}%)")
    print(f"Throughput Increase:   +{best['throughput_increase_pct']}%")
    print("\n--- Recommended Staffing Allocation ---")
    staff = best["staffing"]
    print(f"  Morning (07-15h): {staff['physicians_morning']} MDs, {staff['nurses_morning']} RNs")
    print(f"  Evening (15-23h): {staff['physicians_evening']} MDs, {staff['nurses_evening']} RNs")
    print(f"  Night   (23-07h): {staff['physicians_night']} MDs, {staff['nurses_night']} RNs")
    print(f"  Diagnostics:      {staff['diagnostic_stations']} stations")
    print(f"  ED Beds:          {staff['total_ed_beds']} beds (+{staff['additional_beds']})")


if __name__ == "__main__":
    main()
