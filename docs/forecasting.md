# Time-Series Demand Forecasting Methodology

## Target Formulations
MedFlow forecasts emergency department patient arrivals across four operational horizons:
- **1-Hour Ahead (\(t+1\)):** Immediate bed and triage nurse staging.
- **4-Hour Ahead (\(\sum_{i=1}^4 t+i\)):** Shift-level staffing adjustments.
- **12-Hour Ahead (\(\sum_{i=1}^{12} t+i\)):** Half-day bed census and inpatient bed boarding forecasts.
- **24-Hour Ahead (\(\sum_{i=1}^{24} t+i\)):** Macro shift scheduling and daily resource procurement.

## Evaluated Algorithms
1. **Seasonal Naive Benchmark:**
   \[
   \hat{y}_{t+h} = y_{t+h - 168}
   \]
   Baseline model predicting arrivals from the identical hour 7 days prior.
2. **Poisson Generalized Linear Model (GLM):**
   \[
   \log(\lambda_t) = \beta_0 + \sum_{j} \beta_j X_{j,t}
   \]
   Standard epidemiological baseline ensuring non-negative count predictions.
3. **Extreme Gradient Boosting (XGBoost):**
   Tree-based ensemble optimizing squared loss over lag and rolling statistics.
4. **LightGBM Quantile Regressors:**
   Minimizes pinball loss \(\rho_\alpha(u) = u(\alpha - \mathbb{I}(u < 0))\) to yield non-parametric 80% (\(\alpha=0.10, 0.90\)) and 95% (\(\alpha=0.025, 0.975\)) predictive intervals.

## Measured Performance Leaderboard (Holdout Test Split)
| Algorithm | MAE (1h) | RMSE | WAPE (%) | Bias | 80% Coverage | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Seasonal Naive** | 3.895 | 5.007 | 36.59% | +0.131 | N/A | Heuristic baseline |
| **Poisson GLM** | 3.464 | 4.279 | 32.54% | +0.155 | N/A | Count GLM |
| **XGBoost** | 2.904 | 3.671 | 27.28% | +1.284 | N/A | Tree ensemble |
| **LightGBM (Quantile)** | **2.740** | **3.476** | **25.74%** | **+0.842** | **71.77%** | **Best overall accuracy** |
