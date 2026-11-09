# C10e v2: low-sitting patients; continuous slide and paying scores in own units. Descriptive.
import pandas as pd, numpy as np
X = pd.read_csv("c10_shapes.csv")[["icustay_id", "who", "shape"]]
G = pd.read_csv("c13_groups.csv")[["icustay_id", "tip"]]
H = pd.read_csv("c13d_hourly.csv").merge(G, on="icustay_id").merge(X, on="icustay_id")
H = H[H.who.isin(["Kranthi", "Ajay"])]
H["si"] = np.where(H.hr.between(20, 250) & H.sbp.between(40, 260), H.hr / H.sbp, np.nan)
H["pp"] = H.sbp - H.dbp
H["hb"] = (np.ceil(H.tip) - 1 - H.hour).astype(int); H = H[H.hb.between(0, 11)]
def auc(a, b):
    a, b = np.asarray(pd.Series(a).dropna(), float), np.asarray(pd.Series(b).dropna(), float)
    if len(a) == 0 or len(b) == 0: return np.nan
    return (a[:, None] > b[None, :]).mean() + 0.5 * (a[:, None] == b[None, :]).mean()
FL = {"mbp": 2, "hr": 2, "rr": 1, "pp": 2, "si": 0.02}
early = H[H.hb.between(8, 11)]
E = early.groupby("icustay_id").agg(who=("who", "first"), shape=("shape", "first"), n_map=("mbp", "count"),
    low=("mbp", "median"), **{f"{c}0": (c, "median") for c in ["hr", "si", "pp", "rr"]},
    **{f"{c}_sd": (c, "std") for c in FL})
for c, f in FL.items(): E[f"{c}_sd"] = E[f"{c}_sd"].fillna(f).clip(lower=f)
E = E[E.n_map >= 3]; L = E[E.low <= 65]
print("==== Sitting low early (median MAP <= 65 in hours 11-8; of those with >= 3 MAP hours) ====")
print(pd.DataFrame({"with_early_MAP": E.who.value_counts(), "sitting_low": L.who.value_counts()})
      .assign(share=lambda d: (d.sitting_low / d.with_early_MAP).round(2)).to_string())
print("Low-sitting Kranthis by shape:", L[L.who == "Kranthi"]["shape"].value_counts().to_dict())
T = H[H.hb.between(0, 7)].merge(L.drop(columns=["who", "shape"]).reset_index(), on="icustay_id")
T["z_hr"] = (T.hr - T.hr0) / T.hr_sd; T["z_si"] = (T.si - T.si0) / T.si_sd
T["z_pp"] = -(T.pp - T.pp0) / T.pp_sd; T["z_rr"] = (T.rr - T.rr0) / T.rr_sd
T["paying"] = T[["z_hr", "z_si", "z_pp", "z_rr"]].mean(axis=1, skipna=True)
T["slide"] = (T.low - T.mbp) / T.mbp_sd
T["neg_map"] = -T.mbp
T["combined"] = T.groupby("hb")[["slide", "paying"]].rank(pct=True).mean(axis=1, skipna=False)
nK, nA = (L.who == "Kranthi").sum(), (L.who == "Ajay").sum()
print(f"\n==== Within low-sitting group (Kranthi n={nK}, Ajay n={nA}): AUC, higher = Kranthi worse ====")
for hb in (4, 2):
    S = T[T.hb == hb]; k, a = S[S.who == "Kranthi"], S[S.who == "Ajay"]
    print(f"  {hb} h before: " + "  ".join(f"{lab} {auc(k[f], a[f]):.2f}" for f, lab in
          [("neg_map", "MAP level"), ("slide", "slide"), ("z_hr", "HR"), ("z_si", "SI"), ("z_pp", "PP narrowing"),
           ("z_rr", "RR"), ("paying", "paying"), ("combined", "combined")]))
line = T[T.who == "Ajay"].groupby("hb").combined.quantile(0.90).rename("line")
T = T.merge(line, left_on="hb", right_index=True); T["above"] = T.combined > T.line
print("\n==== Provisional line = Ajay 90th percentile of combined, per hour ====")
for hb in (4, 2):
    S = T[T.hb == hb]; k = S[S.who == "Kranthi"].above.mean(); a = S[S.who == "Ajay"].above.mean()
    print(f"  {hb} h before: Kranthi caught {k:.2f}, Ajay above {a:.2f}, precision {nK * k / (nK * k + nA * a):.2f}")
ever = T[T.who == "Kranthi"].groupby("icustay_id").above.max()
Kb = L[L.who == "Kranthi"].join(ever.rename("ever"), how="left")
print("\n==== Blind spot: low-sitting Kranthis never above the line in hours 7-0 ====")
print(f"  overall: {(Kb.ever != True).mean():.2f} of {len(Kb)}")
print("  by shape:", Kb.groupby("shape").ever.apply(lambda s: round((s != True).mean(), 2)).to_dict())
