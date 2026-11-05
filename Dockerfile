# Multi-stage Dockerfile for MedFlow Hospital Operations Digital Twin

# Stage 1: Build React Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Production Python Backend & Static Serving
FROM python:3.12-slim AS runner
WORKDIR /app

# Install system dependencies including OpenMP for LightGBM/XGBoost
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# Copy application modules
COPY backend ./backend
COPY ml ./ml
COPY simulation ./simulation
COPY optimization ./optimization
COPY scripts ./scripts

# Copy built frontend assets to static directory for unified serving
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Initialize demo datasets and models
RUN python scripts/bootstrap_demo.py

ENV PORT=8000
EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
