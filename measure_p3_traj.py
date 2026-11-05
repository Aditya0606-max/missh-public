# measure_p3.py — part 3a: relationships over the last 6 h (block HR-MAP,
# step kinds, lead-pair block) and coupling change (4 h window vs ruler hours).
# Symmetric sampling: det lookbacks k = 0,1,2,4,6 and stable at every hour.
import numpy as np
import pandas as pd
from itertools import combinations

CH = ["hr", "map", "rr", "spo2"]
SDPOP = np.array([3.706, 5.975, 2.608, 1.211])
PAIRS = list(combinations(range(4), 2))
LOOK = tuple(range(13))

v = pd.read_csv("../missh_data/vitals_hourly_cal_v2.csv")
for c in ["block_bolus", "block_iv", "sed_infusion"]:
    v[c] = v[c].astype(str).str.lower().eq("true")
v["blocked"] = v.block_bolus | v.block_iv | v.sed_infusion
rul = pd.read_csv("../missh_data/rulers_cal_v3.csv")
anc = pd.read_csv("../missh_data/anchors_cal_v2.csv")
news = pd.read_csv("../missh_data/news_hourly_cal.csv").set_index(["stay_id", "hour_idx"])

RAW = {}
for sid, g in v.groupby("stay_id"):
    RAW[sid] = {int(r.hour_idx): np.array([r[c] for c in CH], float)
                for _, r in g.iterrows()
                if not r.blocked and np.isfinite([r[c] for c in CH]).sum() >= 2}
RUL = {}
for sid, g in rul[rul.arm == "main"].groupby("stay_id"):
    g = g.set_index("channel")
    RUL[sid] = (np.array([g.centre.get(c, np.nan) for c in CH], float),
                np.array([g.sd_used.get(c, np.nan) for c in CH], float))

def corr(a, b):
    m = np.isfinite(a) & np.isfinite(b)
    if m.sum() < 3 or np.std(a[m]) == 0 or np.std(b[m]) == 0:
        return np.nan
    return float(np.corrcoef(a[m], b[m])[0, 1])

def rel(sid, h):
    d = RAW.get(sid, {})
    steps = [(d[hh] - d[hh - 1]) for hh in range(h - 5, h + 1) if hh in d and hh - 1 in d]
    out = {}
    hm = [s for s in steps if np.isfinite(s[0]) and np.isfinite(s[1])]
    out["block_hrmap"] = float(np.mean([(s[0] / SDPOP[0]) * (s[1] / SDPOP[1]) for s in hm])) if len(hm) >= 2 else np.nan
    big = [s for s in hm if abs(s[0]) >= 1 and abs(s[1]) >= 1]
    if len(big) >= 2:
        out["share_defend"] = float(np.mean([s[0] > 0 and s[1] < 0 for s in big]))
        out["share_recover"] = float(np.mean([s[0] < 0 and s[1] > 0 for s in big]))
        out["share_bothdown"] = float(np.mean([s[0] < 0 and s[1] < 0 for s in big]))
    else:
        out["share_defend"] = out["share_recover"] = out["share_bothdown"] = np.nan
    out["lead_block"] = np.nan
    if sid in RUL and h in d and len(steps) >= 2:
        z = (d[h] - RUL[sid][0]) / RUL[sid][1]
        if np.isfinite(z).sum() >= 2:
            zz = np.where(np.isfinite(z), z ** 2, 0.0)
            i, j = max(PAIRS, key=lambda p: zz[p[0]] + zz[p[1]])
            pv = [(s[i] / SDPOP[i]) * (s[j] / SDPOP[j]) for s in steps if np.isfinite(s[i]) and np.isfinite(s[j])]
            out["lead_block"] = float(np.mean(pv)) if len(pv) >= 2 else np.nan
    win = [hh for hh in range(h - 3, h + 1) if hh in d]
    base = [hh for hh in range(0, 3) if hh in d]
    if len(win) >= 4 and len(base) >= 3:
        rw = corr(np.array([d[x][0] for x in win]), np.array([d[x][1] for x in win]))
        rb = corr(np.array([d[x][0] for x in base]), np.array([d[x][1] for x in base]))
        out["drho"] = abs(rw - rb) if np.isfinite(rw) and np.isfinite(rb) else np.nan
    else:
        out["drho"] = np.nan
    nw = news.loc[(sid, h)] if (sid, h) in news.index else None
    out["news"] = float(nw.news) if nw is not None else np.nan
    out["news_items"] = float(nw.n_items) if nw is not None else np.nan
    return out

rows = []
T = anc[anc.target & anc.open_h.notna()]
for _, a in T[T.cohort == "deteriorating"].iterrows():
    for k in LOOK:
        if pd.isna(a.anchor):
            continue
        h = int(np.floor(a.anchor - k)) - 1
        if h >= a.open_h:
            rows.append(dict(stay_id=a.stay_id, cohort="det", k=k, hour=h, tier=a.ptier,
                             anchor_type=str(a.anchor_type), dni=bool(a.dni_before), **rel(a.stay_id, h)))
for _, a in T[T.cohort == "stable"].iterrows():
    for h in range(int(a.open_h), 72):
        rows.append(dict(stay_id=a.stay_id, cohort="stable", k=np.nan, hour=h, tier=a.ptier,
                         anchor_type="", dni=False, **rel(a.stay_id, h)))

M = pd.DataFrame(rows)
M.to_csv("../missh_data/measures_p3_traj.csv", index=False)
d = M[M.cohort == "det"]
print("MEASURE_P3 table built")
print(d.groupby("k").stay_id.nunique().rename("det patients per lookback").to_string())
print(f"stable rows {int((M.cohort=='stable').sum())}  patients {M[M.cohort=='stable'].stay_id.nunique()}")
cols = ["block_hrmap", "share_defend", "share_recover", "share_bothdown", "lead_block", "drho"]
print("non-missing share:", M[cols].notna().mean().round(3).to_dict())
