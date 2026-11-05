# Deployment Guide & Free Hosting Options

## Local Development Setup

### 1. Backend Setup
```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e .

# Run bootstrap (generates datasets, trains models, seeds database)
python scripts/bootstrap_demo.py

# Start FastAPI server
uvicorn backend.app.main:app --reload --port 8000
```
Interactive Swagger API docs available at: `http://localhost:8000/docs`

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Dashboard available at: `http://localhost:3000` (or `http://localhost:5173`)

### 3. Unified Docker Compose
```bash
docker compose up --build
```
Runs both backend and frontend inside a unified container at `http://localhost:8000`.

---

## Free Public Hosting Architecture

MedFlow is engineered to deploy cleanly on free cloud tiers without requiring paid services:

### Option A: Render (Free Web Service)
- Build Command: `pip install -e . && python scripts/bootstrap_demo.py && cd frontend && npm install && npm run build`
- Start Command: `uvicorn backend.app.main:app --host 0.0.0.0 --port 10000`
- Database: Embedded SQLite file or free Neon / Supabase PostgreSQL.

### Option B: Vercel / Netlify (Frontend) + Render / Fly.io (Backend)
- Frontend: Deployed on Vercel with rewrite proxy to backend API.
- Backend: Deployed on Fly.io / Render with zero-cost tier.

### Option C: Standalone Read-Only Demo
Precomputed simulation and optimization scenarios allow zero-latency interactive exploration on constrained free tiers.
