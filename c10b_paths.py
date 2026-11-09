# C10b: hour-by-hour path before tip, same patients and shapes as C10. Descriptive.
import pandas as pd, numpy as np
X = pd.read_csv("c10_shapes.csv")[["icustay_id", "who", "shape"]]
G = pd.read_csv("c13_groups.csv")[["icustay_id", "tip"]]
H = pd.read_csv("c13d_hourly.csv").merge(G, on="icustay_id").merge(X, on="icustay_id")
H["si"] = np.where(H.hr.between(20, 250) & H.sbp.between(40, 260), H.hr / H.sbp, np.nan)
H["pp"] = H.sbp - H.dbp
H["hb"] = (np.ceil(H.tip) - 1 - H.hour).astype(int)            # 0 = last hour before tip
H = H[H.hb.between(0, 11)]
groups = {"Kranthi straining pump": (H.who == "Kranthi") & (H["shape"] == "straining pump"),
          "Kranthi silent heart":   (H.who == "Kranthi") & (H["shape"] == "silent heart"),
          "Kranthi neither":        (H.who == "Kranthi") & (H["shape"] == "neither"),
          "Ajay all":               (H.who == "Ajay"),
          "Ajay pump-shaped":       (H.who == "Ajay") & (H["shape"] == "straining pump")}
pd.set_option("display.width", 200)
for name, m in groups.items():
    D = H[m]
    T = D.groupby("hb").agg(n=("si", "count"), SI=("si", "median"), SI_ge1=("si", lambda s: (s.dropna() >= 1).mean()),
                            PP=("pp", "median"), MAP=("mbp", "median"), HR=("hr", "median"))
    T = T.sort_index(ascending=False).round({"SI": 2, "SI_ge1": 2, "PP": 0, "MAP": 0, "HR": 0})
    T.index.name = "h before tip"
    print(f"\n==== {name}: {D.icustay_id.nunique()} patients ====\n{T.to_string()}")
