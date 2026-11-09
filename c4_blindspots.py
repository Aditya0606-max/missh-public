# C4 Blind-spot rehearsal (CONTROLS.md). Check at 2 h before tip; last-6 h window; C3b share version.
# PROVISIONAL line = Ajay 90th percentile (stand-in, NOT the frozen budget).
import pandas as pd, numpy as np
G = pd.read_csv("c13_groups.csv"); H = pd.read_csv("c13d_hourly.csv").merge(G, on="icustay_id")
B = pd.read_csv("m3_bolus.csv"); O = pd.read_csv("m3_o2_events_all.csv")
H["si"] = np.where(H.hr.between(20, 250) & H.sbp.between(40, 260), H.hr / H.sbp, np.nan)
H["pp"] = H.sbp - H.dbp
H["has_s"] = H.si.notna(); H["has_b"] = H.rr.notna() | H.spo2.notna()
H["bad_s"] = H.has_s & ((H.si >= 1) | (H.mbp <= 65) | (H.pp <= 30))
H["bad_b"] = H.has_b & ((H.rr >= 25) | (H.spo2 <= 92))
H["burden_s"] = ((H.si - 1).clip(lower=0) + (65 - H.mbp).clip(lower=0) / 10).fillna(0)
H["burden_b"] = ((H.rr - 25).clip(lower=0) / 5 + (92 - H.spo2).clip(lower=0) / 2).fillna(0)
O = O.dropna(subset=["num"]).sort_values(["icustay_id", "kind", "h"])
O = O[O.groupby(["icustay_id", "kind"]).num.diff() > 0]
TB = B.groupby("icustay_id").h.apply(np.array).to_dict(); TO = O.groupby("icustay_id").h.apply(np.array).to_dict()
def change(s):
    s = s.dropna(); return s.iloc[-1] - s.iloc[0] if len(s) >= 2 else np.nan
rows = []
for sid, g in H.groupby("icustay_id"):
    g = g.sort_values("hour"); who, tip = g.who.iloc[0], g.tip.iloc[0]
    c = int(np.ceil(tip)) - 3                      # last full hour ending 2 h before tip
    if c < 1: continue
    w = g[(g.hour >= max(c - 5, 0)) & (g.hour <= c)]
    r = dict(icustay_id=sid, who=who, c=c)
    for sd, has, bad, bur, tr, wit in [("s", "has_s", "bad_s", "burden_s", TB, "hr"), ("b", "has_b", "bad_b", "burden_b", TO, "rr")]:
        n = int(w[has].sum()); t = tr.get(sid, np.array([]))
        r.update({f"n_{sd}": n,
                  f"burden_{sd}": w[bur].sum() / n if n else np.nan,
                  f"good_{sd}": 1 - w[bad].sum() / n if n else np.nan,
                  f"treated_{sd}": bool(((t >= max(c - 5, 0)) & (t < c + 1)).any()),
                  f"witness_{sd}": change(w[wit]) > 0})
    rows.append(r)
X = pd.DataFrame(rows); X.to_csv("c4_features.csv", index=False)
for sd, who, side in [("s", "Kranthi", "SHOCK"), ("b", "Sundar", "BREATHING")]:
    S = X[X.who.isin([who, "Ajay"])].copy()
    S["score"] = (S[f"burden_{sd}"].rank(pct=True) + (-S[f"good_{sd}"]).rank(pct=True)) / 2
    line = S.loc[S.who == "Ajay", "score"].quantile(0.90)
    a = S[S.who == who].copy(); a["caught"] = a.score > line
    def bin_(r):
        if r[f"n_{sd}"] == 0: return "1 no readings"
        if r[f"n_{sd}"] < 3: return "2 sparse (<3 of 6 h)"
        if r[f"treated_{sd}"]: return "3 treatment masked"
        if not r[f"witness_{sd}"]: return "4 witness absent"
        return "5 no sign"
    m = a[~a.caught].copy(); m["bin"] = m.apply(bin_, axis=1)
    print(f"\n#### {side}: {who} at 2 h before tip (provisional line = Ajay 90th pct; ~10% of Ajays above)")
    print(f"  {who} checked {len(a)}, caught {a.caught.sum()} ({a.caught.mean():.0%}), missed {len(m)}")
    share = m.bin.value_counts(normalize=True).sort_index()
    print("  Misses by bin:\n" + "\n".join(f"    {k:22s} {int((m.bin == k).sum()):5d}  {v:.0%}" for k, v in share.items()))
    print("  FLAG: one bin holds >50% of misses" if share.max() > 0.5 else "  ok: no bin holds >50% of misses")
