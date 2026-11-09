# C10 revised (MIMIC3_COVERAGE_RULE.md). Kranthi shapes, one value per hour, last 6 h before tip.
import pandas as pd, numpy as np
G = pd.read_csv("c13_groups.csv"); G = G[G.tip >= 6]
H = pd.read_csv("c13d_hourly.csv").merge(G, on="icustay_id")
H["si"] = np.where(H.hr.between(20, 250) & H.sbp.between(40, 260), H.hr / H.sbp, np.nan)
H["pp"] = H.sbp - H.dbp
def slope(x, y):
    m = np.isfinite(x) & np.isfinite(y)
    return np.polyfit(x[m], y[m], 1)[0] if m.sum() >= 3 else np.nan
rows = []
for sid, g in H.groupby("icustay_id"):
    tip, who = g.tip.iloc[0], g.who.iloc[0]; last_k = int(np.ceil(tip)) - 1
    w = g[(g.hour >= last_k - 5) & (g.hour <= last_k)].sort_values("hour")
    s = w.dropna(subset=["si"]); strain = (s.si >= 1) & (s.pp <= 35)
    pump = len(s) >= 4 and strain.sum() >= 3 and s.si.iloc[-1] >= 1
    ms, hs = slope(w.hour.values, w.mbp.values.astype(float)), slope(w.hour.values, w.hr.values.astype(float))
    silent = len(s) >= 4 and ms <= -1 and hs <= 0.5
    rows.append(dict(icustay_id=sid, who=who, si_hours=len(s), pump=pump, silent=silent,
        shape="unreadable" if len(s) < 4 else "straining pump" if pump else "silent heart" if silent else "neither",
        first_strain_hb=(last_k - s.hour[strain].min()) if strain.any() else np.nan,
        map_slope=ms, hr_slope=hs))
X = pd.DataFrame(rows)
E = pd.read_csv("cuff_check_events.csv"); E = E[E.src == "cuff"].copy()
E["hb"] = np.floor(E.tip - E.h).clip(0, 5).astype(int)
cnt = E.groupby(["icustay_id", "hb"]).size().reset_index(name="n")
X = X.merge(cnt[cnt.n >= 2].groupby("icustay_id").hb.max().rename("first_speedup_hb"), on="icustay_id", how="left")
X.to_csv("c10_shapes.csv", index=False)
def report(X, title):
    print(f"\n==== {title} ====")
    T = pd.crosstab(X.who, X["shape"], normalize="index").round(2); T["n"] = X.who.value_counts()
    print(T.to_string())
    print("Both shapes (counted as pump):", X[X.pump & X.silent].who.value_counts().to_dict())
    print("Any cuff speed-up in last 6 h:", X.groupby("who").first_speedup_hb.apply(lambda s: round(s.notna().mean(), 2)).to_dict())
    K = X[(X.who == "Kranthi") & (X["shape"] == "straining pump")]
    both = K.dropna(subset=["first_strain_hb", "first_speedup_hb"])
    print(f"Straining-pump Kranthis: {len(K)}; with both a strain hour and a cuff speed-up: {len(both)}")
    if len(both):
        d = both.first_strain_hb - both.first_speedup_hb          # > 0: strain showed earlier than the speed-up
        print(f"  strain before speed-up {(d > 0).mean():.0%}, same hour {(d == 0).mean():.0%}, after {(d < 0).mean():.0%}; "
              f"median hours before tip: strain {both.first_strain_hb.median():.0f}, speed-up {both.first_speedup_hb.median():.0f}")
report(X, "All stays with tip >= 6 h")
try:
    U = pd.read_csv("m3_usable.csv"); wf = U[(U.tip_h >= 6) & (U.cov_any >= 0.8)].icustay_id
    report(X[X.icustay_id.isin(wf)], "Waveform subset (m3_usable: tip >= 6, cov_any >= 0.8)")
except Exception as ex:
    print("\nWaveform subset skipped:", ex)
