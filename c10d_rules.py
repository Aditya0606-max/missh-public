# C10d: headroom x direction x witness, hour by hour before tip. Descriptive.
import pandas as pd, numpy as np
X = pd.read_csv("c10_shapes.csv")[["icustay_id", "who", "shape"]]
G = pd.read_csv("c13_groups.csv")[["icustay_id", "tip"]]
H = pd.read_csv("c13d_hourly.csv").merge(G, on="icustay_id").merge(X, on="icustay_id")
H["si"] = np.where(H.hr.between(20, 250) & H.sbp.between(40, 260), H.hr / H.sbp, np.nan)
H["hb"] = (np.ceil(H.tip) - 1 - H.hour).astype(int)
H = H[H.hb.between(0, 14)].sort_values(["icustay_id", "hour"])
E = H[["icustay_id", "hb", "si", "mbp", "hr"]].copy(); E["hb"] = E.hb - 3     # values from 3 h earlier
H = H.merge(E.rename(columns={"si": "si3", "mbp": "map3", "hr": "hr3"}), on=["icustay_id", "hb"], how="left")
H = H[H.hb.between(0, 11)]
H["A"] = np.where(H.si.notna() & H.mbp.notna(), (H.si >= 1) & (H.mbp <= 65), np.nan)
okC = H[["mbp", "map3"]].notna().all(axis=1) & (H[["si", "si3"]].notna().all(axis=1) | H[["hr", "hr3"]].notna().all(axis=1))
H["C"] = np.where(okC, (H.map3 - H.mbp >= 5) & ((H.si - H.si3 >= 0.1) | (H.hr3 - H.hr >= 5)), np.nan)
H["D"] = np.where(H.C.notna(), ((H.si >= 0.9) | (H.mbp <= 70)) & (H.C == 1), np.nan)
H["E"] = np.where(H.A.notna() & H.hr.notna() & H.hr3.notna(), (H.A == 1) & (H.hr3 - H.hr >= 5), np.nan)
H["F"] = np.where(H.A.notna(), (H.A == 1) | (H.E == 1), np.nan)
H["grp"] = np.where(H.who == "Kranthi", "Kranthi " + H["shape"], np.where(H.who == "Ajay", "Ajay", "other"))
H = H[H.grp != "other"]
pd.set_option("display.width", 220)
labels = {"A": "SI>=1 and MAP<=65", "D": "near edge AND moving toward it",
          "E": "A AND heart fading (HR -5 over 3 h)", "F": "A OR E"}
for r in ["A", "D", "E", "F"]:
    T = H.groupby(["hb", "grp"])[r].mean().unstack().sort_index(ascending=False).round(2)
    T.index.name = "h before tip"
    print(f"\n==== Rule {r} ({labels[r]}): share firing per hour ====\n{T.to_string()}")
nK = X[X.who == "Kranthi"].icustay_id.nunique(); nA = X[X.who == "Ajay"].icustay_id.nunique()
print(f"\n==== All Kranthis (n={nK}) vs Ajays (n={nA}) ====")
for hb in (8, 4, 2):
    S = H[H.hb == hb]
    for r in ["A", "D", "E", "F"]:
        k = S[S.who == "Kranthi"][r].mean(); a = S[S.who == "Ajay"][r].mean()
        prec = nK * k / (nK * k + nA * a) if (k + a) > 0 else np.nan
        print(f"  {hb} h before, rule {r}: Kranthi caught {k:.2f}, Ajay false {a:.3f}, precision {prec:.2f}")
