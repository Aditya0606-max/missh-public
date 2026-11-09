import pandas as pd, numpy as np
src = open("c14_replay.py").read(); exec(src.split("B = pd.read_csv")[0])
Bo = pd.read_csv("m3_bolus.csv")[["icustay_id", "h"]]; fb = Bo[Bo.h >= 0].groupby("icustay_id").h.min()
parts = []
for sid, g in H.groupby("icustay_id"):
    who, tip = g.who.iloc[0], g.tip.iloc[0]; T = int(min(np.ceil(tip), 72))
    g = g.set_index("hour").reindex(range(T)); rd = g[FC].mean(axis=1)
    parts.append(pd.DataFrame({"icustay_id": sid, "who": who, "tip": tip, "hour": range(T),
        "road": rd.values, "road3": rd.rolling(3, min_periods=1).mean().values, "si": g.si.values,
        "negmap": -g.mp.values, "news": g.news.values, "news3": g.news.rolling(3, min_periods=1).mean().values}))
L = pd.concat(parts, ignore_index=True)
SC = ["road", "road3", "si", "negmap", "news", "news3"]
for s in SC: L["p_" + s] = L.groupby("icustay_id")[s].shift(1)
days = L.groupby("who").size() / 24
A = L[L.who == "Ajay"]; K = L[L.who == "Kranthi"]; Su = L[L.who == "Sundar"]
nK, nS = K.icustay_id.nunique(), Su.icustay_id.nunique()
def cost(s, t):
    x = A[s].values; p = np.nan_to_num(A["p_" + s].values, nan=-np.inf)
    return np.sum((x >= t) & (p < t)) / days["Ajay"]
print("Budget = false alarm episodes per Ajay-day. Lead = median hours before tip among warned.\n")
for b in (0.2, 0.44, 1.0, 1.97):
    print(f"==== Budget {b} ====")
    for s in SC:
        cand = np.unique(np.nanquantile(A[s].values, np.linspace(0.5, 0.9999, 400)))
        ok = [t for t in cand if cost(s, t) <= b]
        if not ok: print(f"  {s:7s} cannot reach budget"); continue
        t = ok[0]; c = cost(s, t)
        hit = K[K[s] >= t].groupby("icustay_id").hour.min()
        tipK = K.groupby("icustay_id").tip.first()
        lead = (tipK[hit.index] - hit).median()
        bol = fb.reindex(hit.index); before = ((hit < bol) | bol.isna()).mean() if len(hit) else np.nan
        sh = Su[Su[s] >= t].icustay_id.nunique() / nS
        print(f"  {s:7s} line {t:7.2f} (actual cost {c:.2f})  Kranthi warned {len(hit) / nK:.2f}  lead {lead:5.1f} h  "
              f"before 1st bolus {before:.2f}  | Sundar warned {sh:.2f}")
    print()
