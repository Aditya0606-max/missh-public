
# ---- E16 (appended): F1/F3 underneath, matched on ICU hour and tier, descriptive ----
SPLIT = "__SPLIT__"
F = pd.read_csv("../missh_data/f1f3_hourly.csv")
def todict(col):
    x = F.dropna(subset=[col])
    return {(int(s), int(h)): v for s, h, v in zip(x.stay_id, x.hour_idx, x[col])}
UO, LAC, BE = todict("uo_ml"), todict("lactate"), todict("base_excess")
def last_within(D, sid, h, back=5):
    for x in range(h, h - back - 1, -1):
        if (sid, x) in D:
            return D[(sid, x)]
    return np.nan
def add_feats(T):
    u1, u3, lac6, be6, drawn = [], [], [], [], []
    for sid, h in zip(T.stay_id.values, T.hour.values):
        if pd.isna(h):
            u1.append(np.nan); u3.append(np.nan); lac6.append(np.nan); be6.append(np.nan); drawn.append(np.nan); continue
        sid, h = int(sid), int(h)
        u1.append(UO.get((sid, h), np.nan))
        v = [UO[(sid, x)] for x in (h - 2, h - 1, h) if (sid, x) in UO]
        u3.append(np.mean(v) if len(v) >= 2 else np.nan)
        lac6.append(last_within(LAC, sid, h)); be6.append(last_within(BE, sid, h))
        drawn.append(1.0 if (sid, h) in LAC else 0.0)
    T = T.copy()
    T["uo_1h"], T["uo_3h_mean"], T["lactate_6h"], T["base_excess_6h"], T["lactate_drawn"] = u1, u3, lac6, be6, drawn
    return T
D3, S3 = add_feats(D2), add_feats(S2)
has_tier = "tier" in D3.columns and "tier" in S3.columns
keys = ["tier", "hour"] if has_tier else ["hour"]
def matched(D, S, m):
    S = S.dropna(subset=[m])
    grp = {kk: v.values for kk, v in S.groupby(keys)[m]}
    res = []
    for k in range(13):
        d = D[D.k == k].dropna(subset=[m])
        diffs, pw = [], []
        for _, r in d.iterrows():
            if pd.isna(r.hour) or (has_tier and pd.isna(r.tier)):
                continue
            parts = [grp[(r.tier, hh) if has_tier else hh] for hh in range(int(r.hour) - 1, int(r.hour) + 2)
                     if ((r.tier, hh) if has_tier else hh) in grp]
            if not parts:
                continue
            ref = np.sort(np.concatenate(parts))
            if len(ref) < 30:
                continue
            x = r[m]; diffs.append(x - np.median(ref))
            lo, hi = np.searchsorted(ref, x, "left"), np.searchsorted(ref, x, "right")
            pw.append((lo + 0.5 * (hi - lo)) / len(ref))
        n_all = int((D.k == k).sum())
        if pw:
            res.append(f"   -{k:>2}h  measured {len(pw):5d} of {n_all:5d}  det median {d[m].median():+.2f}  "
                       f"median diff {np.median(diffs):+.2f}  matched AUC {np.mean(pw):.3f}")
    return res
out = [f"E16 — F1/F3 underneath, deteriorating vs stable matched on ICU hour (+-1)"
       f"{' and tier' if has_tier else ''}, {SPLIT}",
       "AUC = chance a deteriorating value is HIGHER than a matched stable one.",
       "Urine: AUC < 0.5 means less urine (worse). Lactate: > 0.5 means higher (worse).",
       "Base excess: < 0.5 means more negative (worse). Drawn: > 0.5 means drawn more often (suspicion).", ""]
strata = [("all deteriorating", D3)]
if "tgroup" in D3.columns:
    strata.append(("anchor < 8 h", D3[D3.tgroup.isin(["<5", "5-8"])]))
for name, D in strata:
    for m in ("uo_1h", "uo_3h_mean", "lactate_6h", "base_excess_6h", "lactate_drawn"):
        out.append(f"=== {name}: {m} ===")
        out += matched(D, S3, m)
        out.append("")
text = "\n".join(out); print(text); open(f"E16_F1F3_{SPLIT}.txt", "w").write(text + "\n")
