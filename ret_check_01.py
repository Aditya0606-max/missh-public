# ret_check_01.py — is "hours since return" an artifact of missing/blocked hours?
import numpy as np
import pandas as pd

CH = ["hr", "map", "rr", "spo2"]
SDPOP = np.array([3.706, 5.975, 2.608, 1.211]); W = np.array([1., -1., 1., -1.])
v = pd.read_csv("../missh_data/vitals_hourly_cal_v2.csv")
for c in ["block_bolus", "block_iv", "sed_infusion"]:
    v[c] = v[c].astype(str).str.lower().eq("true")
v["blocked"] = v.block_bolus | v.block_iv | v.sed_infusion
anc = pd.read_csv("../missh_data/anchors_cal_v2.csv")
C = {}
for sid, g in v.groupby("stay_id"):
    C[sid] = {int(r.hour_idx): np.array([r[c] for c in CH], float) / SDPOP
              for _, r in g.iterrows()
              if not r.blocked and np.isfinite([r[c] for c in CH]).sum() >= 2}
def snorm(a):
    m = ~np.isnan(a); return np.nan if m.sum() < 2 else float(np.sqrt(4 / m.sum() * np.sum(a[m]**2)))
def cosw(a):
    m = ~np.isnan(a); n = np.linalg.norm(a[m]) if m.sum() >= 2 else 0
    return np.nan if n == 0 else float(a[m] @ W[m] / (n * np.linalg.norm(W[m])))
def feats(sid, op, h):
    d = C.get(sid, {}); gap = 0; steps_since = 0
    for hh in range(int(op), h + 1):
        if hh in d and hh - 1 in d:
            a = d[hh] - d[hh - 1]; L, cs = snorm(a), cosw(a)
            if not np.isnan(L) and L >= 1 and not np.isnan(cs) and cs < 0:
                steps_since = 0
            else:
                steps_since += 1
        else:
            gap += 1
    return gap, steps_since
rows = []
T = anc[anc.target & anc.open_h.notna()]
for _, a in T.iterrows():
    if a.cohort == "deteriorating" and pd.notna(a.anchor):
        for k in (0, 2):
            h = int(np.floor(a.anchor - k)) - 1
            if h >= a.open_h:
                rows.append((a.stay_id, "det", k, h, a.ptier, *feats(a.stay_id, a.open_h, h)))
    elif a.cohort == "stable":
        for h in range(int(a.open_h), 72):
            rows.append((a.stay_id, "stable", np.nan, h, a.ptier, *feats(a.stay_id, a.open_h, h)))
R = pd.DataFrame(rows, columns=["sid", "cohort", "k", "hour", "tier", "gap_hours", "clean_steps_since_ret"])
S = R[R.cohort == "stable"]
def mauc(d, col):
    p = []
    for _, r in d.iterrows():
        ref = S[(S.tier == r.tier) & S.hour.between(r.hour - 2, r.hour + 2)][col].values
        if len(ref) >= 30:
            p.append((ref < r[col]).mean() + 0.5 * (ref == r[col]).mean())
    return np.mean(p), len(p)
L = ["RET_CHECK — matched (tier, hour +-2) AUC; 0.5 = no difference"]
for k in (0, 2):
    d = R[(R.cohort == "det") & (R.k == k)]
    for col in ("gap_hours", "clean_steps_since_ret"):
        a, n = mauc(d, col); L.append(f"k={k}  {col:22s} AUC {a:.3f}  n={n}")
text = "\n".join(L); print(text); open("RET_CHECK.txt", "w").write(text + "\n")
