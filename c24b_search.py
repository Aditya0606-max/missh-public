import pandas as pd, numpy as np
src = open("c24_lines.py").read(); exec(src.split("\nbest = None")[0])
g = L.groupby("icustay_id"); Aj = L[L.who == "Ajay"]
rm, r95 = np.nanmedian(Aj.rr3), np.nanquantile(Aj.rr3, 0.95); sm, s5 = np.nanmedian(Aj.spo23), np.nanquantile(Aj.spo23, 0.05)
L["bpos"] = pd.concat([(L.rr3 - rm) / (r95 - rm), (sm - L.spo23) / (sm - s5)], axis=1).mean(axis=1)
for c in ["lead3", "negsf", "rr3", "bpos"]: L[c + "_l3"] = g[c].shift(3)
nzl = lambda v: np.nan_to_num(np.asarray(v, float), nan=-np.inf)
gate = lambda D, c: nzl(D[c]) >= nzl(D[c + "_l3"])
A = L[L.who == "Ajay"]
def thr_gen(col, b, m):
    v = A[col].values[m(A)]; v = v[~np.isnan(v)]
    if len(v) == 0 or b <= 0: return np.inf
    for c in np.unique(np.quantile(v, np.linspace(0.5, 0.9999, 80))):
        if acost(lambda D, c=c: (nzl(D[col]) >= c) & m(D)) <= b: return c
    return np.inf
def masks(eff, gt):
    all_ = lambda D: np.ones(len(D), bool)
    mP = (lambda D: gate(D, "lead3")) if gt else all_
    mS = (lambda D: hasF(D) & gate(D, "negsf")) if gt else hasF
    mE = (lambda D: noF(D) & gate(D, eff)) if gt else noF
    return mP, mS, mE
def build(p, eff, gt, k):
    mP, mS, mE = masks(eff, gt)
    tp, ts, te = thr_gen("lead3", p * k, mP), thr_gen("negsf", (1 - p) * 0.6 * k, mS), thr_gen(eff, (1 - p) * 0.4 * k, mE)
    return lambda D: ((nzl(D.lead3) >= tp) & mP(D)) | ((nzl(D.negsf) >= ts) & mS(D)) | ((nzl(D[eff]) >= te) & mE(D))
def score(f):
    out, tot = {}, 0
    for w in ["Kranthi", "Sundar", "mixed"]:
        D = L[L.who == w]; tip = D.groupby("icustay_id").tip_c.first()
        h = D[f(D) & (D.hour.values < D.tip_c.values)].groupby("icustay_id").hour.min().reindex(tip.index)
        ok = h.notna() & (h < tip); out[w] = ok.mean(); tot += ok.sum()
    return out, tot
res = []
for eff, elab in [("rr3", "A: RR"), ("bpos", "B: RR+SpO2")]:
    for gt in (False, True):
        for p in (0.4, 0.5, 0.6, 0.7, 0.8):
            best = None
            for k in np.arange(1.0, 2.01, 0.1):
                f = build(p, eff, gt, k)
                if acost(f) <= 1.0: best = (f, k)
                else: break
            if best is None: print(f"  {elab} gate {'on ' if gt else 'off'} p {p}: could not fit"); continue
            o, tot = score(best[0]); c = acost(best[0])
            res.append((tot, elab, gt, p, best[1], o, c))
            print(f"  {elab:11s} gate {'on ' if gt else 'off'} pressure {p:.1f} (x{best[1]:.1f}) cost {c:.2f} | Kranthi {o['Kranthi']:.2f} "
                  f"Sundar {o['Sundar']:.2f} mixed {o['mixed']:.2f} | TOTAL {tot}")
tN = thr_gen("news3", 1.0, lambda D: np.ones(len(D), bool)); oN, totN = score(lambda D: nzl(D.news3) >= tN)
print(f"\n  NEWS-lite 3-h >= {tN:.2f} cost {acost(lambda D: nzl(D.news3) >= tN):.2f} | Kranthi {oN['Kranthi']:.2f} Sundar {oN['Sundar']:.2f} "
      f"mixed {oN['mixed']:.2f} | TOTAL {totN}")
b = max(res, key=lambda r: r[0])
verdict = "CLAIM HOLDS -> freeze" if (b[0] > totN and b[5]["Kranthi"] >= oN["Kranthi"]) else "CLAIM FAILS -> rewrite primary claim before signing"
print(f"\nBEST: {b[1]}, gate {'on' if b[2] else 'off'}, pressure {b[3]:.1f} (x{b[4]:.1f}): TOTAL {b[0]}, Kranthi {b[5]['Kranthi']:.2f} | {verdict}")
