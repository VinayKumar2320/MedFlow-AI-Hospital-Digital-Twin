# ==============================================================================
# MedFlow Backend — Production Dockerfile for Cloud Hosting (Render / Railway / Fly)
# ==============================================================================
FROM python:3.12-slim AS runner

WORKDIR /app

# Prevent Python from writing .pyc files and buffer stdout/stderr for real-time logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    ENVIRONMENT=production \
    PYTHONPATH=/app

# Install essential system runtime libraries (libgomp1 for OpenMP acceleration in LightGBM/XGBoost)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# Copy backend application, ML artifacts, simulation, and optimization engines
COPY backend ./backend
COPY ml ./ml
COPY simulation ./simulation
COPY optimization ./optimization
COPY scripts ./scripts

# Install medflow package in editable mode so setuptools discovers all packages
RUN pip install --no-cache-dir --no-deps -e .

# Initialize database schema and pre-bake synthetic baseline data during build
# so cold-starts consume minimal memory (<150MB RAM)
RUN PYTHONPATH=/app python scripts/bootstrap_demo.py

# Expose default port
EXPOSE 8000

# Health check probe
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/api/v1/health || exit 1

# Production startup dynamically binding to $PORT provided by cloud host
CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1 --timeout-keep-alive 65"]
