import pandas as pd, numpy as np
src = open("c14b_budget.py").read(); exec(src.split("A = L[L.who")[0])
Fh = H[["icustay_id", "hour"] + FC].drop_duplicates(["icustay_id", "hour"])
L = L.merge(Fh, on=["icustay_id", "hour"], how="left").sort_values(["icustay_id", "hour"])
g = L.groupby("icustay_id")
L["lead1"] = L[FC].max(axis=1)
L["lead3"] = g.lead1.transform(lambda s: s.rolling(3, min_periods=1).mean())
L["pp1"] = L.f_pp
for c in ["lead1", "lead3", "pp1"] + FC: L["p_" + c] = g[c].shift(1)
A = L[L.who == "Ajay"]
def nz(v): return np.nan_to_num(v, nan=-np.inf)
def cost(col, t): return np.sum((nz(A[col].values) >= t) & (nz(A["p_" + col].values) < t)) / days["Ajay"]
def line(col, b):
    cand = np.unique(np.nanquantile(A[col].values, np.linspace(0.5, 0.9999, 300)))
    return next((c for c in cand if cost(col, c) <= b), np.inf)
def any_state(D, lines, prev=False):
    return np.column_stack([nz(D[("p_" if prev else "") + c].values) >= lines[c] for c in FC]).any(axis=1)
def any_lines(b):
    for q in np.linspace(0.5, 0.9999, 300):
        ln = {c: np.nanquantile(A[c].values, q) for c in FC}
        if np.sum(any_state(A, ln) & ~any_state(A, ln, True)) / days["Ajay"] <= b: return ln, q
    return None, None
T = pd.read_csv("c14g_kranthi.csv", index_col=0)
def report(lab, mask_fn, c):
    out = [f"  {lab:30s} cost {c:.2f}"]
    for w in ["Kranthi", "Sundar"]:
        D = L[L.who == w]; tip = D.groupby("icustay_id").tip.first()
        h = D[mask_fn(D)].groupby("icustay_id").hour.min().reindex(tip.index); ok = h.notna() & (h < tip)
        out.append(f"{w} {ok.mean():.2f} ({(tip - h)[ok].median():.1f} h)")
        if w == "Kranthi":
            s = ok.reindex(T.index)[T.slip]; out.append(f"slippers {int(s.sum())}/{len(s)}")
    print(" | ".join(out))
SC = [("road3", "road, 3-hour (current)"), ("road", "road, 1-hour"), ("lead1", "leading channel, 1-hour"),
      ("lead3", "leading channel, 3-hour"), ("pp1", "pulse pressure alone")]
for b in (0.44, 1.0):
    print(f"==== Budget {b} episodes per Ajay-day ====")
    for col, lab in SC:
        t = line(col, b); report(lab, lambda D, col=col, t=t: nz(D[col].values) >= t, cost(col, t))
    ln, q = any_lines(b)
    if ln is not None:
        c = np.sum(any_state(A, ln) & ~any_state(A, ln, True)) / days["Ajay"]
        report(f"any channel past own line (q {q:.3f})", lambda D: any_state(D, ln), c)
    print()
