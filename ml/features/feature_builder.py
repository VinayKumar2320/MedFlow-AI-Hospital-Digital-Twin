"""Feature engineering for time-series patient arrival forecasting."""

import numpy as np
import pandas as pd


def create_forecasting_features(df: pd.DataFrame) -> pd.DataFrame:
    """Builds lag, rolling, and cyclical features without future data leakage."""
    data = df.copy()

    # 1. Cyclical trigonometric transforms for hour and day of week
    data["sin_hour"] = np.sin(2 * np.pi * data["hour"] / 24.0)
    data["cos_hour"] = np.cos(2 * np.pi * data["hour"] / 24.0)
    data["sin_dow"] = np.sin(2 * np.pi * data["day_of_week"] / 7.0)
    data["cos_dow"] = np.cos(2 * np.pi * data["day_of_week"] / 7.0)

    # 2. Historical lag features (strictly past observations)
    for lag in [1, 2, 3, 4, 6, 12, 24, 48, 168]:
        data[f"lag_{lag}h"] = data["arrivals"].shift(lag)

    # 3. Rolling window aggregations (shift by 1 to exclude current point)
    shifted = data["arrivals"].shift(1)
    for window in [4, 12, 24, 168]:
        data[f"rolling_mean_{window}h"] = shifted.rolling(window=window).mean()
        data[f"rolling_std_{window}h"] = shifted.rolling(window=window).std().fillna(0)

    # 4. Same-hour last week ratio
    data["ratio_to_last_week"] = (data["lag_1h"] / (data["lag_168h"] + 1e-4)).clip(0.1, 10.0)

    # 5. Prediction targets across horizons
    data["target_1h"] = data["arrivals"].shift(-1)
    data["target_4h"] = sum(data["arrivals"].shift(-i) for i in range(1, 5))
    data["target_12h"] = sum(data["arrivals"].shift(-i) for i in range(1, 13))
    data["target_24h"] = sum(data["arrivals"].shift(-i) for i in range(1, 25))

    # Drop rows with NaN resulting from lags (168 hours = 1 week warmup) and targets
    clean_data = data.dropna().copy()
    return clean_data


FEATURE_COLUMNS = [
    "hour", "day_of_week", "is_weekend", "month",
    "sin_hour", "cos_hour", "sin_dow", "cos_dow",
    "lag_1h", "lag_2h", "lag_3h", "lag_4h", "lag_6h", "lag_12h", "lag_24h", "lag_48h", "lag_168h",
    "rolling_mean_4h", "rolling_std_4h",
    "rolling_mean_12h", "rolling_std_12h",
    "rolling_mean_24h", "rolling_std_24h",
    "rolling_mean_168h", "rolling_std_168h",
    "ratio_to_last_week",
]
