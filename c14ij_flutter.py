import pandas as pd, numpy as np
src = open("c14b_budget.py").read(); exec(src.split("A = L[L.who")[0])
def eps(D, col, t):
    x = np.nan_to_num(D[col].values, nan=-np.inf); p = np.nan_to_num(D["p_" + col].values, nan=-np.inf)
    return np.sum((x >= t) & (p < t))
A = L[L.who == "Ajay"]; cand = np.unique(np.nanquantile(A.road3.values, np.linspace(0.5, 0.9999, 300)))
tr = next(t for t in cand if eps(A, "road3", t) / days["Ajay"] <= 1.0)
L["amb"] = L.road3 >= tr
L["last_amb"] = L.hour.where(L.amb).groupby(L.icustay_id).ffill()
L["qdur"] = np.where(L.last_amb.isna(), np.nan, L.hour - L.last_amb)
L["event"] = (L.who != "Ajay") & (L.tip - L.hour > 0) & (L.tip - L.hour <= 3)
Q = L[L.road3.notna() & ~L.amb].copy()
Q["band"] = pd.cut(Q.qdur, [-1, 2, 5, 11, 999], labels=["0-2 h since amber", "3-5 h", "6-11 h", "12+ h"]).astype(str)
Q.loc[Q.qdur.isna(), "band"] = "never amber"
print(f"==== C14i residual risk, all routes (amber line {tr:.2f}) ====")
print(f"  Quiet on road: {Q.event.mean() * 1000:.1f} escalations within 3 h per 1,000 quiet hours (quiet hours {len(Q)})")
print("  Of those escalations, by route: " + ", ".join(f"{w} {v:.2f}" for w, v in Q[Q.event].who.value_counts(normalize=True).items()))
print("  By time since last amber:\n" + Q.groupby("band").event.agg(hours="size", per_1000=lambda s: round(s.mean() * 1000, 1)).to_string())
Nq = L[L.news.notna() & (L.news < 5)]; Bq = Q[Q.news.notna() & (Q.news < 5)]
print(f"  Quiet on NEWS-lite (< 5): {Nq.event.mean() * 1000:.1f} per 1,000 | quiet on both: {Bq.event.mean() * 1000:.1f} per 1,000")
print("  Quiet-on-both escalations by route: " + ", ".join(f"{w} {v:.2f}" for w, v in Bq[Bq.event].who.value_counts(normalize=True).items()), "\n")
g = L.groupby("icustay_id").road
L["r1"], L["r2"], L["r3"] = g.shift(1), g.shift(2), g.shift(3)
L["climb"] = L.road - L.r3; L["steady"] = (L.road > L.r1) & (L.r1 > L.r2) & (L.r2 > L.r3)
A = L[L.who == "Ajay"]
def rule(D, C): return D.steady.values & (np.nan_to_num(D.climb.values, nan=-np.inf) >= C) & (np.nan_to_num(D.road3.values, nan=np.inf) < tr)
Cc = np.unique(np.nanquantile(A.climb.values, np.linspace(0.5, 0.9999, 300)))
C = next((c for c in Cc if rule(A, c).sum() / days["Ajay"] <= 0.2), np.inf)
print(f"==== C14j steady climb (3 h rising, climb >= {C:.2f}, below amber; Ajay {rule(A, C).sum() / days['Ajay']:.2f} h/day) ====")
for w in ["Kranthi", "Sundar", "mixed"]:
    D = L[L.who == w]; tip = D.groupby("icustay_id").tip.first()
    hit = D[rule(D, C)].groupby("icustay_id").hour.min().reindex(tip.index); ok = hit.notna() & (hit < tip)
    amb = D[D.amb].groupby("icustay_id").hour.min().reindex(tip.index); okA = amb.notna() & (amb < tip)
    print(f"  {w:8s} climb caught {ok.mean():.2f} (lead {(tip - hit)[ok].median():.1f} h) | amber {okA.mean():.2f} | amber OR climb {(ok | okA).mean():.2f}")
T = pd.read_csv("c14g_kranthi.csv", index_col=0); K = L[L.who == "Kranthi"]
hit = K[rule(K, C)].groupby("icustay_id").hour.min().reindex(T.index); ok = hit.notna() & (hit < T.tip)
b = T[ok & T.amb.notna()]; d = (b.amb - hit[b.index])
print(f"  Kranthi: climb before amber {(d > 0).mean():.2f} (median {d[d > 0].median():.1f} h earlier); sudden slippers caught {ok[T.slip].sum()}/{T.slip.sum()}")
