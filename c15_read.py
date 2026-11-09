import pandas as pd, numpy as np
S = pd.read_csv("c15_samples.csv"); L = pd.read_csv("c15_log.csv")
X = pd.read_csv("c10_shapes.csv")[["icustay_id", "shape"]]
S = S.merge(X, on="icustay_id", how="left")
S["hb"] = (S.min_before_tip // 60).astype(int)
S["strict"] = (~S.irregular) & (S.n_clean >= 0.9 * S.hr_ecg)
def auc(a, b):
    a, b = np.asarray(pd.Series(a).dropna(), float), np.asarray(pd.Series(b).dropna(), float)
    if len(a) == 0 or len(b) == 0: return np.nan
    return (a[:, None] > b[None, :]).mean() + 0.5 * (a[:, None] == b[None, :]).mean()
print("Patients with ECG samples:", S.groupby("who").icustay_id.nunique().to_dict())
print("Log reasons:", L.groupby(["who", "reason"]).size().to_dict() if len(L) else "none", "\n")
P0 = S.groupby(["icustay_id", "who"]).irregular.mean().reset_index()
print("==== Q0 irregular rhythm: share of each patient's strips ====")
print(P0.groupby("who").irregular.describe()[["count", "25%", "50%", "75%"]].round(2).to_string())
print(f"  AUC Kranthi vs Ajay (more irregular = worse): {auc(P0[P0.who == 'Kranthi'].irregular, P0[P0.who == 'Ajay'].irregular):.2f}\n")
def hourly(D):
    return D.groupby(["icustay_id", "who", "hb"])[["hr_ecg", "rmssd", "rmssd_norm"]].median().reset_index().merge(X, on="icustay_id", how="left")
for label, D in [("regular strips", S[~S.irregular]), ("cleanest strips only", S[S.strict])]:
    Hh = hourly(D)
    print(f"==== Q1 rigidity ({label}): AUC vs Ajay, lower flexibility = worse ====")
    for c in (8, 4, 2):
        W = Hh[Hh.hb.between(c, c + 2)].groupby(["icustay_id", "who"])[["rmssd", "rmssd_norm"]].median().reset_index().merge(X, on="icustay_id", how="left")
        k, a, m = W[W.who == "Kranthi"], W[W.who == "Ajay"], W[W.who == "mixed"]
        print(f"  {c} h: Kranthi n{len(k)} vs Ajay n{len(a)}  corrected {auc(-k.rmssd_norm, -a.rmssd_norm):.2f}  raw {auc(-k.rmssd, -a.rmssd):.2f}"
              f"  | median corrected K {k.rmssd_norm.median():.1f} A {a.rmssd_norm.median():.1f}  | mixed {auc(-m.rmssd_norm, -a.rmssd_norm):.2f}")
        print("        by shape: " + "  ".join(f"{sh} n{len(g)} {auc(-g.rmssd_norm, -a.rmssd_norm):.2f}" for sh, g in k.groupby("shape")))
    print()
Hh = hourly(S[~S.irregular])
prev = Hh[["icustay_id", "hb", "hr_ecg", "rmssd_norm"]].rename(columns={"hr_ecg": "hr_prev", "rmssd_norm": "flex_prev"}).copy()
prev["hb"] = prev.hb - 1
D = Hh.merge(prev, on=["icustay_id", "hb"], how="inner")
D = D[(D.hb <= 3) & (D.hr_prev - D.hr_ecg >= 5)].copy()
D["dflex"] = D.rmssd_norm - D.flex_prev
P = D.groupby(["icustay_id", "who", "shape"], dropna=False).dflex.mean().reset_index()
print("==== Q2 rest or quit: last 4 h, HR fell >= 5 bpm; change in corrected flexibility ====")
print("  pairs:", D.groupby("who").size().to_dict(), "| patients:", P.who.value_counts().to_dict())
for w in ["Ajay", "Kranthi", "mixed"]:
    g = P[P.who == w]
    if len(g): print(f"  {w:8s} median change {g.dflex.median():+.2f}  share with flexibility rising {(g.dflex > 0).mean():.2f}")
k, a = P[P.who == "Kranthi"], P[P.who == "Ajay"]
print(f"  AUC Kranthi vs Ajay (flexibility NOT rising = worse): {auc(-k.dflex, -a.dflex):.2f}")
print("  by shape: " + "  ".join(f"{sh} n{len(g)} {auc(-g.dflex, -a.dflex):.2f}" for sh, g in k.groupby("shape")))
