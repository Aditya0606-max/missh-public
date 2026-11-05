# d2_combined_ci.py — D2: patient-bootstrap CI for the A16 combined model.
# Scoring copied unchanged from rank_01.py (lines 69-93); boot() unchanged (36-44).
import json
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

rng = np.random.default_rng(2026)

def boot(d, col, base, n=300):
    ids = d.sid.unique(); idx = {i: np.where(d.sid.values == i)[0] for i in ids}; out = []
    for _ in range(n):
        sel = np.concatenate([idx[i] for i in rng.choice(ids, len(ids))])
        x = d.iloc[sel]
        if x.y.nunique() < 2:
            continue
        out.append(roc_auc_score(x.y, x[col]) - roc_auc_score(x.y, x[base]))
    return np.percentile(out, [2.5, 97.5])

F = json.load(open("COMBINED_FROZEN.json"))
p1 = pd.read_csv("../missh_data/measures_p1.csv", low_memory=False)
p2 = pd.read_csv("../missh_data/measures_p2.csv", low_memory=False)
p3 = pd.read_csv("../missh_data/measures_p3.csv", low_memory=False)
for p in (p1, p2, p3):
    p["kk"] = p.k.fillna(-1)
K = ["stay_id", "cohort", "kk", "hour"]
FE = F["features"]
B = (p2[K + ["tier", "news"] + [f for f in FE if f in p2.columns]]
     .merge(p3[K + [f for f in FE if f in p3.columns]], on=K, how="left")
     .merge(p1[K + [f for f in FE if f in p1.columns]], on=K, how="left"))
for f in FE:
    B[f] = (B[f].fillna(F["median"][f]) - F["mean"][f]) / F["sd"][f]
B["news"] = B.news.fillna(F["news_median"])
for t in F["tiers"]:
    B[f"t_{t}"] = (B.tier == t).astype(float)

L = ["D2 — combined model (A16), patient-bootstrap 95% CI, test split", ""]
verdict = "not computed"
for k, m in F["models"].items():
    h0, h1 = m["stable_hour_range"]
    d = pd.concat([B[(B.cohort == "det") & (B.kk == int(k))],
                   B[(B.cohort == "stable") & B.hour.between(h0, h1)]])
    y = (d.cohort == "det").astype(int).values
    sc = {nm: d[m[nm]["columns"]].values @ np.array(m[nm]["coef"]) + m[nm]["intercept"] for nm in ("A", "B")}
    aa, ab = roc_auc_score(y, sc["A"]), roc_auc_score(y, sc["B"])
    d = d.assign(y=y, sid=d.stay_id.values, sA=sc["A"], sB=sc["B"])
    lo, hi = boot(d, "sB", "sA")
    tag = "  [primary]" if str(k) == "2" else ""
    L.append(f"   k={k}: det pts {d[d.y == 1].sid.nunique()}  stable pts {d[d.y == 0].sid.nunique()}  "
             f"AUC A {aa:.3f}  AUC B {ab:.3f}  gain {ab - aa:+.3f} ({lo:+.3f} to {hi:+.3f}){tag}")
    if str(k) == "2":
        verdict = "SUPPORT=yes" if (ab - aa > 0 and lo > 0) else "SUPPORT=no"
L += ["", f"A16 at k = 2 h: {verdict}"]
text = "\n".join(L); print(text); open("D2_COMBINED.txt", "w").write(text + "\n")
