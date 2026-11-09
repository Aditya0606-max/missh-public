import pandas as pd, numpy as np
X = pd.read_csv("c10_shapes.csv")[["icustay_id", "who", "shape"]]; X = X[X.who.isin(["Kranthi", "Ajay"])]
G = pd.read_csv("c13_groups.csv")[["icustay_id", "tip"]]
H = pd.read_csv("c13d_hourly.csv")[["icustay_id", "hour", "mbp"]].dropna()
H = H.groupby(["icustay_id", "hour"]).mbp.mean().reset_index()
B = pd.read_csv("m3_bolus.csv").merge(G, on="icustay_id").merge(X, on="icustay_id")
B = B[(B.h >= 1) & (B.h <= B.tip - 3)].copy(); B["bh"] = np.floor(B.h).astype(int)
for col, off in [("before", -1), ("after1", 1), ("after2", 2)]:
    K = H.rename(columns={"hour": "bh", "mbp": col}).copy(); K["bh"] = K.bh - off
    B = B.merge(K, on=["icustay_id", "bh"], how="left")
B = B.dropna(subset=["before", "after1", "after2"])
B["gain"] = B.after1 - B.before; B["fallback"] = B.after1 - B.after2
P = B.groupby(["icustay_id", "who", "shape"])[["gain", "fallback"]].mean().reset_index()
def auc(a, b):
    a, b = np.asarray(a.dropna(), float), np.asarray(b.dropna(), float)
    if len(a) == 0 or len(b) == 0: return np.nan
    return (a[:, None] > b[None, :]).mean() + 0.5 * (a[:, None] == b[None, :]).mean()
print("Boluses used:", B.groupby("who").size().to_dict(), "| patients:", P.who.value_counts().to_dict())
print(P.groupby("who")[["gain", "fallback"]].median().round(1).to_string())
k, a = P[P.who == "Kranthi"], P[P.who == "Ajay"]
print(f"AUC fallback Kranthi vs Ajay: {auc(k.fallback, a.fallback):.2f} | AUC smaller gain: {auc(-k.gain, -a.gain):.2f}")
for sh, g in k.groupby("shape"):
    print(f"  {sh:15s} n {len(g):3d}  fallback median {g.fallback.median():5.1f}  AUC {auc(g.fallback, a.fallback):.2f}")
