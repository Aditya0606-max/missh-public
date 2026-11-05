# freeze_fast_refs.py — freeze calibration stable references for P3-P5 (fast group).
import json
import numpy as np
import pandas as pd

CH = ["hr", "map", "rr", "spo2"]
SD = np.array([3.743, 5.941, 2.600, 1.211])
W = np.array([1.0, -1.0, 1.0, -1.0])
v = pd.read_csv("../missh_data/vitals_hourly_cal.csv")
for c in ["blocked", "sedated"]:
    v[c] = v[c].astype(str).str.lower().eq("true")
out = pd.read_csv("../missh_data/outcome_cal.csv")
stable = set(out.stay_id[out.label == "stable"])

def snorm(d):
    m = ~np.isnan(d)
    return np.nan if m.sum() < 2 else float(np.sqrt(4.0 / m.sum() * np.sum(d[m] ** 2)))
def cosw(d):
    m = ~np.isnan(d)
    if m.sum() < 2: return np.nan
    na = np.linalg.norm(d[m])
    return np.nan if na == 0 else float(d[m] @ W[m] / (na * np.linalg.norm(W[m])))

cos_ref, blk_ref, bend_ref = [], [], []
for sid, g in v[(v.hour_idx <= 4) & v.stay_id.isin(stable)].groupby("stay_id"):
    x = {}
    for _, r in g.iterrows():
        if r.blocked or r.sedated: continue
        vec = np.array([r[c] for c in CH], float) / SD
        if (~np.isnan(vec)).sum() >= 2: x[int(r.hour_idx)] = vec
    for h in sorted(x):
        if h - 1 in x:
            a = x[h] - x[h - 1]
            c = cosw(a)
            if not np.isnan(c): cos_ref.append(c)
            if not (np.isnan(a[0]) or np.isnan(a[1])): blk_ref.append(float(a[0] * a[1]))
            if h - 2 in x:
                a1 = x[h - 1] - x[h - 2]; c1 = cosw(a1)
                if not (np.isnan(c1) or np.isnan(c)): bend_ref.append((c - c1) * snorm(a))
refs = {"source": "calibration stable, hours 0-4, clean (A13), SD_POP_TIGHT",
        "SD_tight": SD.tolist(), "bend_line_95": 5.434,
        "cos": sorted(cos_ref), "block": sorted(blk_ref), "bend": sorted(bend_ref)}
json.dump(refs, open("FAST_REFS.json", "w"))
print(f"frozen: cos {len(cos_ref)}  block {len(blk_ref)}  bend {len(bend_ref)}  "
      f"bend 95th recomputed {np.percentile(bend_ref, 95):.3f} (registered 5.434)")
