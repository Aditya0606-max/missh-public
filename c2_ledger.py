# C2 Treatment ledger (CONTROLS.md). MIMIC-III only. Share of recoveries preceded by treatment.
import pandas as pd, numpy as np
G = pd.read_csv("c13_groups.csv"); H = pd.read_csv("c13_hourly.csv").merge(G, on="icustay_id")
B = pd.read_csv("m3_bolus.csv"); O = pd.read_csv("m3_o2_events_all.csv")
print("O2 event kinds:\n", O.kind.value_counts(), "\n")
H = H[(H.hour >= 0) & (H.hour < H.tip.clip(upper=72))].sort_values(["icustay_id", "hour"])
H["si"] = H.hr / H.sbp; H["pp"] = H.sbp - H.dbp
sides = {"shock": (H[["map", "sbp"]].notna().any(axis=1), (H.si >= 1) | (H["map"] <= 65) | (H.pp <= 30)),
         "breathing": (H[["rr", "spo2"]].notna().any(axis=1), (H.rr >= 25) | (H.spo2 <= 92))}
# oxygen increases: numeric value rising vs the previous one of the same kind
O = O.dropna(subset=["num"]).sort_values(["icustay_id", "kind", "h"])
O = O[O.groupby(["icustay_id", "kind"]).num.diff() > 0]
treat = {"shock": B.groupby("icustay_id").h.apply(np.array).to_dict(),
         "breathing": O.groupby("icustay_id").h.apply(np.array).to_dict()}
rows = []
for side, (known, bad) in sides.items():
    D = H[["icustay_id", "who", "hour"]].copy(); D["known"] = known; D["bad"] = bad & known
    g = D.groupby("icustay_id")
    D["rec"] = ((D.hour - g.hour.shift() == 1) & g.bad.shift().fillna(False).astype(bool)
                & g.known.shift().fillna(False).astype(bool) & D.known & ~D.bad)
    for r in D[D.rec].itertuples():
        t = treat[side].get(r.icustay_id, np.array([]))
        rows.append({"side": side, "who": r.who, "treated": bool(((t >= r.hour - 1) & (t < r.hour + 1)).any())})
R = pd.DataFrame(rows)
S = R.groupby(["side", "who"]).agg(recoveries=("treated", "size"), after_treatment=("treated", "mean")).round(2)
print("Recoveries and share preceded by treatment:\n", S, "\n")
for side in sides:
    a = S.loc[(side, "Ajay"), "after_treatment"]
    print(f"FLAG {side}:" if a > 0.5 else f"ok {side}:", f"Ajay returns after treatment = {a}")
