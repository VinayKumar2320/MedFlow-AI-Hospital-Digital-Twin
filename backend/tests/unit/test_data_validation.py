"""Unit tests for synthetic dataset schema, temporal feature engineering, and split integrity."""
from ml.features.feature_builder import FEATURE_COLUMNS, create_forecasting_features
from ml.preprocessing.generator import (
    generate_synthetic_hourly_arrivals,
    generate_synthetic_patient_records,
)


def test_synthetic_hourly_arrivals_generation():
    df = generate_synthetic_hourly_arrivals(num_days=10, seed=42)
    assert len(df) == 10 * 24
    assert "arrivals" in df.columns
    assert (df["arrivals"] >= 0).all()
    assert (df["hour"] >= 0).all() and (df["hour"] <= 23).all()
    assert (df["day_of_week"] >= 0).all() and (df["day_of_week"] <= 6).all()


def test_feature_engineering_no_future_leakage():
    raw_df = generate_synthetic_hourly_arrivals(num_days=30, seed=42)
    feat_df = create_forecasting_features(raw_df)

    # Assert feature columns exist
    for col in FEATURE_COLUMNS:
        assert col in feat_df.columns, f"Missing feature: {col}"

    # Assert no NaN values in engineered dataset
    assert not feat_df[FEATURE_COLUMNS].isna().any().any(), "Features contain unexpected NaN values."

    # Assert target columns are present and positive
    assert "target_1h" in feat_df.columns
    assert "target_4h" in feat_df.columns
    assert (feat_df["target_1h"] >= 0).all()
    assert (feat_df["target_4h"] >= 0).all()


def test_patient_records_schema():
    raw_df = generate_synthetic_hourly_arrivals(num_days=7, seed=42)
    pts = generate_synthetic_patient_records(raw_df, max_records=100, seed=42)

    assert len(pts) > 0
    required_fields = [
        "event_id", "patient_id", "arrival_timestamp", "triage_priority",
        "arrival_mode", "age_group", "service_category", "registration_duration",
        "assessment_duration", "diagnostic_duration", "treatment_duration",
        "observation_duration", "departure_timestamp", "bed_required", "simulated_outcome"
    ]
    for field in required_fields:
        assert field in pts.columns, f"Missing field in patient record: {field}"

    # Acuity priority range
    assert pts["triage_priority"].isin([1, 2, 3, 4, 5]).all()
    # Positive service times
    assert (pts["registration_duration"] > 0).all()
    assert (pts["assessment_duration"] > 0).all()
