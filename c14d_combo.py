import pandas as pd, numpy as np
src = open("c14b_budget.py").read(); exec(src.split("A = L[L.who")[0])
A = L[L.who == "Ajay"]; K = L[L.who == "Kranthi"]; Su = L[L.who == "Sundar"]
nK, nS = K.icustay_id.nunique(), Su.icustay_id.nunique(); tipK = K.groupby("icustay_id").tip.first()
def state(D, tr, tn, prev=False):
    r = D["p_road3" if prev else "road3"].values; n = D["p_news3" if prev else "news3"].values
    return (np.nan_to_num(r, nan=-np.inf) >= tr) | (np.nan_to_num(n, nan=-np.inf) >= tn)
def cost(tr, tn):
    return np.sum(state(A, tr, tn) & ~state(A, tr, tn, True)) / days["Ajay"]
def report(tr, tn, lab):
    sK = state(K, tr, tn); hit = K[sK].groupby("icustay_id").hour.min()
    rF = K[np.nan_to_num(K.road3.values, nan=-np.inf) >= tr].groupby("icustay_id").hour.min().reindex(hit.index)
    nF = K[np.nan_to_num(K.news3.values, nan=-np.inf) >= tn].groupby("icustay_id").hour.min().reindex(hit.index)
    bol = fb.reindex(hit.index); before = ((hit < bol) | bol.isna()).mean() if len(hit) else np.nan
    first = pd.Series(np.where(rF == nF, "both", np.where(rF.fillna(1e9) < nF.fillna(1e9), "road", "NEWS")), index=hit.index)
    sh = Su[state(Su, tr, tn)].icustay_id.nunique() / nS
    print(f"  {lab:28s} cost {cost(tr, tn):.2f}  Kranthi warned {len(hit) / nK:.2f} ({len(hit)}/{nK})  "
          f"lead {(tipK[hit.index] - hit).median():4.1f} h  before 1st bolus {before:.2f}  Sundar {sh:.2f}  first: "
          + ", ".join(f"{k} {v:.2f}" for k, v in first.value_counts(normalize=True).items()))
def single(col, b):
    cand = np.unique(np.nanquantile(A[col].values, np.linspace(0.5, 0.9999, 300)))
    for t in cand:
        tr, tn = (t, np.inf) if col == "road3" else (np.inf, t)
        if cost(tr, tn) <= b: return t
    return np.inf
cr = np.unique(np.nanquantile(A.road3.values, np.linspace(0.5, 0.9999, 80)))
cn = np.unique(np.nanquantile(A.news3.values, np.linspace(0.5, 0.9999, 60)))
print(f"Kranthis {nK}, Sundars {nS}, Ajay-days {days['Ajay']:.0f}\n")
for b in (0.2, 0.44, 1.0, 1.97):
    print(f"==== Budget {b} episodes per Ajay-day ====")
    tr1, tn1 = single("road3", b), single("news3", b)
    report(tr1, np.inf, "road3 alone")
    report(np.inf, tn1, "NEWS-lite alone")
    trh, tnh = single("road3", b / 2), single("news3", b / 2)
    report(trh, tnh, "OR, split budget (primary)")
    best = (-1, None, None)
    for tr in cr:
        for tn in cn:
            if cost(tr, tn) <= b:
                n = K[state(K, tr, tn)].icustay_id.nunique()
                if n > best[0]: best = (n, tr, tn)
    if best[1] is not None: report(best[1], best[2], "OR, best pair (optimistic)")
    print()
