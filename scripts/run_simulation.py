"""CLI script to run SimPy discrete-event hospital simulation."""
import argparse

from simulation.experiments.runner import SimulationExperimentRunner
from simulation.scenarios.scenario_definitions import PROFILES


def main():
    parser = argparse.ArgumentParser(description="Run SimPy hospital operations simulation.")
    parser.add_argument("--profile", type=str, default="urban", choices=["community", "urban", "metropolitan"], help="Hospital profile")
    parser.add_argument("--surge", type=float, default=0.0, help="Arrival surge percentage (e.g. 40.0)")
    parser.add_argument("--duration", type=int, default=48, help="Simulation duration in hours")
    parser.add_argument("--reps", type=int, default=5, help="Number of Monte Carlo replications")
    parser.add_argument("--seed", type=int, default=42, help="Base random seed")
    args = parser.parse_args()

    config = PROFILES[args.profile]
    runner = SimulationExperimentRunner(config)

    print(f"Executing SimPy simulation for '{config.name}' (Surge: {args.surge}%, Duration: {args.duration}h, Replications: {args.reps})...")
    res = runner.run_multi_replications(
        duration_hours=args.duration,
        arrival_surge_pct=args.surge,
        replications=args.reps,
        base_seed=args.seed,
    )

    print("\n--- Simulation Operational Results ---")
    print(f"Total Arrived (Mean):    {res['total_arrived']}")
    print(f"Total Departed (Mean):   {res['total_departed']}")
    print(f"In-System at Cutoff:     {res['in_system_at_cutoff']}")
    print(f"Conservation Invariant:  {'VERIFIED (Zero Discrepancy)' if res['conservation_verified'] else 'FAILED'}")
    print(f"Mean Wait Time:          {res['mean_wait_time']['mean']} min (95% CI: [{res['mean_wait_time']['ci_lower']}, {res['mean_wait_time']['ci_upper']}])")
    print(f"P95 Wait Time:           {res['p95_wait_time']['mean']} min")
    print(f"Mean Length of Stay:     {res['mean_los']['mean']} min")
    print(f"Throughput Rate:         {res['throughput_per_hour']['mean']} departures/hour")

    print("\n--- Resource Utilization ---")
    for r_name, u in res["resource_utilization"].items():
        print(f"  {r_name:<22}: {u['mean_pct']}% (95% CI: [{u['ci_lower']}%, {u['ci_upper']}%])")

    if res.get("bottlenecks"):
        print("\n--- Identified Bottlenecks ---")
        for b in res["bottlenecks"]:
            print(f"  [{b['severity']}] {b['resource']}: {b['recommendation']}")


if __name__ == "__main__":
    main()
