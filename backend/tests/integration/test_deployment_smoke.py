"""Deployment readiness and production smoke tests for MedFlow."""
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_production_health_probe():
    """Verifies that the /api/v1/health probe responds with valid operational state."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "service" in data
    assert data["database"] == "healthy"


def test_openapi_schema_readiness():
    """Ensures Swagger and OpenAPI specifications load without serialization errors."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "paths" in schema
    assert "/api/v1/health" in schema["paths"]
    assert "/api/v1/simulations" in schema["paths"]
    assert "/api/v1/optimizations" in schema["paths"]
    assert "/api/v1/forecasts" in schema["paths"]


def test_production_cors_headers():
    """Verifies that requests from the Render dashboard origin receive correct CORS headers."""
    for origin in ["https://medflow-dashboard-eyyu.onrender.com", "https://medflow-dashboard.onrender.com"]:
        headers = {
            "Origin": origin,
            "Access-Control-Request-Method": "GET",
        }
        response = client.get("/api/v1/health", headers=headers)
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
        allowed_origin = response.headers["access-control-allow-origin"]
        assert allowed_origin in [origin, "*"]


def test_dashboard_overview_smoke():
    """Smoke test for Command Center overview payload."""
    response = client.get("/api/v1/dashboard/overview")
    assert response.status_code == 200
    data = response.json()
    assert "hospital_name" in data
    assert "active_census" in data
    assert "bed_occupancy_pct" in data
    assert "forecast_next_1h" in data
    assert len(data["profiles"]) >= 1


def test_forecasts_smoke():
    """Smoke test for arrival forecasting endpoints."""
    response = client.get("/api/v1/forecasts?horizon_hours=24&model_name=lightgbm")
    assert response.status_code == 200
    data = response.json()
    assert data["model_name"] == "lightgbm"
    assert len(data["points"]) == 24
    assert "metrics" in data
    assert "mae" in data["metrics"]


def test_analytics_bottlenecks_smoke():
    """Smoke test for bottleneck sensitivity analytics."""
    response = client.get("/api/v1/analytics/bottlenecks?hospital_profile=urban&arrival_surge_pct=20.0")
    assert response.status_code == 200
    data = response.json()
    assert "bottlenecks" in data
    assert "resource_utilization" in data
    assert "stage_wait_decomposition" in data


def test_models_metrics_smoke():
    """Smoke test for model intelligence comparison metrics."""
    response = client.get("/api/v1/models/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "model_comparison" in data
    assert "lightgbm" in data["model_comparison"]
    assert "seasonal_naive" in data["model_comparison"]
    assert "calibration" in data
