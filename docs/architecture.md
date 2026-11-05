# MedFlow System Architecture

## Overview
MedFlow is designed as a modular, decoupled decision-support platform uniting:
1. **Demand Forecasting:** Non-homogeneous temporal Poisson, Poisson GLM, LightGBM, and XGBoost with quantile uncertainty bounds.
2. **Discrete-Event Simulation (DES):** High-fidelity SimPy simulation of clinical stages, multi-resource contention, non-preemptive acuity queuing, and anti-starvation mechanisms.
3. **Constraint Optimization:** Google OR-Tools CP-SAT solving multi-shift labor and capacity allocation models subject to budget and nurse-to-physician safety ratios.
4. **Digital Twin Interactive Visualization:** Full-stack React + TypeScript + Tailwind CSS dashboard delivering real-time playback, what-if stress testing, and counterfactual sensitivity diagnostics.

```
+-----------------------------------------------------------------------------------+
|                                 REACT 19 FRONTEND                                 |
|  [Command Center] [Forecasting] [Digital Twin] [What-If Lab] [Optimization Studio] |
+------------------------------------------+----------------------------------------+
                                           | HTTP REST / JSON
                                           v
+-----------------------------------------------------------------------------------+
|                                 FASTAPI BACKEND                                   |
|   /health  /dashboard  /forecasts  /simulations  /scenarios  /optimizations       |
+---------------------+--------------------+--------------------+-------------------+
                      |                    |                    |
                      v                    v                    v
+-------------------------+  +----------------------+  +----------------------------+
|   TIME-SERIES ENGINE    |  |   SIMPY DES ENGINE   |  |   OR-TOOLS CP-SAT SOLVER   |
| - LightGBM Quantile GBDT|  | - Patient Entities   |  | - Shift Integer Variables  |
| - XGBoost Regressor     |  | - Priority Queues    |  | - Nurse:MD Safety Ratios   |
| - Poisson GLM Count     |  | - Monitored Resources|  | - Budget Ceilings          |
| - Seasonal Naive        |  | - Event Tracing Logs |  | - Coverage Maximization    |
+-------------------------+  +----------------------+  +----------------------------+
                      |                    ^                    |
                      | (Arrival Rates)    | (Common Random     | (Feasible Allocations)
                      +--------------------+ Numbers Validation)+
```

## Module Boundaries
- `simulation/`: Completely independent of the web/API layer. Can run headless via CLI or import as a standalone Python library.
- `ml/`: Independent feature engineering, model training, and artifact persistence.
- `optimization/`: Formulates CP-SAT constraint models and orchestrates simulation-based candidate evaluation.
- `backend/app/`: Exposes REST endpoints, validates schemas with Pydantic v2, and manages database sessions.
- `frontend/`: Single-page React application consuming versioned endpoints.
