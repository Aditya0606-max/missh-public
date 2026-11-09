import pandas as pd, numpy as np
X = pd.read_csv("c10_shapes.csv")[["icustay_id", "who", "shape"]]; X = X[X.who.isin(["Kranthi", "Ajay"])]
G = pd.read_csv("c13_groups.csv")[["icustay_id", "tip"]]
H = pd.read_csv("c13d_hourly.csv").merge(G, on="icustay_id").merge(X, on="icustay_id")
H["si"] = np.where(H.hr.between(20, 250) & H.sbp.between(40, 260), H.hr / H.sbp, np.nan)
H["pp"] = H.sbp - H.dbp; H["map"] = H.mbp
H["hb"] = (np.ceil(H.tip) - 1 - H.hour).astype(int); H = H[H.hb.between(0, 11)].copy()
CH = ["map", "si", "pp", "hr", "rr", "spo2"]
A_, K_ = H[H.who == "Ajay"], H[H.who == "Kranthi"]
rec, sh, sd = A_[CH].median(), K_[K_.hb == 0][CH].median(), A_[CH].std()
w = (sh - rec).abs() / sd
print("Anchors and weights:\n", pd.DataFrame({"recovery": rec, "shock": sh, "weight": w}).round(2).to_string(), "\n")
F = ((H[CH] - rec) / (sh - rec)).clip(-0.5, 1.5)
W = F.notna() * w
H["road"] = (F.fillna(0) * w).sum(axis=1) / W.sum(axis=1).replace(0, np.nan)
H["witnesses"] = ((F >= 0.5) & (w >= 0.2)).sum(axis=1)
H["A"] = np.where(H.si.notna() & H["map"].notna(), (H.si >= 1) & (H["map"] <= 65), np.nan)
H["grp"] = np.where(H.who == "Kranthi", "Kranthi " + H["shape"], "Ajay")
pd.set_option("display.width", 220)
T = H.groupby(["hb", "grp"]).road.median().unstack().sort_index(ascending=False).round(2); T.index.name = "h before tip"
print("Median road position (0 = Ajay, 1 = Kranthi at tip):\n" + T.to_string(), "\n")
low = H[H.hb.between(8, 11)].groupby("icustay_id")["map"].agg(["count", "median"])
lowA = set(low[(low["count"] >= 3) & (low["median"] <= 65)].index)
def auc(a, b):
    a, b = np.asarray(pd.Series(a).dropna(), float), np.asarray(pd.Series(b).dropna(), float)
    if len(a) == 0 or len(b) == 0: return np.nan
    return (a[:, None] > b[None, :]).mean() + 0.5 * (a[:, None] == b[None, :]).mean()
for hb in (8, 4, 2):
    S = H[H.hb == hb]; k = S[S.who == "Kranthi"]; a = S[S.who == "Ajay"]; al = a[a.icustay_id.isin(lowA)]
    print(f"{hb} h: road AUC vs all Ajays {auc(k.road, a.road):.2f}, vs low-sitting Ajays {auc(k.road, al.road):.2f} | "
          f"witnesses AUC {auc(k.witnesses, a.witnesses):.2f} | rule A vs all {auc(k.A, a.A):.2f}")
    print("     by shape vs low-sitting Ajays: " + "  ".join(f"{s} {auc(g.road, al.road):.2f}" for s, g in k.groupby("shape")))
