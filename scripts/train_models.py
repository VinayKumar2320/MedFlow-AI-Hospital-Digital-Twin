"""Script to execute model training and evaluation."""
import argparse

from ml.training.train_forecasting import train_and_evaluate_forecasting


def main():
    parser = argparse.ArgumentParser(description="Train arrival forecasting models.")
    parser.add_argument("--days", type=int, default=180, help="Days of synthetic data.")
    parser.add_argument("--output-dir", type=str, default="ml/artifacts", help="Output directory for artifacts.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed.")
    args = parser.parse_args()

    print(f"Executing forecasting model training pipeline (seed={args.seed})...")
    results = train_and_evaluate_forecasting(output_dir=args.output_dir, num_days=args.days, seed=args.seed)

    print("\n--- Model Benchmark Summary (1-Hour Horizon) ---")
    for m_name in ["seasonal_naive", "poisson_glm", "xgboost", "lightgbm"]:
        m_info = results.get(m_name, {})
        m_metrics = m_info.get("metrics_1h", {})
        print(f"Model: {m_name:<16} | MAE: {m_metrics.get('mae', 'N/A'):<6} | RMSE: {m_metrics.get('rmse', 'N/A'):<6} | WAPE: {m_metrics.get('wape', 'N/A')}%")


if __name__ == "__main__":
    main()
