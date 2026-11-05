
# ---- E15 (appended): settling matched on ICU hour and tier, descriptive ----
SPLIT = "__SPLIT__"
has_tier = "tier" in D2.columns and "tier" in S2.columns
keys = ["tier", "hour"] if has_tier else ["hour"]
out = [f"E15 — change from own hours 0-2, deteriorating vs stable matched on ICU hour (+-1)"
       f"{' and tier' if has_tier else ''}, {SPLIT}", ""]
for m in ("d_hr", "d_map"):
    S = S2.dropna(subset=[m])
    grp = {kk: v.values for kk, v in S.groupby(keys)[m]}
    out.append(f"=== {m} ===")
    for k in range(13):
        d = D2[D2.k == k].dropna(subset=[m])
        diffs, pw, refmed = [], [], []
        for _, r in d.iterrows():
            if pd.isna(r.hour) or (has_tier and pd.isna(r.tier)):
                continue
            parts = [grp[(r.tier, hh) if has_tier else hh]
                     for hh in range(int(r.hour) - 1, int(r.hour) + 2)
                     if ((r.tier, hh) if has_tier else hh) in grp]
            if not parts:
                continue
            ref = np.sort(np.concatenate(parts))
            if len(ref) < 30:
                continue
            x = r[m]; med = np.median(ref)
            refmed.append(med); diffs.append(x - med)
            lo, hi = np.searchsorted(ref, x, "left"), np.searchsorted(ref, x, "right")
            pw.append((lo + 0.5 * (hi - lo)) / len(ref))
        if not pw:
            continue
        out.append(f"   -{k:>2}h  n={len(pw):5d}  det {d[m].median():+.1f}  matched stable {np.median(refmed):+.1f}  "
                   f"median diff {np.median(diffs):+.1f}  matched AUC {np.mean(pw):.3f}")
    out.append("")
text = "\n".join(out); print(text); open(f"E15_SETTLING_{SPLIT}.txt", "w").write(text + "\n")
