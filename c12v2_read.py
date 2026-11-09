# C12v2 part 2: readings at 8, 4, 2 h before tip from 5-min blocks; bolus fade. Descriptive.
import pandas as pd, numpy as np
B = pd.read_csv("c12v2_blocks.csv"); L = pd.read_csv("c12v2_log.csv")
drop = set(L[L.reason.str.startswith("HR in only")].icustay_id); B = B[~B.icustay_id.isin(drop)]
B["si"] = np.where(B.hr.between(20, 250) & B.sbp.between(40, 260), B.hr / B.sbp, np.nan)
print("Patients:", B.drop_duplicates("icustay_id").who.value_counts().to_dict(), "| dropped:", L.who.value_counts().to_dict())
print("Pressure source share of blocks:\n", pd.crosstab(B.who, B.src, normalize="index").round(2).to_string(), "\n")
def auc(a, b):
    a, b = np.asarray(pd.Series(a).dropna(), float), np.asarray(pd.Series(b).dropna(), float)
    if len(a) == 0 or len(b) == 0: return np.nan
    return (a[:, None] > b[None, :]).mean() + 0.5 * (a[:, None] == b[None, :]).mean()
def slope(t, y):
    m = np.isfinite(y); return np.polyfit(t[m], y[m], 1)[0] if m.sum() >= 6 else np.nan
def feats(g):
    g = g.sort_values("blk", ascending=False); t = -g.blk.values * 5 / 60.0          # hours, increasing to tip
    mp, hr, si, rr = g["map"].values, g.hr.values, g.si.values, g.rr.values
    ok = np.isfinite(si) & np.isfinite(mp)
    out = dict(A_share=np.mean((si[ok] >= 1) & (mp[ok] <= 65)) if ok.sum() >= 6 else np.nan,
               map_low=-np.nanmedian(mp) if np.isfinite(mp).sum() >= 6 else np.nan,
               si_level=np.nanmedian(si) if np.isfinite(si).sum() >= 6 else np.nan,
               map_falling=-slope(t, mp), si_rising=slope(t, si), rr_creep=slope(t, rr))
    dm, dh = np.diff(mp), np.diff(hr)
    pr = np.isfinite(dm[:-1]) & np.isfinite(dh[1:])
    out["not_answering"] = np.corrcoef(dm[:-1][pr], dh[1:][pr])[0, 1] if pr.sum() >= 10 else np.nan
    if np.isfinite(mp).sum() >= 12:
        m = np.isfinite(mp); res = mp[m] - np.polyval(np.polyfit(t[m], mp[m], 1), t[m])
        out["slow_return"] = np.corrcoef(res[:-1], res[1:])[0, 1]
    else: out["slow_return"] = np.nan
    return pd.Series(out)
F = ["A_share", "map_low", "si_level", "map_falling", "si_rising", "rr_creep", "not_answering", "slow_return"]
for c in (8, 4, 2):
    W = B[B.blk.between(12 * c, 12 * c + 35)]
    R = W.groupby(["icustay_id", "who"]).apply(feats).reset_index()
    k, a, m = R[R.who == "Kranthi"], R[R.who == "Ajay"], R[R.who == "mixed"]
    print(f"==== {c} h before tip (preceding 3 h): AUC vs Ajay, higher = worse ====")
    print("  Kranthi: " + "  ".join(f"{f} {auc(k[f], a[f]):.2f} (n{k[f].notna().sum()})" for f in F))
    print("  mixed:   " + "  ".join(f"{f} {auc(m[f], a[f]):.2f}" for f in F))
Bo = pd.read_csv("m3_bolus.csv"); U = pd.read_csv("m3_usable.csv")[["icustay_id", "tip_h"]]
Bo = Bo.merge(U, on="icustay_id"); Bo["mb"] = (Bo.tip_h - Bo.h) * 60
Bo = Bo[Bo.icustay_id.isin(B.icustay_id) & Bo.mb.between(120, 690)]
rows = []
for r in Bo.itertuples():
    g = B[B.icustay_id == r.icustay_id]; mm = g.blk * 5
    pre = g[mm.between(r.mb, r.mb + 30)]["map"].median()
    g1 = g[mm.between(r.mb - 60, r.mb - 30)]["map"].median(); g2 = g[mm.between(r.mb - 120, r.mb - 90)]["map"].median()
    if np.isfinite([pre, g1, g2]).all(): rows.append(dict(icustay_id=r.icustay_id, gain=g1 - pre, kept=g2 - pre))
P = pd.DataFrame(rows)
if len(P):
    P["fade"] = P.gain - P.kept
    Q = P.groupby("icustay_id")[["gain", "kept", "fade"]].mean().join(B.drop_duplicates("icustay_id").set_index("icustay_id").who)
    print("\n==== Bolus fade (boluses >= 2 h before tip; per-patient mean) ====")
    print(Q.groupby("who")[["gain", "kept", "fade"]].median().round(1).join(Q.who.value_counts().rename("n")).to_string())
    print(f"  AUC fade Kranthi vs Ajay: {auc(Q[Q.who == 'Kranthi'].fade, Q[Q.who == 'Ajay'].fade):.2f}")
else:
    print("\nNo boluses with full before/after MAP in the window.")
