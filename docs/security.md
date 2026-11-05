# Operational Safety & Ethics Guidelines

## Clinical Non-Intervention Mandate
> **IMPORTANT:** MedFlow is strictly an educational simulation and operations research platform. It is designed solely for capacity planning, staffing shift allocation modeling, and queue bottleneck diagnostics.
> 
> - **No Medical Diagnosis:** MedFlow does not evaluate patient clinical conditions or prescribe treatments.
> - **No Clinical Triage:** Emergency Severity Index (ESI) classifications modeled in this platform are synthetic operational attributes, not real-time clinical recommendations.
> - **Simulation Boundary:** All optimization outputs are candidate operational plans intended for administrative evaluation and human supervisory validation.

## Data Provenance & Privacy
- **Synthetic Data Generation:** MedFlow utilizes non-homogeneous Poisson processes calibrated to published emergency medicine epidemiological literature. No Protected Health Information (PHI) or real patient records are processed or stored.
- **HIPAA Exemption:** Because all data is purely synthetic and mathematically generated, no HIPAA privacy rules are violated.

## Computational Safeguards
- **Max Simulation Duration:** Capped at 168 hours (1 week) to prevent unbounded memory allocation.
- **Monte Carlo Replications:** Capped at 30 replications per request.
- **CP-SAT Solver Time Limit:** Capped at 30 seconds to prevent thread starvation.
- **CORS & Rate Limiting:** Enforces allowed origin headers and protects API endpoints against Denial of Service.
