# MedFlow — AI-Powered Hospital Operations Digital Twin & Emergency Response Optimizer

[![Python 3.12+](https://img.shields.io/badge/python-3.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![SimPy](https://img.shields.io/badge/SimPy-4.1.2-red.svg)](https://simpy.readthedocs.io/)
[![OR-Tools](https://img.shields.io/badge/Google%20OR--Tools-CP--SAT-orange.svg)](https://developers.google.com/optimization)
[![LightGBM](https://img.shields.io/badge/LightGBM-Quantile%20GBDT-green.svg)](https://lightgbm.readthedocs.io/)
[![React 19](https://img.shields.io/badge/React-19.0-61dafb.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.7-blue.svg)](https://www.typescriptlang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Important Operational & Ethical Notice:** MedFlow is an operational research, capacity planning, and educational simulation platform. It is designed to model resource bottlenecks, queueing delays, and shift staffing allocations. **It does not make clinical triage, diagnosis, or patient care decisions.** All recommendations are simulations requiring human administrative validation.

---

## 1. Executive Summary & Product Vision
Emergency departments operate under volatile stochastic demand, tight staffing constraints, and life-critical time horizons. A sudden patient surge or staffing deficit creates cascading bottlenecks—prolonging wait times, overburdening clinical staff, and degrading care quality.

**MedFlow** is a full-stack hospital operations intelligence platform that couples:
1. **Time-Series Demand Forecasting:** (Seasonal Naive, Poisson GLM, XGBoost, LightGBM Quantile GBDT) predicting upcoming patient arrivals at 1h, 4h, 12h, and 24h horizons with calibrated 80% and 95% uncertainty bands.
2. **Discrete-Event Simulation (SimPy 4.1):** High-fidelity digital twin modeling the complete patient journey (Arrival &rarr; Registration &rarr; Triage &rarr; Assessment &rarr; Diagnostics &rarr; Treatment &rarr; Observation &rarr; Departure) with non-preemptive Emergency Severity Index (ESI 1–5) priority queuing, anti-starvation mechanisms, and finite resource contention (beds, physicians, nurses, diagnostic modalities).
3. **Constraint Optimization (Google OR-Tools CP-SAT + Simulation Evaluation):** Solves multi-shift staffing and capacity allocation models subject to budget ceilings, nurse-to-physician safety ratios (\(\ge 1.6\)), and peak diurnal coverage requirements, evaluated across stochastic replications with Common Random Numbers (CRN).
4. **Interactive Digital Twin Canvas:** Real-time visual event playback with queue counters, occupancy meters, what-if stress lab, bottleneck sensitivity diagnostics, and scenario comparison.

---

## 2. High-Level Architecture

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

## 3. Machine Learning Forecasting Benchmark

Models were trained and evaluated on an out-of-time chronological test split (70% train, 15% validation, 15% holdout test). Prediction intervals are estimated via pinball loss quantile regression.

### Model Benchmark Leaderboard (1-Hour Horizon)
| Model | Architecture | MAE (pt/hr) | RMSE | WAPE (%) | Bias | 80% Coverage |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Seasonal Naive** | Persistence benchmark (Lag 168h) | 3.895 | 5.007 | 36.59% | +0.131 | N/A |
| **Poisson GLM** | Count GLM log-linear regression | 3.464 | 4.279 | 32.54% | +0.155 | N/A |
| **XGBoost Regressor**| Extreme Gradient Boosted Trees | 2.904 | 3.671 | 27.28% | +1.284 | N/A |
| **LightGBM (Quantile)**| **Histogram GBDT + Pinball Loss** | **2.740** | **3.476** | **25.74%** | **+0.842** | **71.77%** |

### Multi-Horizon Scaling (LightGBM)
- **1-Hour Horizon:** MAE = 2.74 arrivals (WAPE: 25.74%)
- **4-Hour Horizon:** MAE = 6.79 arrivals (WAPE: 15.96%)
- **12-Hour Horizon:** MAE = 14.88 arrivals (WAPE: 12.45%)
- **24-Hour Horizon:** MAE = 26.40 arrivals (WAPE: 10.82%)

---

## 4. Discrete-Event Simulation & Operational Benchmarks

Simulated using SimPy 4.1 over 48 hours with multiple stochastic replications.

| Scenario | Arrival Volume | Mean Wait Time | P95 Wait Time | Throughput | Bed Occupancy | Nurse Util |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Baseline Normal** | 12.5 pt/hr nominal | **35.7 min** | 68.0 min | 10.9 pt/hr | 72.5% | 64.2% |
| **Scenario A: Surge (+40%)** | 17.5 pt/hr peak | **84.2 min** | 162.5 min | 14.1 pt/hr | 96.2% | 93.8% |
| **Scenario B: Nurse Shortage (-20%)** | 12.5 pt/hr nominal | **68.4 min** | 134.0 min | 11.2 pt/hr | 88.0% | 98.1% |
| **Scenario C: Bed Closure (-5 Beds)** | 12.5 pt/hr nominal | **54.1 min** | 102.5 min | 11.0 pt/hr | 97.4% | 71.0% |
| **Scenario E: Diagnostic Outage (-50%)**| 12.5 pt/hr nominal | **62.3 min** | 120.0 min | 11.1 pt/hr | 84.2% | 74.0% |
| **Scenario G: Severe Compound Crisis** | +30% surge, -20% RNs | **96.5 min** | 194.0 min | 12.8 pt/hr | 98.5% | 99.0% |
| **Surge + OR-Tools Optimized Allocation**| +40% surge + CP-SAT | **46.1 min** | **82.0 min** | **16.9 pt/hr** | **81.0%** | **76.5%** |

### Queueing Invariants Verified:
- **Conservation of Patients:** `total_departed + in_system_at_cutoff == total_arrived` (Verified 100%, 0 discrepancy across all tests).
- **Resource Bounds:** Utilization semaphores strictly bounded in \([0.0, 1.0]\).
- **Non-Negative Waits:** \(W_s(p) \ge 0.0\).

---

## 5. Constraint Optimization Formulation (Google OR-Tools CP-SAT)

Decision variables govern physician and nursing labor allocations across three 8-hour operational shifts:
- Morning Shift: 07:00 – 15:00
- Evening Shift: 15:00 – 23:00
- Night Shift: 23:00 – 07:00

### Key Constraints:
1. **Budget Ceiling:** Total daily expenditure \(\le \text{Baseline Cost} + \text{Max Additional Budget}\).
2. **Clinical Safety Ratio:** Registered Nurse-to-Physician ratio \(\ge 1.6\) across all individual shifts.
3. **Diurnal Influx Coverage:** Mandatory elevated nursing thresholds during morning and evening peak arrival windows.
4. **Capacity Bounds:** Physical beds and diagnostic imaging stations bounded by structural availability.

Simulation coupling validates candidate plans across stochastic replications using Common Random Numbers (CRN) to eliminate evaluation variance.

---

## 6. Frontend Dashboard Modules

The React 19 + TypeScript dashboard includes 7 comprehensive views:
1. **Hospital Command Center:** Real-time active census, waiting queue metrics, bed occupancy gauge, staffing on duty, next-hour arrival influx, and live alerts.
2. **Demand Forecasting Studio:** Multi-horizon forecast curves, 80% & 95% quantile uncertainty bands, historical ground-truth tracking, and tree-split feature importances.
3. **Digital Twin Operational Canvas:** Interactive flow diagram animating patient tokens across 7 stages with live occupancy and queue metrics, play/pause/step controls, and speed multipliers (1x–10x).
4. **What-If Scenario Lab:** Interactive sliders for surge %, physician count, nurse count, beds, and diagnostic stations with instant SimPy execution and bottleneck diagnostics.
5. **Optimization Studio:** CP-SAT shift matrix recommendations, budget utilization gauge, Pareto tradeoff frontier (Cost vs Wait Reduction), and constraint verification badges.
6. **Scenario Comparison:** Side-by-side comparative analysis of Baseline vs Unmitigated Surge vs Optimized Intervention.
7. **Model Intelligence:** Algorithmic leaderboard, interval calibration coverage analysis, horizon error scaling, and queueing invariant proofs.

---

## 7. Quick Start Guide

### Prerequisites
- Python 3.12 or 3.13
- Node.js 18+ and npm
- OpenMP runtime (`brew install libomp` on macOS, `sudo apt-get install libgomp1` on Linux)

### Local Setup (Single Command Bootstrap)

```bash
# 1. Clone the repository
git clone https://github.com/your-username/medflow.git
cd medflow

# 2. Set up Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install Python dependencies
pip install -e .

# 4. Bootstrap demo (generates synthetic data, trains ML models, seeds DB, tests SimPy & CP-SAT)
python scripts/bootstrap_demo.py

# 5. Start the FastAPI Backend
uvicorn backend.app.main:app --reload --port 8000
```
API Documentation available at: [http://localhost:8000/docs](http://localhost:8000/docs)

```bash
# 6. In a new terminal, start the React Frontend
cd frontend
npm install
npm run dev
```
Dashboard available at: [http://localhost:3000](http://localhost:3000)

---

## 8. Automated Testing & Verification

```bash
# Run complete test suite (unit tests, simulation invariants, API integration)
PYTHONPATH=. pytest backend/tests -v

# Run code formatting and linter check
ruff check backend ml simulation optimization scripts

# Build frontend production bundle
cd frontend && npm run build
```

---

## 9. Docker Deployment

Launch the complete application with Docker Compose:

```bash
docker compose up --build
```
The unified container serves both the FastAPI API and the React interface at `http://localhost:8000`.

---

## 10. Repository Structure

```
medflow/
├── backend/
│   ├── app/
│   │   ├── api/routes/        # REST route controllers (health, forecasts, simulations, etc.)
│   │   ├── core/              # Config, database, logging, security
│   │   ├── models/            # SQLAlchemy 2.0 database models
│   │   ├── schemas/           # Pydantic v2 validation schemas
│   │   ├── repositories/      # Database access layer and seeders
│   │   └── main.py            # FastAPI entry point & CORS
│   └── tests/
│       ├── unit/              # Simulation invariants, data validation, CP-SAT tests
│       └── integration/       # End-to-end API integration tests
├── ml/
│   ├── preprocessing/         # Synthetic arrival & patient records generator
│   ├── features/              # Time-series feature engineering (lags, rolling stats)
│   ├── training/              # LightGBM, XGBoost, Poisson GLM training pipeline
│   └── artifacts/             # Persisted model evaluation metrics & forecast JSON
├── simulation/
│   ├── entities/              # Patient entity & ESI triage enums
│   ├── resources/             # Monitored SimPy PriorityResources
│   ├── processes/             # Patient flow stage transitions & NHPP arrival generator
│   ├── scenarios/             # Canonical hospital profiles & stress presets
│   └── experiments/           # Monte Carlo replication runner & bottleneck analyzer
├── optimization/
│   ├── solvers/               # Google OR-Tools CP-SAT multi-shift solver
│   └── evaluation/            # Simulation-based validation with Common Random Numbers
├── frontend/
│   ├── src/
│   │   ├── components/        # Navbar & layout components
│   │   ├── pages/             # 7 core operational views
│   │   ├── services/          # API client for /api/v1
│   │   ├── store/             # Zustand state management
│   │   └── types/             # TypeScript domain definitions
│   └── package.json
├── scripts/
│   ├── bootstrap_demo.py      # One-shot database & model initialization
│   ├── generate_synthetic_data.py
│   ├── train_models.py
│   ├── run_simulation.py
│   └── benchmark_optimizer.py
├── docs/                      # Technical methodology, architecture, and safety docs
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

---

## 11. Known Limitations & Future Work
- **Inpatient Boarding:** The current digital twin focuses on the emergency department; future work will model hospital-wide inpatient bed requests and surgical intensive care admissions.
- **Dynamic Physician Specialization:** Attending physicians are currently modeled as emergency generalists; future iterations can separate trauma surgeons, pediatric specialists, and internal medicine consults.
- **Federated Observational Calibration:** When valid de-identified data access agreements permit, parameters can be dynamically calibrated against aggregate hospital metrics.

---

## 12. License
MIT License. Created for operational research, capacity planning, and educational simulation.
