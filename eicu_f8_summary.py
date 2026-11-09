import pandas as pd, numpy as np
P = pd.read_csv("eicu_f8_hours.csv"); F = pd.read_csv("eicu_f8_first.csv")
rows, pooled = [], []
for (sid, who, wh), g in P.groupby(["patientunitstayid", "who", "window_h"]):
    T = int(np.ceil(min(wh, 72))); g = g.set_index("h")
    full = g.reindex(range(-12, T)).fillna(0)
    info = (full.fi + full.dev).clip(0, 1).replace(0, np.nan).ffill(limit=12).fillna(0).loc[0:T - 1]
    hrs = full.loc[0:T - 1]
    rows.append(dict(who=who, vit=hrs.vit.mean(), bp=hrs.bp.mean(), gcs=hrs.gcs.mean(), fio2_info=info.mean()))
    pooled.append((who, T, (1 - info).sum()))
R = pd.DataFrame(rows); Q = pd.DataFrame(pooled, columns=["who", "hours", "noF_hours"])
print("Median share of pre-tip hours (<= 72 h) with each signal, by cast:")
print(R.groupby("who")[["vit", "bp", "gcs", "fio2_info"]].median().round(2).to_string(), "\n")
S = Q.groupby("who").sum(); S["no_FiO2_share"] = (S.noF_hours / S.hours).round(2)
print("Share of hours with NO FiO2/oxygen information (12-h carry-forward), pooled by cast:\n" + S[["hours", "no_FiO2_share"]].to_string())
allshare = Q.noF_hours.sum() / Q.hours.sum()
print(f"\nPOOLED no-FiO2 share, all cast: {allshare:.2f}  -> breathing reading for eICU: "
      + ("FALLBACK (S/F + RR-led effort)" if allshare >= 0.40 else "FROZEN S/F"))
print("\nMinutes to first vital sign, by cast (median, 75th pct, share with none):")
print(F.groupby("who").first_vital_min.agg(median="median", q75=lambda s: s.quantile(.75), none=lambda s: s.isna().mean()).round(1).to_string())
