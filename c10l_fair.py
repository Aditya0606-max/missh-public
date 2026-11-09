import pandas as pd, numpy as np
src = open("c10i_road.py").read(); exec(src.split('print("Median road position')[0])
exec("\n".join(l for l in src.splitlines() if l.startswith(("low =", "lowA =", "def auc", "    a, b =", "    if len(a)", "    return"))))
def pts(v, cuts):
    if pd.isna(v): return np.nan
    for lo, hi, p in cuts:
        if lo <= v <= hi: return p
    return 0
RRc = [(-1, 8, 3), (9, 11, 1), (12, 20, 0), (21, 24, 2), (25, 999, 3)]; SPc = [(-1, 91, 3), (92, 93, 2), (94, 95, 1), (96, 101, 0)]
SBc = [(-1, 90, 3), (91, 100, 2), (101, 110, 1), (111, 219, 0), (220, 999, 3)]; HRc = [(-1, 40, 3), (41, 50, 1), (51, 90, 0), (91, 110, 1), (111, 130, 2), (131, 999, 3)]
TPc = [(-1, 35.0, 3), (35.01, 36.0, 1), (36.01, 38.0, 0), (38.01, 39.0, 1), (39.01, 99, 2)]
P = pd.DataFrame({"rr": H.rr.map(lambda v: pts(v, RRc)), "sp": H.spo2.map(lambda v: pts(v, SPc)), "sb": H.sbp.map(lambda v: pts(v, SBc)),
                  "hr": H.hr.map(lambda v: pts(v, HRc)), "tp": H.temp.map(lambda v: pts(v, TPc))})
H["news"] = np.where(P.notna().sum(axis=1) >= 3, P.sum(axis=1), np.nan)
H["neg_map"] = -H["map"]; H["neg_pp"] = -H.pp
M = [("road", "road"), ("si", "SI"), ("neg_map", "MAP"), ("neg_pp", "PP"), ("news", "NEWS-lite"), ("A", "rule A")]
for c in (8, 4, 2):
    one = H[H.hb == c]
    three = H[H.hb.between(c, c + 2)].groupby(["icustay_id", "who"])[[m for m, _ in M]].mean().reset_index()
    for lab, S in [("single hour", one), ("3-h mean", three)]:
        k = S[S.who == "Kranthi"]; a = S[S.who == "Ajay"]; al = a[a.icustay_id.isin(lowA)]
        print(f"==== {c} h before tip, {lab} (Kranthi n{len(k)}, Ajay n{len(a)}, low-sitting Ajay n{len(al)}) ====")
        print("  vs all Ajays:         " + "  ".join(f"{n} {auc(k[m], a[m]):.2f}" for m, n in M))
        print("  vs low-sitting Ajays: " + "  ".join(f"{n} {auc(k[m], al[m]):.2f}" for m, n in M))
        best = max((auc(k[m], al[m]), n) for m, n in M[1:5])
        print(f"  best single vs low-sitting: {best[1]} {best[0]:.2f} | road minus best: {auc(k.road, al.road) - best[0]:+.2f}\n")
