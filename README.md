# MedFlow — AI-Powered Hospital Operations Digital Twin & Emergency Response Optimizer

[![CI/CD Pipeline](https://github.com/VinayKumar2320/MedFlow-AI-Hospital-Digital-Twin/actions/workflows/ci.yml/badge.svg)](https://github.com/VinayKumar2320/MedFlow-AI-Hospital-Digital-Twin/actions)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-Render%20Dashboard-00C7B7?style=flat&logo=render)](https://medflow-dashboard.onrender.com)
[![API Docs](https://img.shields.io/badge/API%20Docs-FastAPI%20Swagger-009688?style=flat&logo=fastapi)](https://medflow-api-kgsv.onrender.com/docs)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12%20%7C%203.13-3776AB?style=flat&logo=python)](https://www.python.org/)
[![SimPy](https://img.shields.io/badge/Discrete%20Event-SimPy%204.1-E11D48?style=flat)](https://simpy.readthedocs.io/)
[![Google OR-Tools](https://img.shields.io/badge/Optimizer-Google%20OR--Tools%20CP--SAT-EA4335?style=flat&logo=google)](https://developers.google.com/optimization)
[![LightGBM](https://img.shields.io/badge/Forecasting-LightGBM%20Quantile-22C55E?style=flat)](https://lightgbm.readthedocs.io/)
[![React 19](https://img.shields.io/badge/Frontend-React%2019%20%2B%20TypeScript-61DAFB?style=flat&logo=react)](https://react.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🌐 Live Production Demonstration

The application is deployed on public cloud infrastructure (100% free tier):

| Component | Endpoint / URL | Operational Status |
| :--- | :--- | :--- |
| **Interactive Dashboard** | [https://medflow-dashboard.onrender.com](https://medflow-dashboard.onrender.com) | ✅ Live SPA (Render Static Site) |
| **Production REST API** | [https://medflow-api-kgsv.onrender.com/api/v1/health](https://medflow-api-kgsv.onrender.com/api/v1/health) | ✅ Online & Verified (Docker Web Service) |
| **Interactive Swagger Docs**| [https://medflow-api-kgsv.onrender.com/docs](https://medflow-api-kgsv.onrender.com/docs) | ✅ Live OpenAPI Explorer |

> **Operational & Ethical Notice:** MedFlow is an operational research, capacity planning, and educational simulation platform. It models resource bottlenecks, queuing delays, and shift staffing allocations. **It does not make clinical triage, diagnosis, or patient care decisions.** All recommendations are simulations requiring human administrative validation.

---

## 1. Executive Summary & Product Vision

Emergency departments operate under volatile stochastic demand, tight staffing constraints, and life-critical time horizons. A sudden patient surge or staffing deficit creates cascading bottlenecks—prolonging wait times, overburdening clinical staff, and degrading care quality.

**MedFlow** answers fundamental operational questions using genuine machine learning, discrete-event simulation, and mathematical optimization—not static formulas or fabricated numbers:

1. **How many patients are likely to arrive in the next 1, 4, 12, and 24 hours?** &rarr; LightGBM Quantile GBDT models non-homogeneous arrival intensities with 80% and 95% uncertainty bands.
2. **When and where does the emergency department experience congestion?** &rarr; SimPy 4.1 discrete-event state engine tracks queues across registration, triage, assessment, diagnostic imaging, and treatment beds.
3. **Which resources cause the largest delays?** &rarr; Automated bottleneck detection and counterfactual sensitivity analysis decompose wait times.
4. **Which shift staffing allocation minimizes waiting times under a fixed budget?** &rarr; Google OR-Tools CP-SAT solves mixed-integer shift allocations validated via Common Random Numbers (CRN) simulation.

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

## 3. Seven Interactive Dashboard Modules

The single-page application incorporates seven dedicated operational views:

### 1. Hospital Command Center
Real-time summary gauges, active emergency department census, waiting patients count, treatment bed occupancy percentage, clinical staff currently on duty, and live operational alerts.

### 2. Demand Forecasting Studio
Interactive trajectory charts comparing historical arrivals against predictions across 24h, 48h, and 72h horizons with 80% (inner) and 95% (outer) quantile uncertainty bands, plus tree-split feature importance gain.

### 3. Digital Twin Simulator Canvas
Live operational flow diagram animating patient transitions through 7 clinical stations:
$$\text{Arrival} \longrightarrow \text{Registration} \longrightarrow \text{Triage} \longrightarrow \text{Bed Queue} \longrightarrow \text{Assessment} \longrightarrow \text{Diagnostics} \longrightarrow \text{Treatment} \longrightarrow \text{Departure}$$
Features play/pause/step controls, simulation clock, and speed multipliers (1x, 2x, 5x, 10x).

### 4. What-If Scenario Lab
Interactive stress-testing laboratory allowing operational planners to configure patient surge percentages, physician counts, nurse counts, bed closures, and diagnostic outages. Generates empirical confidence intervals and bottleneck diagnoses in SimPy.

### 5. Optimization Studio
Staffing decision matrix displaying baseline vs OR-Tools recommended shift allocations across Morning (07–15h), Evening (15–23h), and Night (23–07h) shifts. Interactive Pareto tradeoff curve (Additional Daily Cost vs Wait Time Reduction).

### 6. Scenario Comparison
Side-by-side grouped comparative analysis across three operational scenarios: **Nominal Baseline** vs **Unmitigated +40% Surge** vs **Optimized Staffing Response**.

### 7. Model Intelligence & Scientific Validation
Out-of-time test set model leaderboards, quantile pinball calibration curves (80% and 95% empirical coverage), horizon error scaling (1h to 24h), and mathematical queueing invariant proofs.

---

## 4. Machine Learning Forecasting Benchmark

All models were evaluated on a chronological holdout test set (70% train, 15% validation, 15% out-of-time test):

### Model Leaderboard (1-Hour Influx Prediction)
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

## 5. Discrete-Event Simulation & Operational Benchmarks

Simulated with SimPy 4.1 over 48 hours using multiple stochastic replications:

| Scenario | Arrival Volume | Mean Wait | P95 Wait | Throughput | Bed Occupancy | Nurse Util | Bottleneck |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Baseline Normal** | 12.5 pt/hr nominal | **35.7 min** | 68.0 min | 10.9 pt/hr | 72.5% | 64.2% | Nominal |
| **Scenario A: Surge (+40%)** | 17.5 pt/hr peak | **84.2 min** | 162.5 min | 14.1 pt/hr | 96.2% | 93.8% | Nurses & Beds |
| **Scenario B: Nurse Shortage (-20%)** | 12.5 pt/hr nominal | **68.4 min** | 134.0 min | 11.2 pt/hr | 88.0% | 98.1% | Bedside Care |
| **Scenario C: Bed Closure (-5 Beds)** | 12.5 pt/hr nominal | **54.1 min** | 102.5 min | 11.0 pt/hr | 97.4% | 71.0% | Bed Queue |
| **Scenario E: Diagnostic Outage (-50%)**| 12.5 pt/hr nominal | **62.3 min** | 120.0 min | 11.1 pt/hr | 84.2% | 74.0% | CT / Labs |
| **Scenario G: Severe Compound Crisis** | +30% surge, -20% RN | **96.5 min** | 194.0 min | 12.8 pt/hr | 98.5% | 99.0% | Critical Delay |
| **Surge + OR-Tools Optimized Allocation**| +40% surge + CP-SAT | **46.1 min** | **82.0 min** | **16.9 pt/hr** | **81.0%** | **76.5%** | **Balanced** |

### Verified Queueing Invariants:
- **Conservation of Mass:** $N_{\text{arrived}} = N_{\text{departed}} + N_{\text{in\_system}}$ (100% verified, 0 discrepancy across all tests).
- **Resource Boundary:** Utilization semaphores strictly bounded in $[0.0, 1.0]$.
- **Non-Negative Waits:** Waiting times $W_s(p) \ge 0.0$ for all stages.

---

## 6. Quick Start & Local Execution

### Prerequisites
- Python 3.12 or 3.13
- Node.js 20+ and npm
- OpenMP runtime (`brew install libomp` on macOS, `sudo apt-get install libgomp1` on Linux)

### Local Setup (Single-Command Bootstrap)

```bash
# 1. Clone repository
git clone https://github.com/VinayKumar2320/MedFlow-AI-Hospital-Digital-Twin.git
cd MedFlow-AI-Hospital-Digital-Twin

# 2. Setup Python environment
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

# 3. Bootstrap demo (generates synthetic datasets, trains models, seeds DB)
python scripts/bootstrap_demo.py

# 4. Start FastAPI backend (Port 8000)
uvicorn backend.app.main:app --reload --port 8000
# -> API Docs: http://localhost:8000/docs

# 5. In a new terminal, start React frontend (Port 3000)
cd frontend
npm install
npm run dev
# -> Dashboard: http://localhost:3000
```

### Automated Testing

```bash
# Run 21 automated integration, invariant, and unit tests
PYTHONPATH=. pytest backend/tests -v

# Run code style & formatting check
ruff check backend ml simulation optimization scripts

# Verify production frontend build
cd frontend && npm run build
```

---

## 7. Cloud Deployment (Render Blueprint)

The project includes a root `render.yaml` configuring the complete multi-service architecture for 100% free hosting:

1. Sign in to [Render](https://dashboard.render.com).
2. Click **New +** &rarr; **Blueprint**.
3. Select `VinayKumar2320/MedFlow-AI-Hospital-Digital-Twin`.
4. Name the Blueprint `medflow-production` and click **Apply**.
5. Render deploys:
   - `medflow-api`: Docker Web Service (Free plan, 512 MB RAM)
   - `medflow-dashboard`: Static Site (React 19 SPA, zero RAM overhead)

---

## 8. License & Authorship

- **Author:** Vinay Kumar ([GitHub @VinayKumar2320](https://github.com/VinayKumar2320))
- **License:** MIT License. Built for operational research, educational simulation, and healthcare capacity planning.
