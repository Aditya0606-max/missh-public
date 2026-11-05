# freeze_combined.py — A16: fit models A and B on the full 20% and freeze them.
import json
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

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
B = (p2[KEYS + ["tier", "news"] + F2].merge(p3[KEYS + F3], on=KEYS, how="left")
     .merge(p1[KEYS + F1], on=KEYS, how="left"))
ST = B[B.cohort == "stable"]
med = ST[FEATS].median()
mu = ST[FEATS].fillna(med).mean()
sd = ST[FEATS].fillna(med).std().replace(0, 1)
news_med = float(ST.news.median())
B[FEATS] = (B[FEATS].fillna(med) - mu) / sd
B["news"] = B.news.fillna(news_med)
TIERS = sorted(B.tier.dropna().unique())
for t in TIERS:
    B[f"t_{t}"] = (B.tier == t).astype(float)
BASE = ["news", "hour"] + [f"t_{t}" for t in TIERS]

frozen = {"features": FEATS, "base": BASE, "tiers": TIERS,
          "median": med.to_dict(), "mean": mu.to_dict(), "sd": sd.to_dict(),
          "news_median": news_med, "C": 0.5, "class_weight": "balanced", "models": {}}
for k in (1, 2, 4):
    det = B[(B.cohort == "det") & (B.kk == k)]
    hmin, hmax = int(det.hour.min()), int(det.hour.max())
    st = B[(B.cohort == "stable") & B.hour.between(hmin, hmax)]
    d = pd.concat([det, st]); y = (d.cohort == "det").astype(int).values
    entry = {"stable_hour_range": [hmin, hmax]}
    for name, cols in (("A", BASE), ("B", BASE + FEATS)):
        m = LogisticRegression(C=0.5, class_weight="balanced", max_iter=3000).fit(d[cols].values, y)
        entry[name] = {"columns": cols, "coef": m.coef_[0].tolist(), "intercept": float(m.intercept_[0])}
    frozen["models"][str(k)] = entry
json.dump(frozen, open("COMBINED_FROZEN.json", "w"), indent=1)
print("Frozen: models A and B at k = 1, 2, 4 ->", "COMBINED_FROZEN.json")
