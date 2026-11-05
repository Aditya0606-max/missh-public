# arrival_01.py — EXPLORATORY (docs/EXPLORATORY.md E1), post-result.
# Vital-sign LEVELS in hours 0-2: fast (readable 78 vs unreadable) vs stable.
import numpy as np
import pandas as pd

CH = ["hr", "map", "rr", "spo2"]
OUT = "ARRIVAL_RESULTS.txt"

def load(p):
    d = pd.read_csv(p)
    d["blocked"] = d["blocked"].astype(str).str.lower().eq("true")
    return d.sort_values(["stay_id", "hour_idx"])

hyp = load("../missh_data/hyper_hourly_cal.csv")
stb = load("../missh_data/phi_hourly_cal_tight.csv")

readable = set()
for sid, g in hyp.groupby("stay_id"):
    last = int(np.floor(g.esc_h.iloc[0] - 1))
    c = g[(g.hour_idx <= last) & (~g.blocked)]
    if (c[CH].notna().sum(axis=1) >= 2).sum() >= 2:
        readable.add(sid)

h02 = hyp[(hyp.hour_idx <= 2) & (hyp.hour_idx + 1 <= hyp.esc_h)]
s02 = stb[stb.hour_idx <= 2]

def levels(df):
    return df.groupby("stay_id")[CH].mean()

sets = {
    "stable": s02,
    "fast_all": h02,
    "fast_readable": h02[h02.stay_id.isin(readable)],
    "fast_unreadable": h02[~h02.stay_id.isin(readable)],
}

L = ["ARRIVAL_RESULTS — EXPLORATORY E1 (post-result), hours 0-2 levels", ""]
for name, d in sets.items():
    g = levels(d)
    L.append(f"[{name}] patients={d.stay_id.nunique()}  with any vital={len(g.dropna(how='all'))}")
    for c in CH:
        s = g[c].dropna()
        L.append(f"   {c:5s} n={len(s):4d}  median {s.median():6.1f}  "
                 f"IQR {s.quantile(.25):6.1f}-{s.quantile(.75):6.1f}")
    L.append(f"   MAP<65 {(g['map'] < 65).mean():.3f}  HR>100 {(g['hr'] > 100).mean():.3f}  "
             f"RR>20 {(g['rr'] > 20).mean():.3f}  SpO2<94 {(g['spo2'] < 94).mean():.3f}")
    L.append(f"   hours 0-2 blocked by treatment: {d.blocked.mean():.3f}   "
             f"hours with no vitals: {d[CH].isna().all(axis=1).mean():.3f}")
    L.append("")
text = "\n".join(L)
print(text)
open(OUT, "w").write(text + "\n")
