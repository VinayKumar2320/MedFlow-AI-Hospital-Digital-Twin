"""Demand forecasting endpoints delivering predictions and uncertainty intervals."""
import json
import os
from typing import Any, Dict

from fastapi import APIRouter, Query

from ml.training.train_forecasting import train_and_evaluate_forecasting

router = APIRouter(prefix="/forecasts", tags=["Forecasting"])

ARTIFACT_PATH = "ml/artifacts/forecasting_evaluation.json"


def load_or_train_forecasting() -> Dict[str, Any]:
    if os.path.exists(ARTIFACT_PATH):
        try:
            with open(ARTIFACT_PATH, "r") as f:
                return json.load(f)
        except Exception:
            pass
    # If not existing, train and generate
    return train_and_evaluate_forecasting()


@router.get("")
def get_demand_forecast(
    horizon_hours: int = Query(48, ge=1, le=72),
    model_name: str = Query("lightgbm", pattern="^(lightgbm|xgboost|poisson_glm|seasonal_naive)$"),
) -> Dict[str, Any]:
    """Returns forward arrival predictions with 80% and 95% confidence intervals."""
    data = load_or_train_forecasting()
    sample = data.get("forward_forecast_sample", [])[:horizon_hours]
    model_info = data.get(model_name, data.get("lightgbm", {}))

    return {
        "model_name": model_name,
        "horizon_hours": horizon_hours,
        "points": sample,
        "metrics": model_info.get("metrics_1h", {}),
        "feature_importance": data.get("lightgbm", {}).get("feature_importance", []),
    }


@router.get("/metrics")
def get_forecasting_metrics() -> Dict[str, Any]:
    """Returns comparative validation metrics across all 4 models and multiple horizons."""
    data = load_or_train_forecasting()
    return {
        "models": {
            "seasonal_naive": data.get("seasonal_naive", {}),
            "poisson_glm": data.get("poisson_glm", {}),
            "xgboost": data.get("xgboost", {}),
            "lightgbm": data.get("lightgbm", {}),
        },
        "multi_horizon_lightgbm": data.get("horizons", {}),
    }
