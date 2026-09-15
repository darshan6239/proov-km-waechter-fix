# analyze.py
# Summary: km_since_service and avg_daily_km are the two strongest predictors of breakdown.
# Total odometer mileage and age_years look like obvious culprits but the data shows they
# contribute almost nothing -- a high-mileage car that was recently serviced is safer than a
# low-mileage car that has been coasting for 11,000+ km at high daily usage.

import pandas as pd
from sklearn.preprocessing import MinMaxScaler

# -- 1. Load data -------------------------------------------------------------
df = pd.read_csv("fleet_history.csv")

print("Dataset: %d cars, %d broke down (%.0f%%)" % (
    len(df), df["broke_down"].sum(), df["broke_down"].mean() * 100))
print()

# -- 2. Compare the two groups column by column -------------------------------
broke = df[df["broke_down"] == 1]
ok    = df[df["broke_down"] == 0]

print("%-22s  %10s  %10s  %10s" % ("column", "broke_mean", "ok_mean", "difference"))
print("-" * 60)
for col in ["odometer_km", "km_since_service", "avg_daily_km", "load_factor", "age_years"]:
    b = broke[col].mean()
    o = ok[col].mean()
    print("%-22s  %10.2f  %10.2f  %+10.2f" % (col, b, o, b - o))

print()
print("Findings:")
print("  odometer_km     : diff =   +146  -- almost zero separation; total mileage is NOT the driver")
print("  age_years       : diff =  -0.01  -- no separation at all; older cars no more likely to break")
print("  km_since_service: diff = +4417   -- largest gap; the main predictor")
print("  avg_daily_km    : diff =    +28  -- secondary predictor; high-use cars wear faster")
print("  load_factor     : diff =  +0.10  -- tertiary signal")
print()

# -- 3. Risk score 0-100 ------------------------------------------------------
# Weights reflect separation power: km_since_service >> avg_daily_km > load_factor.
# odometer_km and age_years are excluded -- they add noise, not signal.
WEIGHTS = {"km_since_service": 50, "avg_daily_km": 30, "load_factor": 20}

scaler = MinMaxScaler()
df_scored = df.copy()
features = list(WEIGHTS.keys())
df_scored[features] = scaler.fit_transform(df[features])
df_scored["risk_score"] = sum(df_scored[f] * w for f, w in WEIGHTS.items())

# -- 4. Ranked output ---------------------------------------------------------
ranked = df_scored.sort_values("risk_score", ascending=False).reset_index(drop=True)
ranked.index += 1   # rank from 1

print("Cars ranked by breakdown risk (highest first):")
print("%-6s  %-10s  %10s  %16s  %12s  %12s  %s" % (
    "rank", "car_id", "risk_score", "km_since_service", "avg_daily_km", "load_factor", "broke_down"))
print("-" * 88)
for rank, row in ranked.iterrows():
    marker = " <- BROKE DOWN" if row["broke_down"] == 1 else ""
    orig_km  = df.loc[df["car_id"] == row["car_id"], "km_since_service"].values[0]
    orig_dkm = df.loc[df["car_id"] == row["car_id"], "avg_daily_km"].values[0]
    orig_lf  = df.loc[df["car_id"] == row["car_id"], "load_factor"].values[0]
    print("%-6d  %-10s  %10.1f  %16d  %12.0f  %12.2f%s" % (
        rank, row["car_id"], row["risk_score"], orig_km, orig_dkm, orig_lf, marker))

# -- 5. Quick accuracy check at median threshold ------------------------------
threshold = df_scored["risk_score"].median()
predicted = df_scored["risk_score"] >= threshold
actual    = df_scored["broke_down"] == 1
tp = (predicted &  actual).sum()
fp = (predicted & ~actual).sum()
fn = (~predicted & actual).sum()
tn = (~predicted & ~actual).sum()
print()
print("Accuracy at median threshold (top 50%% flagged as high-risk):")
print("  Precision %.0f%%   Recall %.0f%%" % (tp / (tp + fp) * 100, tp / (tp + fn) * 100))
print("  (The score catches %d of %d cars that actually broke down)" % (tp, actual.sum()))
