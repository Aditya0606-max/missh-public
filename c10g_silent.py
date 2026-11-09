import pandas as pd, numpy as np
X = pd.read_csv("c10_shapes.csv")[["icustay_id", "who", "shape"]]
G = pd.read_csv("c13_groups.csv")[["icustay_id", "tip"]]
H = pd.read_csv("c13d_hourly.csv").merge(G, on="icustay_id").merge(X, on="icustay_id")
H["si"] = np.where(H.hr.between(20, 250) & H.sbp.between(40, 260), H.hr / H.sbp, np.nan)
H["hb"] = (np.ceil(H.tip) - 1 - H.hour).astype(int)
H = H[H.hb.between(0, 14)]
E = H[["icustay_id", "hb", "mbp", "hr"]].copy(); E["hb"] = E.hb - 3
H = H.merge(E.rename(columns={"mbp": "map3", "hr": "hr3"}), on=["icustay_id", "hb"], how="left")
H = H[H.hb.between(0, 11)]
H["A"] = np.where(H.si.notna() & H.mbp.notna(), (H.si >= 1) & (H.mbp <= 65), np.nan)
okHR = H[["hr", "hr3"]].notna().all(axis=1)
H["E"] = np.where(H.A.notna() & okHR, (H.A == 1) & (H.hr3 - H.hr >= 5), np.nan)
okE2 = H[["mbp", "map3"]].notna().all(axis=1) & okHR
H["E2"] = np.where(okE2, (H.mbp <= 70) & (H.map3 - H.mbp >= 5) & (H.hr3 - H.hr >= 5), np.nan)
H["grp"] = np.where(H.who == "Kranthi", "Kranthi " + H["shape"], np.where(H.who == "Ajay", "Ajay", "other"))
H = H[H.grp != "other"]
pd.set_option("display.width", 220)
T = H.groupby(["hb", "grp"])["E2"].mean().unstack().sort_index(ascending=False).round(2); T.index.name = "h before tip"
print("==== Rule E' share firing per hour ====\n" + T.to_string())
nK = X[X.who == "Kranthi"].icustay_id.nunique(); nA = X[X.who == "Ajay"].icustay_id.nunique()
print(f"\n==== All Kranthis (n={nK}) vs Ajays (n={nA}) ====")
for hb in (8, 4, 2):
    S = H[H.hb == hb]
    for r in ["A", "E", "E2"]:
        k = S[S.who == "Kranthi"][r].mean(); a = S[S.who == "Ajay"][r].mean()
        prec = nK * k / (nK * k + nA * a) if (k + a) > 0 else np.nan
        print(f"  {hb} h before, rule {r:2s}: Kranthi caught {k:.2f}, Ajay false {a:.3f}, precision {prec:.2f}")
    s = S[(S.who == "Kranthi") & (S["shape"] == "silent heart")]
    print(f"     silent heart only: E2 {s.E2.mean():.2f} vs A {s.A.mean():.2f}")
