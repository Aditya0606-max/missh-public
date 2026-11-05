
# ---- E18 (appended): ruler at hour 0-1, first ICU hours, descriptive ----
SPLIT = "__SPLIT__"
CH = [c for c in ("hr", "map", "rr", "spo2") if c in M2.columns]
if "hr" not in CH or "map" not in CH:
    print("E18: HR/MAP columns not found in M2:", list(M2.columns)); raise SystemExit(1)
W = {"hr": 1.0, "map": -1.0, "rr": 1.0, "spo2": -1.0}
extra = [c for c in ("tier", "tgroup") if c in M2.columns]
R = M2[["stay_id", "cohort", "hour", "k"] + extra + CH].copy()
R = R[R.hour.notna()].sort_values(["stay_id", "hour"])
st = R[R.cohort == "stable"]
SD = {}
for c in CH:
    s = float(np.nanstd(st.groupby("stay_id")[c].diff()))
    SD[c] = s if np.isfinite(s) and s > 0 else 1.0
n_tot = R.groupby("cohort").stay_id.nunique().to_dict()
o = R[R.hour.isin([0, 1])].groupby("stay_id")[CH].mean().add_suffix("_o")
R = R.merge(o, left_on="stay_id", right_index=True, how="inner")
n_org = R.groupby("cohort").stay_id.nunique().to_dict()
for c in CH:
    R[f"z_{c}"] = (R[c] - R[f"{c}_o"]) / SD[c]
def cosine(cols):
    Z = R[[f"z_{c}" for c in cols]].values
    w = np.array([W[c] for c in cols]); w = w / np.linalg.norm(w)
    ok = np.isfinite(Z).all(axis=1); d = np.sqrt(np.nansum(Z ** 2, axis=1))
    return np.where(ok & (d > 0), (Z @ w) / np.where(d > 0, d, 1), np.nan), np.where(ok, d, np.nan)
R["cos_hm"], _ = cosine(["hr", "map"])
R["cos_4"], R["dist_4"] = cosine(CH)
R["dhr"] = R.groupby("stay_id")["hr"].diff(); R["dmap"] = R.groupby("stay_id")["map"].diff()
R["shock_step"] = np.where(R.dhr.notna() & R.dmap.notna(), ((R.dhr > 0) & (R.dmap < 0)).astype(float), np.nan)
R.loc[R.hour <= 1, "shock_step"] = np.nan
R["shock_share"] = R.groupby("stay_id")["shock_step"].transform(lambda s: s.expanding().mean())
has_tier = "tier" in R.columns
DET = R[(R.cohort == "det") & (R.k >= 1)]
STB = R[R.cohort == "stable"]
def matched_by_hour(D, m):
    S = STB.dropna(subset=[m]); keys = ["tier", "hour"] if has_tier else ["hour"]
    grp = {kk: v.values for kk, v in S.groupby(keys)[m]}
    res = []
    for h in range(2, 7):
        d = D[D.hour == h].dropna(subset=[m]); pw = []
        for _, r in d.iterrows():
            if has_tier and pd.isna(r.tier):
                continue
            parts = [grp[(r.tier, hh) if has_tier else hh] for hh in (h - 1, h, h + 1)
                     if ((r.tier, hh) if has_tier else hh) in grp]
            if not parts:
                continue
            ref = np.sort(np.concatenate(parts))
            if len(ref) < 30:
                continue
            x = r[m]; lo, hi = np.searchsorted(ref, x, "left"), np.searchsorted(ref, x, "right")
            pw.append((lo + 0.5 * (hi - lo)) / len(ref))
        if pw:
            sm = S[S.hour == h][m].median()
            res.append(f"   ICU h{h}  det n={len(pw):5d}  det median {d[m].median():+.3f}  "
                       f"stable median {sm:+.3f}  matched AUC {np.mean(pw):.3f}")
    return res
out = [f"E18 — ruler at hour 0-1, first ICU hours, deteriorating (before anchor) vs stable "
       f"matched on ICU hour (+-1){' and tier' if has_tier else ''}, {SPLIT}",
       "AUC = chance a deteriorating value is HIGHER than a matched stable one (higher = more toward shock).",
       f"Patients with a reading in hours 0-1: det {n_org.get('det', 0)} of {n_tot.get('det', 0)}, "
       f"stable {n_org.get('stable', 0)} of {n_tot.get('stable', 0)}",
       "Scale (stable hour-to-hour SD): " + ", ".join(f"{c} {SD[c]:.2f}" for c in CH), ""]
strata = [("all deteriorating", DET)]
if "tgroup" in DET.columns:
    strata.append(("anchor < 8 h", DET[DET.tgroup.isin(["<5", "5-8"])]))
for name, D in strata:
    for m in ("cos_hm", "cos_4", "dist_4", "shock_share"):
        out.append(f"=== {name}: {m} ===")
        out += matched_by_hour(D, m)
        out.append("")
text = "\n".join(out); print(text); open(f"E18_EARLY_RULER_{SPLIT}.txt", "w").write(text + "\n")
