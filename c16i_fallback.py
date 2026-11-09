import pandas as pd, numpy as np
src = open("c16g_effort.py").read(); exec(src.split('report("(1) frozen')[0])
def thr_mask(col, b, mask):
    cand = np.unique(np.nanquantile(A[col].values[mask(A)], np.linspace(0.5, 0.9999, 150)))
    return next((c for c in cand if acost(lambda D, c=c: (nz(D[col]) >= c) & mask(D)) <= b), np.inf)
hasF = lambda D: ~D.noF.values; noF = lambda D: D.noF.values
def fb_setup(sp, sf_b, ef_b, k):
    tp = thr("lead3", sp * k); ts = thr_mask("negsf", sf_b * k, hasF); r = thr_mask("rr3", ef_b * k, noF)
    f = lambda D: (nz(D.lead3) >= tp) | ((nz(D.negsf) >= ts) & hasF(D)) | ((nz(D.rr3) >= r) & noF(D))
    return f, (tp, ts, r, np.inf)
report("(1) frozen lead3 + S/F", lambda D: (nz(D.lead3) >= 1.5) | (nz(D.negsf) >= -247.5), (1.5, -247.5, np.inf, np.inf))
for lab, s_sf in [("S/F 0.8 / effort 0.2", 0.8), ("S/F 0.6 / effort 0.4", 0.6)]:
    best = None
    for k in np.arange(1.0, 2.01, 0.1):
        f, p = fb_setup(0.4, 0.6 * s_sf, 0.6 * (1 - s_sf), k)
        if acost(f) <= 1.0: best = (f, p, k)
        else: break
    if best: report(f"fallback, {lab} (x{best[2]:.1f})", best[0], best[1])
    else: print(f"  {lab}: could not fit budget")
