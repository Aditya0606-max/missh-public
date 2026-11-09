# C1 Charting control (CONTROLS.md). MIMIC-III only. Share of watched hours with >=1 reading, per channel.
import pandas as pd, numpy as np
rng = np.random.default_rng(2026)
G = pd.read_csv("c13_groups.csv"); H = pd.read_csv("c13d_hourly.csv")
H["bp"] = H[["sbp", "mbp"]].notna().any(axis=1)
print("Tip present per group:\n", G.groupby("who").tip.apply(lambda s: f"{s.notna().sum()}/{len(s)}"), "\n")

last = H.groupby("icustay_id").hour.max()
det_tips = G.loc[(G.who != "Ajay") & G.tip.notna(), "tip"].values
def window_end(r):
    if pd.notna(r.tip): return min(r.tip, 72)
    L = last.get(r.icustay_id, np.nan)            # Ajay with no tip: pseudo-tip from deteriorating tips
    pool = det_tips[det_tips <= L] if pd.notna(L) else []
    return min(rng.choice(pool), 72) if len(pool) else np.nan
G["end"] = G.apply(window_end, axis=1)
print("No usable window:", G.end.isna().groupby(G.who).sum().to_dict(), "\n")

W = H.merge(G[["icustay_id", "who", "end"]].dropna(), on="icustay_id")
W = W[(W.hour >= 0) & (W.hour < W.end)]
rows = []
for (sid, who), g in W.groupby(["icustay_id", "who"]):
    n = int(np.ceil(g.end.iloc[0])); r = {"who": who, "hours": n}
    for c in ["hr", "bp", "rr", "spo2"]:
        has = g["bp"] if c == "bp" else g[c].notna()
        r[c] = g.loc[has, "hour"].nunique() / n
    rows.append(r)
C = pd.DataFrame(rows)
S = C.groupby("who").agg(stays=("hours", "size"), hours_median=("hours", "median"),
                         hr=("hr", "mean"), bp=("bp", "mean"), rr=("rr", "mean"), spo2=("spo2", "mean")).round(2)
print("Share of watched hours with >=1 reading (mean per stay):\n", S, "\n")
R = (S[["hr", "bp", "rr", "spo2"]] / S.loc["Ajay", ["hr", "bp", "rr", "spo2"]]).round(2)
print("Ratio to Ajay:\n", R, "\n")
F = R[(R - 1).abs() >= 0.25].stack()
print("FLAGS (>=25% from Ajay):", "none" if F.empty else F.to_dict())
