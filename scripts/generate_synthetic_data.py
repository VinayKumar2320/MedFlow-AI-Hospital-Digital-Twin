"""Script to generate synthetic hospital operational data."""
import argparse
import os

from ml.preprocessing.generator import (
    generate_synthetic_hourly_arrivals,
    generate_synthetic_patient_records,
)


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic hospital arrival data.")
    parser.add_argument("--days", type=int, default=180, help="Number of synthetic days to generate.")
    parser.add_argument("--output-dir", type=str, default="ml/datasets", help="Output directory for datasets.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility.")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    print(f"Generating {args.days} days of hourly arrival time-series (seed={args.seed})...")
    hourly_df = generate_synthetic_hourly_arrivals(num_days=args.days, seed=args.seed)

    hourly_path = os.path.join(args.output_dir, "synthetic_hourly_arrivals.csv")
    hourly_df.to_csv(hourly_path)
    print(f"Saved {len(hourly_df)} hourly arrival records to {hourly_path}")

    print("Generating synthetic patient-level clinical records...")
    patient_df = generate_synthetic_patient_records(hourly_df, max_records=5000, seed=args.seed)
    patient_path = os.path.join(args.output_dir, "synthetic_patient_records.csv")
    patient_df.to_csv(patient_path, index=False)
    print(f"Saved {len(patient_df)} patient records to {patient_path}")


if __name__ == "__main__":
    main()
