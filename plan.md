# MedFlow — Master Implementation & Architectural Plan
**AI-Powered Hospital Operations Digital Twin & Emergency Response Optimizer**

---

## 1. Executive Summary & System Objectives
MedFlow is an enterprise-grade hospital operations intelligence platform that couples:
1. **Time-Series Demand Forecasting:** (Seasonal Naive, Poisson GLM, LightGBM, XGBoost) with probabilistic prediction intervals (conformal / quantile-calibrated) for 1h, 4h, 12h, and 24h horizons.
2. **High-Fidelity Discrete-Event Simulation (SimPy):** Modeling realistic emergency department (ED) patient journeys (Arrival -> Registration -> Triage -> Assessment -> Diagnostics -> Treatment -> Observation -> Departure) under stochastic arrivals, multi-resource constraints (ED beds, physicians, nurses, diagnostic machines, observation beds), ESI triage priority queuing, and conservation of resources.
3. **Constraint Optimization Engine (Google OR-Tools CP-SAT + Simulation Evaluation):** Solves realistic shift staffing and bed capacity allocations subject to budgetary, skill-mix, bed-to-nurse ratio, and rest constraints, then validates recommendations across stochastic simulation replications with common random numbers.
4. **Explainable Decision Support & What-If Studio:** Counterfactual sensitivity analysis, waiting-time decomposition, SHAP explanations for forecasting, and real-time digital twin visualization.
5. **Modern Full-Stack Architecture:** FastAPI + Pydantic v2 + SQLAlchemy 2.x + React 19 / Vite + Tailwind CSS + Recharts + TanStack Query + Zustand.

> **Operational & Ethical Notice:** MedFlow is strictly an operational research, capacity planning, and educational simulation platform. It does not provide clinical diagnostic, triage, or direct patient care recommendations. All synthetic scenarios require operational and administrative validation.

---

## 2. System Architecture & Component Mapping

```
                                [Synthetic / Historical Arrival Stream]
                                                  |
                                                  v
                                     [Feature Engineering Pipeline]
                                  (Lags, Rolling Stats, Time, Seasonality)
                                                  |
                                                  v
                                     [Forecasting Engine (Ensemble)]
                         (Seasonal Naive, Poisson, LightGBM, XGBoost + Calibrated Intervals)
                                                  |
                         +------------------------+------------------------+
                         | (Demand Forecasts)                              | (Arrival Rates)
                         v                                                 v
             [FastAPI REST API / WebSockets]                  [SimPy Discrete-Event Simulation Engine]
                         ^                                                 |
                         |                                 +---------------+---------------+
                         |                                 |                               |
                         |                                 v                               v
                         |                         [Resource Models]              [Patient Flow Processes]
                         |                    (Beds, MDs, RNs, Imaging)       (Reg, Triage, Consult, Rx)
                         |                                 |                               |
                         |                                 +---------------+---------------+
                         |                                                 |
                         |                                                 v
                         |                                   [Operational Metrics Aggregator]
                         |                               (Waits, LOS, Utilization, Starvation, P95)
                         |                                                 |
                         |                                                 v
                         |                                     [Bottleneck Detector &
                         |                                   Sensitivity Analysis Engine]
                         |                                                 |
                         |                                                 v
                         |                                    [OR-Tools CP-SAT Optimizer]
                         |                                (Staff Schedules, Capacity Allocations)
                         |                                                 |
                         |                                                 v
                         |                                  [Multi-Replication Evaluator]
                         |                                  (Robustness & Tradeoff Curves)
                         |                                                 |
                         +-------------------------------------------------+
                                                  |
                                                  v
                                     [React 19 Vite Dashboard]
                      (Command Center, Demand Forecasting, Digital Twin Canvas,
                       What-If Studio, Optimization Studio, Scenario Comparisons, Model Intelligence)
```

---

## 3. Implementation Phases

### Phase 1: Repository Foundation & Core Architecture
- [x] Inspect workspace and initialize Python virtual environment with dependencies (`fastapi`, `uvicorn`, `pydantic`, `simpy`, `numpy`, `scipy`, `pandas`, `scikit-learn`, `ortools`, `statsmodels`, `lightgbm`, `xgboost`, `sqlalchemy`, `alembic`, `pytest`, `ruff`).
- [ ] Initialize monorepo structure:
  - `backend/app/` (API routes, core config/db, models, schemas, services, repositories)
  - `ml/` (feature engineering, training pipelines, model artifacts, evaluation)
  - `simulation/` (SimPy entities, processes, resources, scenario configs, experiments)
  - `optimization/` (CP-SAT solvers, constraints, simulation surrogates)
  - `frontend/` (React, Vite, Tailwind CSS, Recharts, Lucide, Zustand)
  - `scripts/` (synthetic generator, training, benchmarking, demo bootstrap)
  - `docs/` (comprehensive architecture, methodology, validation guides)

### Phase 2: Synthetic Emergency Department Data Generation & Schemas
- Build realistic stochastic generator with:
  - Diurnal arrival patterns (peak late morning/evening, lull at 04:00)
  - Day-of-week and seasonal factors
  - Emergency Severity Index (ESI 1 through 5) distributions
  - Realistic service duration distributions (LogNormal / Gamma)
  - Multi-resource requirements per acuity level
