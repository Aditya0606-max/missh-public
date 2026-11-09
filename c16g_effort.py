import pandas as pd, numpy as np
src = open("c16h_vent.py").read(); exec(src.split('print("S/F alarm hours')[0])
L = L.merge(H[["icustay_id", "hour", "hr"]].drop_duplicates(["icustay_id", "hour"]), on=["icustay_id", "hour"], how="left")
L = L.merge(pd.read_csv("c16_hourly.csv", usecols=["icustay_id", "hour", "fio2_src"]), on=["icustay_id", "hour"], how="left")
L = L.sort_values(["icustay_id", "hour"]).reset_index(drop=True); g = L.groupby("icustay_id")
for c in ["rr", "hr", "spo2"]: L[c + "3"] = g[c].transform(lambda s: s.rolling(3, min_periods=1).mean())
L["noF"] = L.fio2_src.fillna("none") == "none"
A = L[L.who == "Ajay"]
def eps(D, s):
    prev = pd.Series(s, index=D.index).groupby(D.icustay_id.values).shift(1).fillna(False).values.astype(bool)
    return np.sum(s & ~prev)
def acost(fn): return eps(A, fn(A)) / days["Ajay"]
def thr(col, b):
    cand = np.unique(np.nanquantile(A[col].values, np.linspace(0.5, 0.9999, 150)))
    return next((c for c in cand if acost(lambda D, c=c: nz(D[col]) >= c) <= b), np.inf)
def eff_line(b, mode):
    for q in np.linspace(0.5, 0.995, 150):
        r = np.nanquantile(A.rr3, q); h = np.nanquantile(A.hr3, q) if mode == "rr_hr" else -np.inf
        f = lambda D, r=r, h=h: (nz(D.rr3) >= r) & (nz(D.hr3) >= h) & ((nz(D.spo23) >= 92) | D.noF.values)
        if acost(f) <= b: return f, r, h
    return (lambda D: np.zeros(len(D), bool)), np.inf, np.inf
def setup(sp, ss, se, k, mode):
    tp = thr("lead3", sp * k); ts = thr("negsf", ss * k) if ss > 0 else np.inf
    fe, r, h = eff_line(se * k, mode)
    return (lambda D: (nz(D.lead3) >= tp) | (nz(D.negsf) >= ts) | fe(D)), (tp, ts, r, h)
def topup(sp, ss, se, mode):
    best = None
    for k in np.arange(1.0, 2.01, 0.1):
        f, p = setup(sp, ss, se, k, mode)
        if acost(f) <= 1.0: best = (f, p, k)
        else: break
    return best
def report(lab, f, p):
    out, tot = [f"  {lab:30s} cost {acost(f):.2f}"], 0
    for w in ["Kranthi", "Sundar", "mixed"]:
        D = L[L.who == w]; tip = D.groupby("icustay_id").tip_c.first(); s = f(D) & (D.hour.values < D.tip_c.values)
        E = D[s]; h = E.groupby("icustay_id").hour.min().reindex(tip.index); ok = h.notna() & (h < tip); tot += ok.sum()
        out.append(f"{w} {ok.mean():.2f} ({(tip - h)[ok].median():.1f} h)")
        if w == "Sundar":
            fh = E.sort_values("hour").groupby("icustay_id").first()
            out.append(f"Sundars first warned with no FiO2 {int(fh.noF.reindex(ok[ok].index).fillna(False).sum())}")
    print(" | ".join(out) + f" | TOTAL {tot}")
    print(f"      lines: lead3 {p[0]:.2f}, S/F <= {-p[1]:.0f}, effort RR >= {p[2]:.1f}" + (f" & HR >= {p[3]:.0f}" if np.isfinite(p[3]) else ""))
report("(1) frozen lead3 + S/F", lambda D: (nz(D.lead3) >= 1.5) | (nz(D.negsf) >= -247.5), (1.5, -247.5, np.inf, np.inf))
for mode, mlab in [("rr", "PRIMARY: RR-led effort (HR not required)"), ("rr_hr", "variant: RR and HR both high")]:
    print(f"\n==== {mlab} ====")
    for lab, sp, ss, se in [("(2) lead3 + S/F + effort", 0.4, 0.3, 0.3), ("(3) lead3 + effort only", 0.4, 0.0, 0.6)]:
        res = topup(sp, ss, se, mode)
        if res: report(lab + f" (x{res[2]:.1f})", res[0], res[1])
        else: print(f"  {lab}: could not fit budget")
