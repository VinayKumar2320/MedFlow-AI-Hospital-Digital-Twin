"""Integration tests for MedFlow FastAPI REST endpoints."""
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["database"] == "healthy"


def test_dashboard_overview():
    response = client.get("/api/v1/dashboard/overview")
    assert response.status_code == 200
    data = response.json()
    assert "hospital_name" in data
    assert "active_census" in data
    assert len(data["profiles"]) >= 3


def test_scenarios_listing():
    response = client.get("/api/v1/scenarios")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any("Surge" in s["name"] for s in data)


def test_forecasts_endpoint():
    response = client.get("/api/v1/forecasts?horizon_hours=24&model_name=lightgbm")
    assert response.status_code == 200
    data = response.json()
    assert data["model_name"] == "lightgbm"
    assert len(data["points"]) > 0
    assert "metrics" in data


def test_models_metrics_endpoint():
    response = client.get("/api/v1/models/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "model_comparison" in data
    assert "seasonal_naive" in data["model_comparison"]
    assert "lightgbm" in data["model_comparison"]


def test_simulation_run_endpoint():
    # Run a fast 12-hour simulation via API
    payload = {
        "arrival_surge_pct": 20.0,
        "duration_hours": 12,
        "random_seed": 42,
        "replications": 2,
    }
    response = client.post("/api/v1/simulations", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "COMPLETED"
    assert "summary_metrics" in data
    assert data["summary_metrics"]["mean_wait_time"]["mean"] > 0

    # Test fetching events
    run_id = data["id"]
    events_res = client.get(f"/api/v1/simulations/{run_id}/events")
    assert events_res.status_code == 200
    events = events_res.json()
    assert len(events) > 0
    assert "stage" in events[0]
