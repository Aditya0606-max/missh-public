import pandas as pd, numpy as np
src = open("c24b_search.py").read(); exec(src.split("\nres = []")[0])
best = None
for k in np.arange(1.0, 2.01, 0.1):
    mP, mS, mE = masks("bpos", False)
    tp, ts, te = thr_gen("lead3", 0.7 * k, mP), thr_gen("negsf", 0.3 * 0.6 * k, mS), thr_gen("bpos", 0.3 * 0.4 * k, mE)
    f = lambda D, tp=tp, ts=ts, te=te: (nzl(D.lead3) >= tp) | ((nzl(D.negsf) >= ts) & hasF(D)) | ((nzl(D.bpos) >= te) & noF(D))
    if acost(f) <= 1.0: best = (tp, ts, te, k, acost(f))
    else: break
tp, ts, te, k, c = best
print(f"FROZEN (B, gate off, pressure 0.7, x{k:.1f}, cost {c:.2f}):")
print(f"  pressure leading channel 3-h >= {tp:.3f}")
print(f"  S/F <= {-ts:.1f}  (hours with oxygen recorded)")
print(f"  breathing effort position >= {te:.3f}  (hours without; mean of RR and SpO2 positions)")
print(f"  effort anchors from MIMIC-III Ajays: RR median {rm:.1f}, RR 95th {r95:.1f}; SpO2 median {sm:.1f}, SpO2 5th {s5:.1f}")
