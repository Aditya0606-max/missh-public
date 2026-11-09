import pandas as pd, numpy as np
src = open("c14b_budget.py").read(); exec(src.split("A = L[L.who")[0])
L["mp"] = -L.negmap
H2 = H[["icustay_id", "hour", "pp"]]; L = L.merge(H2, on=["icustay_id", "hour"], how="left")
g = L.groupby("icustay_id")
L["si_min3"] = g.si.transform(lambda s: s.shift(1).rolling(3, min_periods=1).min())
L["mp_max3"] = g.mp.transform(lambda s: s.shift(1).rolling(3, min_periods=1).max())
L["pp_max3"] = g.pp.transform(lambda s: s.shift(1).rolling(3, min_periods=1).max())
L["rise"] = L.si - L.si_min3; L["mdrop"] = L.mp_max3 - L.mp; L["pdrop"] = L.pp_max3 - L.pp
A = L[L.who == "Ajay"]; K = L[L.who == "Kranthi"]
def eps(D, col, t):
    x = np.nan_to_num(D[col].values, nan=-np.inf); p = np.nan_to_num(D["p_" + col].values, nan=-np.inf)
    return np.sum((x >= t) & (p < t))
cand = np.unique(np.nanquantile(A.road3.values, np.linspace(0.5, 0.9999, 300)))
tr = next(t for t in cand if eps(A, "road3", t) / days["Ajay"] <= 1.0)
def nz(v, fill=-np.inf): return np.nan_to_num(v, nan=fill)
def rule(D, R, w):
    wit = {"MAP drop": nz(D.mdrop.values) >= 5, "PP narrowing": nz(D.pdrop.values) >= 5,
           "either (primary)": (nz(D.mdrop.values) >= 5) | (nz(D.pdrop.values) >= 5)}[w]
    return (nz(D.rise.values) >= R) & wit & (nz(D.road3.values, np.inf) < tr)
T = pd.read_csv("c14g_kranthi.csv", index_col=0)
Rc = np.unique(np.nanquantile(A.rise.values, np.linspace(0.5, 0.9999, 300)))
print(f"Amber line {tr:.2f}. Rule: SI up >= R vs 3-h low, plus witness, below amber; each priced at Ajay <= 0.2 hours/day\n")
for w in ["MAP drop", "PP narrowing", "either (primary)"]:
    R = next((r for r in Rc if rule(A, r, w).sum() / days["Ajay"] <= 0.2), np.inf)
    hit = K[rule(K, R, w)].groupby("icustay_id").hour.min()
    ok = hit.reindex(T.index).notna() & (hit.reindex(T.index) < T.tip)
    s = ok[T.slip]; lead = (T.tip - hit.reindex(T.index))[ok & T.slip]
    both = T.amb.notna() | ok
    print(f"  {w:17s} R {R:.2f} (Ajay {rule(A, R, w).sum() / days['Ajay']:.2f} h/day) | slippers caught {s.sum()}/{len(s)} ({s.mean():.2f}), "
          f"lead {lead.median():.1f} h | all Kranthis {ok.mean():.2f} | amber OR rise {both.mean():.2f} ({both.sum()}/{len(T)}), "
          f"total cost ~{eps(A, 'road3', tr) / days['Ajay'] + rule(A, R, w).sum() / days['Ajay']:.2f}/day")
