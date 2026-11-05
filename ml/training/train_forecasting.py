"""Training and comparative evaluation pipeline for time-series arrival forecasting."""
import json
import os

import lightgbm as lgb
import numpy as np
import statsmodels.api as sm
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, root_mean_squared_error

from ml.features.feature_builder import FEATURE_COLUMNS, create_forecasting_features
from ml.preprocessing.generator import generate_synthetic_hourly_arrivals


def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    mae = float(mean_absolute_error(y_true, y_pred))
    rmse = float(root_mean_squared_error(y_true, y_pred))
    sum_true = float(np.sum(y_true))
    wape = float(np.sum(np.abs(y_true - y_pred)) / (sum_true + 1e-6))
    bias = float(np.mean(y_pred - y_true))
    return {
        "mae": round(mae, 3),
        "rmse": round(rmse, 3),
        "wape": round(wape * 100.0, 2),  # In percentage
        "bias": round(bias, 3),
    }


def train_and_evaluate_forecasting(
    output_dir: str = "ml/artifacts",
    num_days: int = 180,
    seed: int = 42,
) -> dict:
    """Trains 4 forecasting models with temporal splits and quantile uncertainty bounds."""
    os.makedirs(output_dir, exist_ok=True)

    # 1. Generate synthetic hourly arrival series
    raw_df = generate_synthetic_hourly_arrivals(num_days=num_days, seed=seed)
    featured_df = create_forecasting_features(raw_df)

    # 2. Chronological Train / Val / Test split (70% train, 15% val, 15% test)
    n = len(featured_df)
    train_end = int(n * 0.70)
    val_end = int(n * 0.85)

    train_df = featured_df.iloc[:train_end]
    val_df = featured_df.iloc[train_end:val_end]
    test_df = featured_df.iloc[val_end:]

    X_train = train_df[FEATURE_COLUMNS]
    y_train_1h = train_df["target_1h"]

    X_val = val_df[FEATURE_COLUMNS]
    y_val_1h = val_df["target_1h"]

    X_test = test_df[FEATURE_COLUMNS]
    y_test_1h = test_df["target_1h"]
    y_test_arr = y_test_1h.to_numpy()

    results = {}

    # Model 1: Seasonal Naive (uses same hour last week = lag_168h)
    naive_pred = test_df["lag_168h"].to_numpy()
    results["seasonal_naive"] = {
        "metrics_1h": calculate_metrics(y_test_arr, naive_pred),
        "notes": "Seasonal persistence benchmark (same hour from 7 days prior)."
    }

    # Model 2: Poisson GLM (log-linear count model)
    try:
        # Standardize features for stable Poisson convergence
        X_train_sm = sm.add_constant(X_train[["hour", "day_of_week", "is_weekend", "lag_1h", "lag_24h", "lag_168h"]])
        X_test_sm = sm.add_constant(X_test[["hour", "day_of_week", "is_weekend", "lag_1h", "lag_24h", "lag_168h"]])
        poisson_model = sm.GLM(y_train_1h, X_train_sm, family=sm.families.Poisson()).fit()
        poisson_pred = np.maximum(0.0, poisson_model.predict(X_test_sm).to_numpy())
        results["poisson_glm"] = {
            "metrics_1h": calculate_metrics(y_test_arr, poisson_pred),
            "notes": "Classical generalized linear model with Poisson link function."
        }
    except Exception as e:
        results["poisson_glm"] = {"error": str(e)}

    # Model 3: XGBoost Regressor
    xgb_model = xgb.XGBRegressor(
        n_estimators=150,
        max_depth=5,
        learning_rate=0.05,
        random_state=seed,
        n_jobs=-1,
    )
    xgb_model.fit(X_train, y_train_1h, eval_set=[(X_val, y_val_1h)], verbose=False)
    xgb_pred = np.maximum(0.0, xgb_model.predict(X_test))
    results["xgboost"] = {
        "metrics_1h": calculate_metrics(y_test_arr, xgb_pred),
        "notes": "Extreme Gradient Boosting decision trees."
    }

    # Model 4: LightGBM Regressor (Point + Quantiles for 80% and 95% predictive intervals)
    lgb_point = lgb.LGBMRegressor(
        objective="regression_l1",
        n_estimators=150,
        max_depth=5,
        learning_rate=0.05,
        random_state=seed,
        n_jobs=-1,
        verbose=-1,
    )
    lgb_point.fit(X_train, y_train_1h)
    lgb_point_pred = np.maximum(0.0, lgb_point.predict(X_test))

    # Train Quantile LightGBM models for intervals (alpha=0.10, alpha=0.90 for 80% CI; alpha=0.025, 0.975 for 95% CI)
    lgb_q10 = lgb.LGBMRegressor(objective="quantile", alpha=0.10, n_estimators=100, random_state=seed, n_jobs=-1, verbose=-1)
    lgb_q10.fit(X_train, y_train_1h)
    q10_pred = np.maximum(0.0, lgb_q10.predict(X_test))

    lgb_q90 = lgb.LGBMRegressor(objective="quantile", alpha=0.90, n_estimators=100, random_state=seed, n_jobs=-1, verbose=-1)
    lgb_q90.fit(X_train, y_train_1h)
    q90_pred = np.maximum(0.0, lgb_q90.predict(X_test))

    lgb_q025 = lgb.LGBMRegressor(objective="quantile", alpha=0.025, n_estimators=100, random_state=seed, n_jobs=-1, verbose=-1)
    lgb_q025.fit(X_train, y_train_1h)
    q025_pred = np.maximum(0.0, lgb_q025.predict(X_test))

    lgb_q975 = lgb.LGBMRegressor(objective="quantile", alpha=0.975, n_estimators=100, random_state=seed, n_jobs=-1, verbose=-1)
    lgb_q975.fit(X_train, y_train_1h)
    q975_pred = np.maximum(0.0, lgb_q975.predict(X_test))

    # Calculate interval coverage
    coverage_80 = float(np.mean((y_test_arr >= q10_pred) & (y_test_arr <= q90_pred))) * 100.0
    coverage_95 = float(np.mean((y_test_arr >= q025_pred) & (y_test_arr <= q975_pred))) * 100.0
    avg_width_80 = float(np.mean(q90_pred - q10_pred))

    lgb_metrics = calculate_metrics(y_test_arr, lgb_point_pred)
    lgb_metrics["coverage_80_pct"] = round(coverage_80, 2)
    lgb_metrics["coverage_95_pct"] = round(coverage_95, 2)
    lgb_metrics["avg_width_80"] = round(avg_width_80, 2)

    # Feature importances
    importances = lgb_point.feature_importances_
    feat_imp = sorted(
        [{"feature": col, "importance": int(imp)} for col, imp in zip(FEATURE_COLUMNS, importances)],
        key=lambda x: x["importance"],
        reverse=True
    )

    results["lightgbm"] = {
        "metrics_1h": lgb_metrics,
        "feature_importance": feat_imp[:10],
        "notes": "LightGBM with quantile regression for calibrated uncertainty intervals."
    }

    # Multi-horizon evaluations for LightGBM (1h, 4h, 12h, 24h)
    horizon_metrics = {"1h": lgb_metrics}
    for h in [4, 12, 24]:
        target_col = f"target_{h}h"
        y_train_h = train_df[target_col]
        y_test_h = test_df[target_col].to_numpy()

        m_h = lgb.LGBMRegressor(n_estimators=100, learning_rate=0.05, random_state=seed, n_jobs=-1, verbose=-1)
        m_h.fit(X_train, y_train_h)
        pred_h = np.maximum(0.0, m_h.predict(X_test))
        horizon_metrics[f"{h}h"] = calculate_metrics(y_test_h, pred_h)

    results["horizons"] = horizon_metrics

    # Generate 48-hour forward forecast sample for frontend visualization
    recent_features = test_df.tail(48).copy()
    forward_forecast = []

    for i, (idx, row) in enumerate(recent_features.iterrows()):
        feat = row[FEATURE_COLUMNS].to_frame().T
        p_val = float(lgb_point.predict(feat)[0])
        p_q10 = float(lgb_q10.predict(feat)[0])
        p_q90 = float(lgb_q90.predict(feat)[0])
        p_q025 = float(lgb_q025.predict(feat)[0])
        p_q975 = float(lgb_q975.predict(feat)[0])
        actual = float(row["target_1h"])

        forward_forecast.append({
            "timestamp": idx.strftime("%Y-%m-%d %H:%M"),
            "horizon_step": i + 1,
            "predicted": round(p_val, 1),
            "lower_80": round(max(0.0, p_q10), 1),
            "upper_80": round(p_q90, 1),
            "lower_95": round(max(0.0, p_q025), 1),
            "upper_95": round(p_q975, 1),
            "historical": round(actual, 1),
        })

    results["forward_forecast_sample"] = forward_forecast

    # Save output artifacts
    output_path = os.path.join(output_dir, "forecasting_evaluation.json")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    return results


if __name__ == "__main__":
    res = train_and_evaluate_forecasting()
    print("Forecasting training completed.")
    print(json.dumps(res["lightgbm"]["metrics_1h"], indent=2))
