# cosine_traj_01.py — does the cosine toward shock build up before the anchor, or jump?
import numpy as np
import pandas as pd

a = pd.read_csv("../missh_data/measures_p1.csv", low_memory=False)
b = pd.read_csv("../missh_data/measures_p1_k0.csv", low_memory=False)
M = pd.concat([a, b[b.cohort == "det"]], ignore_index=True)
M["cos"] = np.where(M.D_main > 0, M.Dw_main / M.D_main, np.nan)
DT, ST = M[M.cohort == "det"], M[M.cohort == "stable"]

L = ["COSINE_TRAJECTORY — cosine of his arrow (own ruler) toward shock", ""]
L.append(" k  | det n | det median | det mean | det >0.5 | stable median (same hours) | stable >0.5 | det median D")
for k in (6, 4, 2, 1, 0):
    d = DT[DT.k == k].dropna(subset=["cos"])
    s = ST[ST.hour.isin(d.hour.unique())].dropna(subset=["cos"])
    L.append(f" {k}  | {len(d):5d} | {d.cos.median():10.3f} | {d.cos.mean():8.3f} | {(d.cos > 0.5).mean():8.3f} | "
             f"{s.cos.median():26.3f} | {(s.cos > 0.5).mean():11.3f} | {d.D_main.median():.2f}")
L.append("")
W = DT.pivot_table(index="stay_id", columns="k", values="cos")
for ks in [(4, 2, 0), (2, 1, 0), (6, 4, 2, 0)]:
    w = W.dropna(subset=list(ks))
    if len(w):
        means = " -> ".join(f"{w[k].mean():.3f}" for k in ks)
        rising = (np.diff(w[list(ks)].values, axis=1) > 0).all(axis=1).mean()
        L.append(f"Same patients at k={ks}: n={len(w)}  mean cosine {means}  "
                 f"share rising at every step {rising:.3f}")
text = "\n".join(L); print(text); open("COSINE_TRAJECTORY.txt", "w").write(text + "\n")
