"""Synthetic emergency department operational data and hourly arrival generator."""
import datetime
import math
import random
from typing import Any, Dict, List

import numpy as np
import pandas as pd


def generate_synthetic_hourly_arrivals(
    start_date: datetime.datetime = datetime.datetime(2025, 1, 1, 0, 0),
    num_days: int = 180,
    base_rate: float = 12.5,
    seed: int = 42,
) -> pd.DataFrame:
    """Generates synthetic hourly arrival series with diurnal, weekly, and seasonal components."""
    np.random.seed(seed)
    random.seed(seed)

    total_hours = num_days * 24
    timestamps = [start_date + datetime.timedelta(hours=i) for i in range(total_hours)]

    # Base diurnal weights (24 hours)
    diurnal_weights = np.array([
        0.48, 0.38, 0.32, 0.28, 0.30, 0.42,
        0.65, 0.90, 1.15, 1.35, 1.45, 1.40,
        1.32, 1.28, 1.25, 1.22, 1.20, 1.25,
        1.30, 1.28, 1.15, 0.95, 0.75, 0.58
    ])

    # Day-of-week multipliers (0=Monday, 6=Sunday)
    # Mondays have highest ED volume; weekends have moderate daytime volume
    dow_multipliers = np.array([1.18, 1.05, 1.00, 0.98, 1.02, 0.92, 0.88])

    records = []
    for dt in timestamps:
        hour = dt.hour
        dow = dt.weekday()
        day_of_year = dt.timetuple().tm_yday

        # Seasonal component (slight winter bump around Dec-Feb)
        seasonal_mult = 1.0 + 0.12 * math.cos(2 * math.pi * (day_of_year - 15) / 365.25)

        expected_lambda = base_rate * diurnal_weights[hour] * dow_multipliers[dow] * seasonal_mult

        # Occasional random shock (surge events like storm or viral outbreak)
        if random.random() < 0.015:
            expected_lambda *= random.uniform(1.3, 1.6)

        # Draw arrivals from Poisson distribution
        arrivals = int(np.random.poisson(max(0.5, expected_lambda)))

        records.append({
            "timestamp": dt,
            "arrivals": arrivals,
            "hour": hour,
            "day_of_week": dow,
            "is_weekend": int(dow >= 5),
            "month": dt.month,
            "day_of_year": day_of_year,
            "expected_rate": round(expected_lambda, 2),
        })

    df = pd.DataFrame(records)
    df.set_index("timestamp", inplace=True)
    return df


def generate_synthetic_patient_records(
    hourly_df: pd.DataFrame,
    max_records: int = 5000,
    seed: int = 42,
) -> pd.DataFrame:
    """Generates synthetic patient-level events conforming to the Phase 2 clinical schema."""
    random.seed(seed)
    np.random.seed(seed)

    patient_records: List[Dict[str, Any]] = []
    patient_id_counter = 1

    for ts, row in hourly_df.head(24 * 30).iterrows():  # Sample 30 days
        num_patients = int(row["arrivals"])
        for _ in range(num_patients):
            if patient_id_counter > max_records:
                break

            arrival_min_offset = random.randint(0, 59)
            arr_time = ts + datetime.timedelta(minutes=arrival_min_offset)

            # Acuity distribution: ESI 1: 3%, ESI 2: 18%, ESI 3: 45%, ESI 4: 24%, ESI 5: 10%
            roll = random.random()
            if roll < 0.03:
                esi = 1
                mode = "AMBULANCE"
                bed_req = True
                serv_cat = "TRAUMA" if random.random() < 0.4 else "MEDICAL"
            elif roll < 0.21:
                esi = 2
                mode = "AMBULANCE" if random.random() < 0.55 else "WALK_IN"
                bed_req = True
                serv_cat = random.choice(["MEDICAL", "SURGICAL", "CARDIAC"])
            elif roll < 0.66:
                esi = 3
                mode = "AMBULANCE" if random.random() < 0.20 else "WALK_IN"
                bed_req = True
                serv_cat = random.choice(["MEDICAL", "PEDIATRIC", "SURGICAL"])
            elif roll < 0.90:
                esi = 4
                mode = "WALK_IN"
                bed_req = (random.random() < 0.5)
                serv_cat = "MEDICAL"
            else:
                esi = 5
                mode = "WALK_IN"
                bed_req = False
                serv_cat = "MEDICAL"

            age_group = random.choices(["pediatric", "adult", "geriatric"], weights=[0.20, 0.55, 0.25])[0]

            # Service durations in minutes (LogNormal)
            reg_dur = round(max(2.0, float(np.random.lognormal(np.log(4.5), 0.3))), 1)
            triage_dur = round(max(3.0, float(np.random.lognormal(np.log(5.5), 0.3))), 1)
            assess_dur = round(max(5.0, float(np.random.lognormal(np.log(15.0), 0.35))), 1)
            diag_dur = round(max(15.0, float(np.random.lognormal(np.log(30.0), 0.4))), 1) if (esi <= 3 and random.random() < 0.65) else 0.0
            treat_dur = round(max(10.0, float(np.random.lognormal(np.log(35.0), 0.4))), 1)
            obs_dur = round(max(60.0, float(np.random.lognormal(np.log(180.0), 0.4))), 1) if (esi <= 3 and random.random() < 0.15) else 0.0

            total_los_min = reg_dur + triage_dur + assess_dur + diag_dur + treat_dur + obs_dur + random.uniform(10.0, 40.0) # includes waiting
            dep_time = arr_time + datetime.timedelta(minutes=total_los_min)

            outcome = "ADMITTED" if esi <= 2 or (esi == 3 and random.random() < 0.4) else "DISCHARGED"

            patient_records.append({
                "event_id": f"EVT-{patient_id_counter:07d}",
                "patient_id": f"SYNTH-PT-{patient_id_counter:06d}",
                "arrival_timestamp": arr_time.isoformat(),
                "triage_priority": esi,
                "arrival_mode": mode,
                "age_group": age_group,
                "service_category": serv_cat,
                "registration_duration": reg_dur,
                "assessment_duration": assess_dur,
                "diagnostic_duration": diag_dur,
                "treatment_duration": treat_dur,
                "observation_duration": obs_dur,
                "departure_timestamp": dep_time.isoformat(),
                "bed_required": bed_req,
                "simulated_outcome": outcome,
                "total_los_minutes": round(total_los_min, 1)
            })
            patient_id_counter += 1

    return pd.DataFrame(patient_records)
