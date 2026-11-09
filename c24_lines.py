import pandas as pd, numpy as np
src = open("c16i_fallback.py").read(); exec(src.split('\nreport("(1) frozen')[0])
rng = np.random.default_rng(24)
cur = L.noF.mean(); p = max(0.0, (0.56 - cur) / (1 - cur))
drop = (~L.noF.values) & (rng.random(len(L)) < p)
L.loc[drop, "noF"] = True; L.loc[drop, "negsf"] = np.nan
A = L[L.who == "Ajay"]
print(f"No-FiO2 share of hours: before {cur:.2f}, after thinning {L.noF.mean():.2f} (target 0.56)\n")
best = None
for k in np.arange(1.0, 2.51, 0.1):
    f, pr = fb_setup(0.4, 0.36, 0.24, k)
    if acost(f) <= 1.0: best = (f, pr, k)
    else: break
report(f"FALLBACK for eICU (x{best[2]:.1f})", best[0], best[1])
tN = thr("news3", 1.0)
report(f"NEWS-lite 3-h >= {tN:.2f} (sanity)", lambda D: nz(D.news3) >= tN, (np.inf, np.inf, np.inf, np.inf))
tp, ts, r, _ = best[1]
print(f"\nFROZEN FOR eICU: pressure leading channel 3-h >= {tp:.3f} | S/F <= {-ts:.1f} (hours with oxygen recorded) "
      f"| RR 3-h >= {r:.2f} (hours without) | NEWS-lite 3-h comparator line on MIMIC-III {tN:.2f}")
