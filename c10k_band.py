import pandas as pd, numpy as np
src = open("c10i_road.py").read(); exec(src.split('print("Median road position')[0])
exec("\n".join(l for l in src.splitlines() if l.startswith(("low =", "lowA =", "def auc", "    a, b =", "    if len(a)", "    return"))))
for c in CH: H["f_" + c] = F[c]
L = H[H.icustay_id.isin(lowA)].copy()
print("Low-sitting patients:", L.drop_duplicates("icustay_id").who.value_counts().to_dict(), "\n")
rows = []
for c in (8, 4, 2):
    W = L[L.hb.between(c, c + 2)].sort_values(["icustay_id", "hb"], ascending=[True, False])
    for (sid, who, shape), g in W.groupby(["icustay_id", "who", "shape"]):
        r = dict(c=c, icustay_id=sid, who=who, shape=shape, road=g.road.mean())
        for ch in ["map", "si", "pp", "rr"]:
            v = g[ch].dropna(); r["bw_" + ch] = (v.max() - v.min()) / sd[ch] if len(v) >= 2 else np.nan
        fr = g[["road", "f_map", "f_si", "f_pp"]].values; steps = ok = 0
        for i in range(1, len(fr)):
            d = fr[i] - fr[i - 1]
            if np.isfinite(d[0]): ok += 1; steps += int(d[0] <= -0.05 and np.nansum(d[1:] < 0) >= 2)
        r["returns"] = steps if ok else np.nan
        rows.append(r)
R = pd.DataFrame(rows)
R["bw_rr_pp"] = R.bw_rr * R.bw_pp
R["bw_press"] = (R.bw_map * R.bw_si * R.bw_pp) ** (1 / 3)
pd.set_option("display.width", 220)
for c in (8, 4, 2):
    S = R[R.c == c].copy()
    S["combined"] = (S.road.rank(pct=True) + (-S.bw_press).rank(pct=True) + (-S.returns).rank(pct=True)) / 3
    k, a = S[S.who == "Kranthi"], S[S.who == "Ajay"]
    M = [("road", 1, "position"), ("bw_rr_pp", -1, "narrow RRxPP"), ("bw_press", -1, "narrow pressure"),
         ("returns", -1, "no return"), ("combined", 1, "all three")]
    print(f"==== {c} h before tip (low-sitting Kranthi n{len(k)} vs Ajay n{len(a)}): AUC, higher = Kranthi worse ====")
    print("  " + "  ".join(f"{lab} {auc(sg * k[m], sg * a[m]):.2f}" for m, sg, lab in M))
    for s, g in k.groupby("shape"): print(f"     {s:15s}: " + "  ".join(f"{lab} {auc(sg * g[m], sg * a[m]):.2f}" for m, sg, lab in M))
    print("  medians:", S.groupby("who")[["road", "bw_press", "bw_rr_pp", "returns"]].median().round(2).to_dict("index"))
    S["near"] = S.road >= 0.5; S["narrow"] = S.bw_press <= a.bw_press.median()
    print("  2x2 (share of each group):\n" + pd.crosstab(S.who, [S.near.map({True: "near", False: "not near"}),
          S.narrow.map({True: "narrow", False: "room"})], normalize="index").round(2).to_string(), "\n")
