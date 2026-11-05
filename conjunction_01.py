# conjunction_01.py — E7: how often do stable vs deteriorating patients meet ALL conditions?
import numpy as np
import pandas as pd

p1 = pd.read_csv("../missh_data/measures_p1.csv", low_memory=False)
p2 = pd.read_csv("../missh_data/measures_p2.csv", low_memory=False)
p3 = pd.read_csv("../missh_data/measures_p3.csv", low_memory=False)
for p in (p1, p2, p3):
    p["kk"] = p.k.fillna(-1)
K = ["stay_id", "cohort", "kk", "hour"]
B = (p2[K + ["news", "consist", "since_ret"]]
     .merge(p3[K + ["share_defend"]], on=K, how="left")
     .merge(p1[K + ["Dw_main"]], on=K, how="left"))
ST = B[B.cohort == "stable"]
q95 = ST.groupby("hour").Dw_main.quantile(0.95)
B["line"] = B.hour.map(q95)
B["C1"] = B.Dw_main > B.line
B["C2"] = B.consist >= 0.75
B["C3"] = B.share_defend >= 0.5
B["C4"] = B.since_ret >= 3
B["ALL"] = B.C1 & B.C2 & B.C3 & B.C4
B["low_news"] = B.news < 5
ST = B[B.cohort == "stable"]; DT = B[B.cohort == "det"]

L = ["CONJUNCTION — E7 (calibration). Shares; stable per hour unless noted", ""]
L.append("Stable:")
for c in ["C1", "C2", "C3", "C4", "ALL"]:
    L.append(f"   {c:4s} per hour {ST[c].mean():.4f}   patients ever {ST.groupby('stay_id')[c].any().mean():.3f}")
L.append(f"   ALL with NEWS<5: per hour {(ST.ALL & ST.low_news).mean():.4f}   "
         f"patients ever {(ST.ALL & ST.low_news).groupby(ST.stay_id).any().mean():.3f}")
for k in (1, 2, 4):
    d = DT[DT.kk == k]
    L.append(f"\nDeteriorating, {k} h before anchor (n={len(d)}):")
    for c in ["C1", "C2", "C3", "C4", "ALL"]:
        L.append(f"   {c:4s} {d[c].mean():.4f}")
    L.append(f"   ALL with NEWS<5: {(d.ALL & d.low_news).mean():.4f}")
    for a, b in [("C1", "C2"), ("C1", "C3"), ("C2", "C3"), ("C1", "C4")]:
        L.append(f"   {a}&{b}: det {(d[a] & d[b]).mean():.4f}  stable {(ST[a] & ST[b]).mean():.4f}")
text = "\n".join(L); print(text); open("CONJUNCTION.txt", "w").write(text + "\n")
