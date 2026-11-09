# C3 Positive control (CONTROLS.md). No-return combination (C13d definition) at the last hour before tip.
import pandas as pd, numpy as np
G = pd.read_csv("c13_groups.csv"); H = pd.read_csv("c13d_hourly.csv").merge(G, on="icustay_id")
H["si"] = np.where(H.hr.between(20, 250) & H.sbp.between(40, 260), H.hr / H.sbp, np.nan)
H["pp"] = H.sbp - H.dbp
H["has_s"] = H.si.notna(); H["has_b"] = H.rr.notna() | H.spo2.notna()
H["bad_s"] = H.has_s & ((H.si >= 1) | (H.mbp <= 65) | (H.pp <= 30))
H["bad_b"] = H.has_b & ((H.rr >= 25) | (H.spo2 <= 92))
H["burden_s"] = ((H.si - 1).clip(lower=0) + (65 - H.mbp).clip(lower=0) / 10).fillna(0)
H["burden_b"] = ((H.rr - 25).clip(lower=0) / 5 + (92 - H.spo2).clip(lower=0) / 2).fillna(0)
def pts(v, cuts):
    if pd.isna(v): return np.nan
    for lo, hi, p in cuts:
        if lo <= v <= hi: return p
    return 0
RRc = [(-1, 8, 3), (9, 11, 1), (12, 20, 0), (21, 24, 2), (25, 999, 3)]
SPc = [(-1, 91, 3), (92, 93, 2), (94, 95, 1), (96, 101, 0)]
SBc = [(-1, 90, 3), (91, 100, 2), (101, 110, 1), (111, 219, 0), (220, 999, 3)]
HRc = [(-1, 40, 3), (41, 50, 1), (51, 90, 0), (91, 110, 1), (111, 130, 2), (131, 999, 3)]
TPc = [(-1, 35.0, 3), (35.01, 36.0, 1), (36.01, 38.0, 0), (38.01, 39.0, 1), (39.01, 99, 2)]
def longest_good(v):
    run = best = 0
    for x in v: run = run + 1 if not x else 0; best = max(best, run)
    return best
rows = []
for sid, g in H.groupby("icustay_id"):
    g = g.sort_values("hour"); who, tip = g.who.iloc[0], g.tip.iloc[0]
    te = int(np.ceil(tip)) - 1                      # last full hour before tip
    h = g[(g.hour >= 0) & (g.hour <= te)]
    if te < 1 or h.empty: continue
    first, recent = h[h.hour <= 2], h[h.hour >= te - 2]
    last = lambda c: recent[c].dropna().iloc[-1] if recent[c].notna().any() else np.nan
    comp = [pts(last("rr"), RRc), pts(last("spo2"), SPc), pts(last("sbp"), SBc), pts(last("hr"), HRc), pts(last("temp"), TPc)]
    ns, nb = max(h.has_s.sum(), 1), max(h.has_b.sum(), 1)
    rows.append(dict(icustay_id=sid, who=who, te=te,
        arr_s=first.bad_s.any(), arr_b=first.bad_b.any(),
        burden_s_rate=h.burden_s.sum() / ns, good_run_s=longest_good(h.bad_s[h.has_s].values),
        burden_b_rate=h.burden_b.sum() / nb, good_run_b=longest_good(h.bad_b[h.has_b].values),
        news_lite=np.nansum(comp) if np.isfinite(comp).sum() >= 3 else np.nan,
        fresh_s=h[h.hour >= te - 1].has_s.any(), fresh_b=h[h.hour >= te - 1].has_b.any()))
X = pd.DataFrame(rows); X.to_csv("c3_features.csv", index=False)
def auc(a, b):
    a, b = np.asarray(a.dropna(), float), np.asarray(b.dropna(), float)
    if len(a) == 0 or len(b) == 0: return np.nan
    return (a[:, None] > b[None, :]).mean() + 0.5 * (a[:, None] == b[None, :]).mean()
for side, who, committed in [("s", "Kranthi", True), ("s", "mixed", False), ("b", "Sundar", True), ("b", "mixed", False)]:
    bur, run, arr, fr = f"burden_{side}_rate", f"good_run_{side}", f"arr_{side}", f"fresh_{side}"
    print(f"\n#### {'SHOCK' if side == 's' else 'BREATHING'}: {who} vs Ajay {'(committed)' if committed else '(descriptive)'}")
    for label, S in [("all", X[X.who.isin([who, "Ajay"])]), ("arrived bad", X[X.who.isin([who, "Ajay"]) & X[arr]])]:
        S = S.copy(); S["combo"] = (S[bur].rank(pct=True) + (-S[run]).rank(pct=True)) / 2
        a, b = S[S.who == who], S[S.who == "Ajay"]
        A = {f: auc(sg * a[f], sg * b[f]) for f, sg in [("combo", 1), (bur, 1), (run, -1), ("news_lite", 1)]}
        print(f"  {label:11s} n {len(a)}/{len(b)}  combo {A['combo']:.2f}  burden {A[bur]:.2f}  "
              f"good_run {A[run]:.2f}  NEWS-lite {A['news_lite']:.2f}  fresh reading last 2 h: {a[fr].mean():.2f}/{b[fr].mean():.2f}")
        if committed and label == "all":
            print("  FLAG: combo AUC < 0.65" if A["combo"] < 0.65 else "  ok: combo AUC >= 0.65")
