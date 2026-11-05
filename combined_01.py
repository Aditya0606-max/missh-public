# combined_01.py — E6: does the architecture as a whole add to NEWS?
# Cross-validated by patient on the 20%. Nothing is frozen here.
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold
from sklearn.metrics import roc_auc_score

rng = np.random.default_rng(2026)
p1 = pd.read_csv("../missh_data/measures_p1.csv", low_memory=False)
p2 = pd.read_csv("../missh_data/measures_p2.csv", low_memory=False)
p3 = pd.read_csv("../missh_data/measures_p3.csv", low_memory=False)
for p in (p1, p2, p3):
    p["kk"] = p.k.fillna(-1)
KEYS = ["stay_id", "cohort", "kk", "hour"]
F1 = ["D_main", "Dw_main", "D_o", "Dw_o"]
F2 = ["consist", "straight", "speed", "bend", "counter", "since_ret"]
F3 = ["block_hrmap", "share_defend", "share_recover", "share_bothdown", "lead_block"]
FEATS = F1 + F2 + F3

B = (p2[KEYS + ["tier", "news"] + F2]
     .merge(p3[KEYS + F3], on=KEYS, how="left")
     .merge(p1[KEYS + F1], on=KEYS, how="left"))
ST = B[B.cohort == "stable"]
med = ST[FEATS].median()
mu, sd = ST[FEATS].fillna(med).mean(), ST[FEATS].fillna(med).std().replace(0, 1)
news_med = ST.news.median()
B[FEATS] = (B[FEATS].fillna(med) - mu) / sd
B["news"] = B.news.fillna(news_med)
TIERS = sorted(B.tier.dropna().unique())
for t in TIERS:
    B[f"t_{t}"] = (B.tier == t).astype(float)
BASE = ["news", "hour"] + [f"t_{t}" for t in TIERS]

def cv_preds(X, y, g):
    p = np.zeros(len(y))
    for tr, te in GroupKFold(5).split(X, y, g):
        m = LogisticRegression(C=0.5, class_weight="balanced", max_iter=3000)
        m.fit(X[tr], y[tr])
        p[te] = m.predict_proba(X[te])[:, 1]
    return p

def boot_diff(y, pa, pb, g, n=300):
    ids = np.unique(g)
    idx = {i: np.where(g == i)[0] for i in ids}
    out = []
    for _ in range(n):
        sel = np.concatenate([idx[i] for i in rng.choice(ids, len(ids))])
        if y[sel].min() == y[sel].max():
            continue
        out.append(roc_auc_score(y[sel], pb[sel]) - roc_auc_score(y[sel], pa[sel]))
    return np.percentile(out, [2.5, 97.5])

L = ["COMBINED_RESULTS — E6, cross-validated by patient on the 20%",
     "A = NEWS + hour + tier;  B = A + 15 architecture measures", ""]
for k in (0, 1, 2, 4):
    det = B[(B.cohort == "det") & (B.kk == k)]
    if det.empty:
        continue
    st = B[(B.cohort == "stable") & B.hour.between(det.hour.min(), det.hour.max())]
    d = pd.concat([det, st])
    y = (d.cohort == "det").astype(int).values
    g = d.stay_id.values
    XA, XB = d[BASE].values, d[BASE + FEATS].values
    pa, pb = cv_preds(XA, y, g), cv_preds(XB, y, g)
    aa, ab = roc_auc_score(y, pa), roc_auc_score(y, pb)
    lo, hi = boot_diff(y, pa, pb, g)
    L.append(f"k={k} h before anchor: det rows {int(y.sum())} ({det.stay_id.nunique()} patients), "
             f"stable rows {int((y == 0).sum())}")
    L.append(f"   AUC A (NEWS+hour+tier) {aa:.3f}   AUC B (+architecture) {ab:.3f}   "
             f"gain {ab - aa:+.3f}  CI {lo:+.3f} to {hi:+.3f}")
    if k == 2:
        m = LogisticRegression(C=0.5, class_weight="balanced", max_iter=3000).fit(XB, y)
        coefs = pd.Series(m.coef_[0][len(BASE):], index=FEATS).sort_values()
        L.append("   k=2 full-fit coefficients (standardised; + = higher in deteriorating):")
        for f, c in coefs.items():
            L.append(f"      {f:15s} {c:+.3f}")
L.append("")
text = "\n".join(L)
print(text)
open("COMBINED_RESULTS.txt", "w").write(text + "\n")
