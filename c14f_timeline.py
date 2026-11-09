import pandas as pd, numpy as np
src = open("c14b_budget.py").read(); exec(src.split("A = L[L.who")[0])
A = L[L.who == "Ajay"]; K = L[L.who == "Kranthi"]
def eps(D, col, t):
    x = np.nan_to_num(D[col].values, nan=-np.inf); p = np.nan_to_num(D["p_" + col].values, nan=-np.inf)
    return np.sum((x >= t) & (p < t))
cand = np.unique(np.nanquantile(A.road3.values, np.linspace(0.5, 0.9999, 300)))
tr = next(t for t in cand if eps(A, "road3", t) / days["Ajay"] <= 1.0)
print(f"Road line {tr:.2f} | Ajay episodes/day: road {eps(A, 'road3', tr) / days['Ajay']:.2f}, "
      f"NEWS>=5 {eps(A, 'news', 5) / days['Ajay']:.2f}, NEWS>=7 {eps(A, 'news', 7) / days['Ajay']:.2f}\n")
def firsthour(mask): return K[mask].groupby("icustay_id").hour.min()
tip = K.groupby("icustay_id").tip.first()
T = pd.DataFrame({"tip": tip, "road": firsthour(K.road3 >= tr), "n5": firsthour(K.news >= 5), "n7": firsthour(K.news >= 7)})
n = len(T)
def q(s): s = s.dropna(); return f"median {s.median():4.1f} h (IQR {s.quantile(.25):.1f}-{s.quantile(.75):.1f}), n {len(s)}"
print(f"==== Kranthis: {n} ====")
for c, lab in [("road", "road amber"), ("n5", "NEWS-lite >= 5"), ("n7", "NEWS-lite >= 7")]:
    print(f"  {lab:15s} fired {T[c].notna().mean():.2f}  lead before tip: {q(T.tip - T[c])}")
b = T.dropna(subset=["road", "n5"])
print(f"\n  Road vs NEWS>=5 (both fired, n {len(b)}): road earlier {(b.road < b.n5).mean():.2f}, same hour {(b.road == b.n5).mean():.2f}, NEWS earlier {(b.road > b.n5).mean():.2f}")
print(f"  Hours from road amber to NEWS>=5: {q(b.n5 - b.road)}")
b7 = T.dropna(subset=["road", "n7"]); print(f"  Hours from road amber to NEWS>=7: {q(b7.n7 - b7.road)}")
print(f"  Hours from NEWS>=5 to pressor: {q(T.tip - T.n5)}")
print(f"  Hours from NEWS>=7 to pressor: {q(T.tip - T.n7)}")
print(f"\n  Seen by: road only {(T.road.notna() & T.n5.isna()).sum()}, NEWS>=5 only {(T.road.isna() & T.n5.notna()).sum()}, "
      f"both {(T.road.notna() & T.n5.notna()).sum()}, neither {(T.road.isna() & T.n5.isna()).sum()}")
ro = T[T.road.notna() & T.n5.isna()]; print(f"  Road-only Kranthis, lead before tip: {q(ro.tip - ro.road)}")
pos = K.merge(T.n5.dropna().rename("h5"), left_on="icustay_id", right_index=True)
pos = pos[pos.hour == pos.h5].road3
print(f"  Road position when NEWS first reaches 5: median {pos.median():.2f} (line {tr:.2f}); share already past road line {(pos >= tr).mean():.2f}")
