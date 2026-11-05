"""One-shot bootstrap script to initialize database, train models, and seed baseline scenarios."""
import os

from backend.app.core.database import Base, SessionLocal, engine
from backend.app.core.logging import setup_logging
from backend.app.repositories.simulation_repo import seed_initial_data
from ml.preprocessing.generator import generate_synthetic_hourly_arrivals, generate_synthetic_patient_records
from ml.training.train_forecasting import train_and_evaluate_forecasting
from optimization.evaluation.evaluator import OptimizationEvaluator
from simulation.experiments.runner import SimulationExperimentRunner
from simulation.scenarios.scenario_definitions import PROFILES


def main():
    setup_logging()
    print("==================================================================")
    print("   MEDFLOW — HOSPITAL OPERATIONS DIGITAL TWIN BOOTSTRAP")
    print("==================================================================")

    # 1. Generate Synthetic Hospital Datasets
    print("\n[Step 1/5] Generating synthetic emergency department arrival data...")
    os.makedirs("ml/datasets", exist_ok=True)
    hourly_df = generate_synthetic_hourly_arrivals(num_days=180, seed=42)
    hourly_df.to_csv("ml/datasets/synthetic_hourly_arrivals.csv")
    patient_df = generate_synthetic_patient_records(hourly_df, max_records=2000, seed=42)
    patient_df.to_csv("ml/datasets/synthetic_patient_records.csv", index=False)
    print("✓ Synthetic datasets generated in ml/datasets/")

    # 2. Train and Benchmark Forecasting Models
    print("\n[Step 2/5] Training arrival forecasting models (Naive, Poisson, XGBoost, LightGBM)...")
    os.makedirs("ml/artifacts", exist_ok=True)
    fc_results = train_and_evaluate_forecasting(output_dir="ml/artifacts", num_days=180, seed=42)
    lgb_m = fc_results["lightgbm"]["metrics_1h"]
    print(f"✓ LightGBM 1-Hour MAE: {lgb_m['mae']} | WAPE: {lgb_m['wape']}% | 80% Coverage: {lgb_m.get('coverage_80_pct')}%")

    # 3. Initialize Database Schema & Seed Profiles
    print("\n[Step 3/5] Initializing database schema & seeding profiles...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_initial_data(db)
        print("✓ Database initialized and hospital profiles seeded.")
    finally:
        db.close()

    # 4. Verify SimPy Discrete-Event Simulation
    print("\n[Step 4/5] Executing SimPy baseline simulation...")
    runner = SimulationExperimentRunner(PROFILES["urban"])
    sim_res = runner.run_multi_replications(duration_hours=24, replications=2, base_seed=42)
    print(f"✓ Baseline Mean Wait: {sim_res['mean_wait_time']['mean']} min | Throughput: {sim_res['throughput_per_hour']['mean']} pt/hr")
    print(f"✓ Conservation of Mass Verified: {sim_res['conservation_verified']}")

    # 5. Verify Google OR-Tools CP-SAT Optimization
    print("\n[Step 5/5] Executing OR-Tools CP-SAT staffing optimization...")
    evaluator = OptimizationEvaluator(PROFILES["urban"])
    opt_res = evaluator.evaluate_optimization(max_additional_daily_budget=5000.0, replications=2, duration_hours=24)
    best = opt_res["recommended_plan"]
    print(f"✓ Recommended Strategy: {best['strategy_name']}")
    print(f"✓ Expected Wait Reduction: -{best['wait_reduction_minutes']} min (-{best['wait_reduction_pct']}%)")

    print("\n==================================================================")
    print("   MEDFLOW SYSTEM INITIALIZATION COMPLETE")
    print("==================================================================")
    print("To run the application locally:")
    print("  1. Backend:  .venv/bin/uvicorn backend.app.main:app --reload --port 8000")
    print("  2. Frontend: cd frontend && npm run dev (or npx vite --port 3000)")
    print("  3. Tests:    .venv/bin/pytest")
    print("==================================================================\n")


if __name__ == "__main__":
    main()
