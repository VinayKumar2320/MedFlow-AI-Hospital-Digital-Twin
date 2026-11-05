# MedFlow — Production Deployment Architecture & Hosting Guide

## Overview

MedFlow is engineered for zero-cost, high-reliability deployment using Render's Infrastructure-as-Code Blueprint (`render.yaml`).

```
                              GitHub Repository
                    (VinayKumar2320/MedFlow-AI-Hospital-Digital-Twin)
                                     |
                                     v
                             Render Blueprint
                               (render.yaml)
                                     |
                    +----------------+----------------+
                    |                                 |
                    v                                 v
         [medflow-dashboard]                   [medflow-api]
         Render Static Site                Render Web Service
       (React 19 + TypeScript)              (FastAPI in Docker)
              |                                       |
              |                                       +-- Demand Forecasting (LightGBM)
              |                                       +-- SimPy Discrete-Event Digital Twin
              |                                       +-- Google OR-Tools CP-SAT Optimizer
              |                                       +-- Bottleneck Diagnostic Engine
              |                                       +-- SQLite Embedded Database
              |                                       +-- OpenAPI / Swagger Docs
              |                                       |
              +------------- HTTPS API REST ----------+
                     (VITE_API_URL Configuration)
```

---

## Service Specifications (100% Free Tier)

| Service Name | Service Type | Runtime | Plan | Cost | Public URL |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`medflow-dashboard`** | Static Site | Node 20 / Vite | Free | **$0.00 / mo** | `https://medflow-dashboard.onrender.com` |
| **`medflow-api`** | Web Service | Docker (Python 3.12) | Free | **$0.00 / mo** | `https://medflow-api.onrender.com` |

---

## Critical Free-Tier Architecture Decisions

### 1. Separate Static Site and Web Service
Rather than running Node inside a heavy Docker container to serve static files, MedFlow separates the frontend into a native Render Static Site and the backend into a Docker Web Service.
- **Benefits:**
  - Zero RAM consumed by the frontend (served directly from Render's global CDN).
  - Faster backend build times without Node dependencies inside the Python container.
  - Independent zero-downtime frontend deployments.

### 2. Memory & Cold-Start Optimization (<512 MB RAM)
Render free web services provide 512 MB RAM and spin down after 15 minutes of inactivity.
- **Pre-Baked Model Artifacts:** Datasets and trained LightGBM/XGBoost models are pre-baked during the Docker build stage via `scripts/bootstrap_demo.py`. The running container never triggers training at startup, keeping steady-state memory under **160 MB RAM**.
- **Cold-Start Grace:** The frontend includes an automatic notification if backend response time exceeds 4 seconds, informing users that the free instance is spinning up.
- **Simulation Memory Clamping:** Default Monte Carlo replications in production are capped at 10 to ensure SimPy executions complete within milliseconds while staying well below the 512 MB threshold.

### 3. Dynamic Port & Strict CORS
- **Port:** The container dynamically reads the `$PORT` environment variable assigned by Render:
  ```dockerfile
  CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]
  ```
- **CORS:** FastAPI is configured with `allow_origin_regex=r"https://.*\.onrender\.com"` and explicit origin `https://medflow-dashboard.onrender.com`, allowing cross-origin API calls without security warnings.

---

## Step-by-Step Deployment Instructions

### Deploying via Render Blueprint

1. **Sign in to Render:**
   Navigate to [https://dashboard.render.com](https://dashboard.render.com) and log in.

2. **Create New Blueprint Instance:**
   - Click **New +** in the top navigation bar.
   - Select **Blueprint**.

3. **Connect GitHub Repository:**
   - Select the repository `VinayKumar2320/MedFlow-AI-Hospital-Digital-Twin`.
   - Branch: `main`.

4. **Verify Blueprint Specification:**
   Render automatically parses `render.yaml` from the root of the repository:
   - **`medflow-api`**: Web Service (Docker, Free Plan, Oregon/Frankfurt)
   - **`medflow-dashboard`**: Static Site (Root Dir `frontend`, Build `npm install && npm run build`, Publish `dist`)
   - **Environment Variables**: Confirms `VITE_API_URL=https://medflow-api.onrender.com` and `ENVIRONMENT=production`.

5. **Deploy:**
   - Enter Blueprint Name: `medflow-production`.
   - Click **Apply**.
   - Render initiates simultaneous deployment of both services.

6. **Verify Live Services:**
   - **Backend Health Check:** `https://medflow-api.onrender.com/api/v1/health`
   - **Interactive API Documentation:** `https://medflow-api.onrender.com/docs`
   - **Frontend Dashboard:** `https://medflow-dashboard.onrender.com`

---

## Post-Deployment Maintenance

- **Continuous Deployment:** Any push to the `main` branch on GitHub automatically triggers a fresh build on Render.
- **Log Inspection:** Access real-time logs via the Render Dashboard under **Events** &rarr; **Logs**.
- **Manual Restart:** In the Render dashboard, click **Manual Deploy** &rarr; **Deploy latest commit** or **Restart Service**.