- Validate data generation with statistical summary and missing-value / range verification tests.

### Phase 3: Time-Series Demand Forecasting Pipeline
- Implement 4 models:
  1. Seasonal Naive baseline (same hour last week)
  2. Historical Moving Average & Poisson GLM
  3. LightGBM Regressor with lag & calendar features
  4. XGBoost Regressor
- Evaluate rolling-origin cross-validation with MAE, RMSE, WAPE, and prediction intervals (10th to 90th percentiles).
- Model explanation module (feature importance & SHAP approximation).

### Phase 4: SimPy Discrete-Event Simulation Engine
- Configurable hospital entities:
  - `EmergencyDepartment` environment
  - Queues with priority scheduling (ESI 1 highest, starvation prevention)
  - Resources: `RegistrationClerks`, `TriageNurses`, `Physicians`, `StaffNurses`, `EDBeds`, `DiagnosticStations` (CT/X-Ray/Lab), `ObservationBeds`
  - Complex flows: conditional diagnostic branching (high ESI 2-3 require imaging before treatment), nurse + MD co-allocation for critical procedures.
- Metrics collector: Waiting times per stage, overall length of stay (LOS), resource utilization time-series, queue lengths, starvation metrics, unfinished patient accounting at cutoff.
- Step-by-step event logging for real-time frontend visualization / playback.

### Phase 5: Bottleneck Analysis & Counterfactual Engine
- Diagnostic queue and utilization tracking.
- Waiting time decomposition (Registration -> Triage -> Assessment -> Diagnostics -> Treatment).
- Automated counterfactual evaluator (e.g., delta wait time per +1 nurse or +1 diagnostic station).

### Phase 6: Constraint Optimization (Google OR-Tools CP-SAT) & Stochastic Evaluation
- Formulate mixed-integer / CP-SAT model:
  - Decision variables: Staff allocation per shift (morning, evening, night) and bed availability.
  - Constraints: Budget ceiling, minimum coverage per acuity, nurse-to-patient safety ratios, maximum shift limits.
  - Objective: Minimize estimated queue delays and penalty for unserved demand subject to operational cost budget.
- Coupling mechanism:
  - Generate Pareto-optimal or top-K candidate staffing allocations via OR-Tools.
  - Execute multi-replication SimPy runs for candidate plans with Common Random Numbers (CRN).
  - Return expected wait reduction, confidence intervals (95% CI), cost delta, and constraint verification.

### Phase 7: FastAPI Backend & Asynchronous Job Runner
- Endpoints:
  - `GET /api/v1/health`
  - `GET /api/v1/dashboard/overview`
  - `GET /api/v1/forecasts` & `/api/v1/forecasts/metrics`
  - `POST /api/v1/simulations` & `GET /api/v1/simulations/{id}` & `/events`
  - `GET /api/v1/scenarios` & `POST /api/v1/scenarios`
  - `POST /api/v1/optimizations` & `GET /api/v1/optimizations/{id}`
  - `GET /api/v1/analytics/bottlenecks`
  - `GET /api/v1/models/metrics`
- Asynchronous task worker for heavy simulations and optimization.
- Database persistence (SQLite with zero-config local run, seamlessly switchable to PostgreSQL via env).

### Phase 8: Interactive Frontend (React + TypeScript + Tailwind + Recharts)
- 7 core modules:
  1. **Hospital Command Center:** Real-time summary gauges, active census, wait times, bed occupancy, live alerts.
  2. **Demand Forecasting:** Historical vs forecast curves, prediction intervals, multi-horizon forecasts, model comparison cards.
  3. **Digital Twin Simulator:** Visual stage diagram with live patient dots/tokens moving through stations, queue counters, playback controls (speed, pause, step).
  4. **What-If Scenario Lab:** Configurable surge sliders (+40% arrivals, -20% staff, bed closures, diagnostic outages) with instant simulation launch.
  5. **Optimization Studio:** Current vs recommended staffing table, budget tracker, constraint satisfaction check, expected wait reductions.
  6. **Scenario Comparison:** Side-by-side radar and bar comparison charts across baseline, surge, and optimized scenarios.
  7. **Model Intelligence:** Residual distributions, MAE/RMSE comparisons, feature importance, simulation calibration diagnostics.

### Phase 9: Automated Verification & Test Suite
- Comprehensive pytest suite:
  - Data validation and temporal split tests
  - Simulation invariant tests (conservation of patients, no negative wait times, resource capacity limits strictly held)
  - Queue priority and starvation avoidance tests
  - Optimization constraint feasibility tests
  - FastAPI integration tests
- Frontend build and lint checks (`npm run build`).

### Phase 10: Docker, CI/CD, Documentation & Benchmark Verification
- `Dockerfile` & `docker-compose.yml` for single-command launch.
- GitHub Actions workflow for linting, typing, and tests.
- Standalone benchmark scripts:
  - `scripts/generate_synthetic_data.py`
  - `scripts/train_models.py`
  - `scripts/benchmark_simulation.py`
  - `scripts/benchmark_optimizer.py`
  - `scripts/bootstrap_demo.py`
- Comprehensive `README.md` and `docs/`.
