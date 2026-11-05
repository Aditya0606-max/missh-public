# rank_01.py — E11 ranking rehearsal with frozen pieces only (calibration).
import json
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

rng = np.random.default_rng(2026)
S = pd.read_csv("../missh_data/series_dw.csv")
news = pd.read_csv("../missh_data/news_hourly_cal.csv").set_index(["stay_id", "hour_idx"]).news
FM = json.load(open("FLAG_FROZEN.json")); FS = json.load(open("FLAG_SENS_FROZEN.json"))
LM = {int(h): v for h, v in FM["lines"].items()}; LS = {int(h): v for h, v in FS["lines"].items()}

def active(g, lines, p):
    c, out = 0, []
    for _, r in g.iterrows():
        L = lines.get(int(r.hour), np.nan)
        if np.isfinite(r.dw) and np.isfinite(L):
            c = c + 1 if r.dw > L else max(0, c - 1)
        out.append(c >= p)
    return out

rows = []
for sid, g in S.groupby("stay_id"):
    g = g.sort_values("hour")
    am, as_ = active(g, LM, FM["p"]), active(g, LS, FS["p"])
    for (_, r), m, s in zip(g.iterrows(), am, as_):
        nw = news.get((sid, int(r.hour)), np.nan)
        if np.isfinite(nw):
            rows.append((sid, r.cohort, int(r.hour), r.anchor, nw, m, s))
W = pd.DataFrame(rows, columns=["sid", "cohort", "hour", "anchor", "news", "flag_main", "flag_sens"])
W["to_anchor"] = W.anchor - (W.hour + 1)

def auc_sets(d, cols):
    return {c: roc_auc_score(d.y, d[c]) for c in cols}

def boot(d, col, base, n=300):
    ids = d.sid.unique(); idx = {i: np.where(d.sid.values == i)[0] for i in ids}; out = []
    for _ in range(n):
        sel = np.concatenate([idx[i] for i in rng.choice(ids, len(ids))])
        x = d.iloc[sel]
        if x.y.nunique() < 2:
            continue
        out.append(roc_auc_score(x.y, x[col]) - roc_auc_score(x.y, x[base]))
    return np.percentile(out, [2.5, 97.5])

L = ["RANK_REHEARSAL — E11 (calibration, frozen pieces)", ""]
for H in (2, 4):
    d = W[(W.cohort == "stable") | ((W.cohort == "deteriorating") & (W.to_anchor <= H) & (W.to_anchor >= 0))].copy()
    d["y"] = (d.cohort == "deteriorating").astype(int)
    d["s_news"] = d.news
    d["s_main"] = d.news + 3 * d.flag_main
    d["s_sens"] = d.news + 3 * d.flag_sens
    a = auc_sets(d, ["s_news", "s_main", "s_sens"])
    top = d.s_news.quantile(0.9)
    L.append(f"Positive = anchor within {H} h: positive hours {int(d.y.sum())} ({d[d.y==1].sid.nunique()} pts), "
             f"stable hours {int((d.y==0).sum())}")
    for c, name in (("s_news", "NEWS alone"), ("s_main", "NEWS + main alarm"), ("s_sens", "NEWS + sensitivity alarm")):
        thr = d[c].quantile(0.9)
        topshare = d[d[c] >= thr].y.mean()
        line = f"   {name:26s} AUC {a[c]:.3f}   positives in top 10% {topshare:.3f}"
        if c != "s_news":
            lo, hi = boot(d, c, "s_news")
            line += f"   gain {a[c] - a['s_news']:+.3f} ({lo:+.3f} to {hi:+.3f})"
        L.append(line)
    L.append(f"   alarm active, main: det {d[d.y==1].flag_main.mean():.3f} stable {d[d.y==0].flag_main.mean():.3f}; "
             f"sens: det {d[d.y==1].flag_sens.mean():.3f} stable {d[d.y==0].flag_sens.mean():.3f}")
    L.append("")

# Combined model, frozen (A16), applied unchanged
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
L.append("Combined model (frozen, applied unchanged; in-sample on the 20%):")
for k, m in F["models"].items():
    h0, h1 = m["stable_hour_range"]
    d = pd.concat([B[(B.cohort == "det") & (B.kk == int(k))],
                   B[(B.cohort == "stable") & B.hour.between(h0, h1)]])
    y = (d.cohort == "det").astype(int).values
    sc = {nm: d[m[nm]["columns"]].values @ np.array(m[nm]["coef"]) + m[nm]["intercept"] for nm in ("A", "B")}
    aa, ab = roc_auc_score(y, sc["A"]), roc_auc_score(y, sc["B"])
    L.append(f"   k={k}: AUC A {aa:.3f}  AUC B {ab:.3f}  gain {ab - aa:+.3f}")
text = "\n".join(L); print(text); open("RANK_REHEARSAL.txt", "w").write(text + "\n")
