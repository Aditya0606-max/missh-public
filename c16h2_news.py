import pandas as pd, numpy as np
src = open("c16h_vent.py").read(); exec(src.split('print("S/F alarm hours')[0])
A = L[L.who == "Ajay"]
def st(D, col, t): return nz(D[col].values) >= t
def cost(col, t):
    s = st(A, col, t); prev = pd.Series(s, index=A.index).groupby(A.icustay_id.values).shift(1).fillna(False).values.astype(bool)
    return np.sum(s & ~prev) / days["Ajay"]
def line1(col, b):
    cand = np.unique(np.nanquantile(A[col].values, np.linspace(0.5, 0.9999, 150)))
    return next((c for c in cand if cost(col, c) <= b), np.inf)
for col, lab in [("news3", "NEWS-lite 3-h"), ("news2_3", "NEWS with O2 3-h")]:
    t = line1(col, 1.0); tot = 0; out = [f"  {lab:18s} line {t:.2f} cost {cost(col, t):.2f}"]
    for w in ["Kranthi", "Sundar", "mixed"]:
        D = L[L.who == w]; tip = D.groupby("icustay_id").tip_c.first()
        E = D[st(D, col, t) & (D.hour < D.tip_c)]
        h = E.groupby("icustay_id").hour.min().reindex(tip.index); ok = h.notna() & (h < tip); tot += ok.sum()
        out.append(f"{w} {ok.mean():.2f} ({(tip - h)[ok].median():.1f} h)")
    print(" | ".join(out) + f" | TOTAL corrected {tot}")
print("  Frozen setup corrected total: 1375 (Kranthi 0.76, Sundar 0.65, mixed 0.36)")
