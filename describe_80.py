# describe_80.py — DESCRIPTIVE_TRAJECTORIES: trajectories, per-patient alarm outcomes,
# treatment context, case atlas, state-space path, bolus-aligned picture, groups.
# Descriptive only. Runs on whichever split sits in ../missh_data.
import json, os
import numpy as np
import pandas as pd

rng = np.random.default_rng(2026)
anc = pd.read_csv("../missh_data/anchors_cal_v2.csv")
age = pd.read_csv("../missh_data/age_cal.csv").set_index("stay_id").admission_age
K = ["stay_id", "cohort", "k", "hour"]
p3 = pd.read_csv("../missh_data/measures_p3_traj.csv", low_memory=False)
p1 = pd.read_csv("../missh_data/measures_p1_traj.csv", low_memory=False)
pp = pd.read_csv("../missh_data/measures_pp_traj.csv", low_memory=False)
for p in (p1, p3, pp):
    p["k"] = p.k.fillna(-1)
M = (p3[K + ["tier", "news", "news_items", "share_defend"]]
     .merge(p1[K + ["D_main", "Dw_main"]], on=K, how="left")
     .merge(pp[K + ["pp_rel", "dpp4", "dhr4", "dmap4"]], on=K, how="left"))
M["cos"] = np.where(M.D_main > 0, M.Dw_main / M.D_main, np.nan)
M["age"] = M.stay_id.map(age)
M["age_band"] = pd.cut(M.age, [0, 50, 65, 80, 200], right=False, labels=["<50", "50-64", "65-79", ">=80"])
A = anc.set_index("stay_id")
M["anchor"] = M.stay_id.map(A.anchor)
M["tgroup"] = pd.cut(M.anchor, [0, 5, 8, 24, 72.01], right=False, labels=["<5", "5-8", "8-24", "24-72"])
MEAS = ["cos", "D_main", "Dw_main", "pp_rel", "dpp4", "dhr4", "dmap4", "share_defend", "news"]
DET, ST = M[M.cohort == "det"], M[M.cohort == "stable"]

rows = []
def traj(name, det, st):
    for k in range(13):
        d = det[det.k == k]
        if d.empty: continue
        s = st[st.hour.isin(d.hour.unique())]
        for m in MEAS:
            dv, sv = d[m].dropna(), s[m].dropna()
            rows.append(dict(stratum=name, k=k, measure=m, n_det=len(dv),
                             det_median=dv.median() if len(dv) else np.nan,
                             det_q25=dv.quantile(.25) if len(dv) else np.nan,
                             det_q75=dv.quantile(.75) if len(dv) else np.nan,
                             n_stable=len(sv), stable_median=sv.median() if len(sv) else np.nan,
                             stable_q95=sv.quantile(.95) if len(sv) else np.nan))
traj("overall", DET, ST)
for b in ["<50", "50-64", "65-79", ">=80"]:
    traj(f"age {b}", DET[DET.age_band == b], ST[ST.age_band == b])
for g in ["<5", "5-8", "8-24", "24-72"]:
    traj(f"anchor {g} h", DET[DET.tgroup == g], ST)
TR = pd.DataFrame(rows)
TR.to_csv("DESCRIBE_TRAJ.csv", index=False)

S = pd.read_csv("../missh_data/series_dw.csv")
v = pd.read_csv("../missh_data/vitals_hourly_cal_v2.csv")
for c in ["block_bolus", "block_iv", "sed_infusion", "flag_oral_bp", "flag_sed_dose"]:
    v[c] = v[c].astype(str).str.lower().eq("true")
v["blocked"] = v.block_bolus | v.block_iv | v.sed_infusion
v["flagged"] = v.flag_oral_bp | v.flag_sed_dose
VB = v.set_index(["stay_id", "hour_idx"])
FL = {n: json.load(open(f)) for n, f in (("main", "FLAG_FROZEN.json"), ("sens", "FLAG_SENS_FROZEN.json"))}
for f in FL.values():
    f["L"] = {int(h): x for h, x in f["lines"].items()}

def counter_states(g, f):
    c, out = 0, {}
    for _, r in g.sort_values("hour").iterrows():
        L = f["L"].get(int(r.hour), np.nan)
        if np.isfinite(r.dw) and np.isfinite(L):
            c = c + 1 if r.dw > L else max(0, c - 1)
        out[int(r.hour)] = c >= f["p"]
    return out

T = anc[anc.target & (anc.cohort == "deteriorating") & anc.anchor.notna() & anc.open_h.notna()]
SG = {sid: g for sid, g in S.groupby("stay_id")}
per = []
for _, a in T.iterrows():
    g = SG.get(a.stay_id)
    rec = dict(sid=a.stay_id, tier=a.ptier, anchor=a.anchor, anchor_type=a.anchor_type,
               age=age.get(a.stay_id, np.nan))
    for n, f in FL.items():
        st = counter_states(g, f) if g is not None else {}
        fired = [h for h, on in sorted(st.items()) if on]
        ft = fired[0] + 1 if fired else np.nan
        if not np.isfinite(ft): cat = "never"
        elif a.anchor_type == "news": cat = "before NEWS" if ft < a.anchor else "same hour"
        else: cat = "before event (NEWS never crossed)"
        rec[f"{n}_cat"], rec[f"{n}_lead"] = cat, (a.anchor - ft) if np.isfinite(ft) else np.nan
    hs = range(int(np.floor(a.anchor)) - 4, int(np.floor(a.anchor)))
    bl = any(VB.blocked.get((a.stay_id, h), False) for h in hs)
    fg = any(VB.flagged.get((a.stay_id, h), False) for h in hs)
    rec["treatment_4h"] = "blocked" if bl else ("flag only" if fg else "none")
    per.append(rec)
PER = pd.DataFrame(per)
PER["tgroup"] = pd.cut(PER.anchor, [0, 5, 8, 24, 72.01], right=False, labels=["<5", "5-8", "8-24", "24-72"])
PER.drop(columns=["sid"]).to_csv("DESCRIBE_PER_PATIENT.csv", index=False)

def mauc(det, col):
    p = []
    for _, r in det.dropna(subset=[col]).iterrows():
        ref = ST[(ST.tier == r.tier) & ST.hour.between(r.hour - 2, r.hour + 2)][col].dropna().values
        if len(ref) >= 30: p.append((ref < r[col]).mean() + 0.5 * (ref == r[col]).mean())
    return (np.mean(p), len(p)) if p else (np.nan, 0)
TRT = PER.set_index("sid").treatment_4h
d2 = DET[DET.k == 2].copy(); d2["trt"] = d2.stay_id.map(TRT)

os.makedirs("atlas", exist_ok=True)
det_ids = sorted(T.stay_id.unique())
st_ids = sorted(anc[anc.target & (anc.cohort == "stable") & anc.open_h.notna()].stay_id.unique())
pick = [("det", s) for s in rng.choice(det_ids, min(20, len(det_ids)), replace=False)] + \
       [("stable", s) for s in rng.choice(st_ids, min(20, len(st_ids)), replace=False)]
news = pd.read_csv("../missh_data/news_hourly_cal.csv").set_index(["stay_id", "hour_idx"]).news
idx = []
for i, (coh, sid) in enumerate(pick, 1):
    g = SG.get(sid)
    last = int(np.floor(A.loc[sid, "anchor"])) if coh == "det" else 71
    stm = counter_states(g, FL["main"]) if g is not None else {}
    sts = counter_states(g, FL["sens"]) if g is not None else {}
    dw = g.set_index("hour").dw if g is not None else pd.Series(dtype=float)
    out = []
    for h in range(0, last + 1):
        r = VB.loc[(sid, h)] if (sid, h) in VB.index else None
        out.append(dict(hour=h, hours_to_anchor=(A.loc[sid, "anchor"] - (h + 1)) if coh == "det" else np.nan,
                        hr=r.hr if r is not None else np.nan, map=r["map"] if r is not None else np.nan,
                        rr=r.rr if r is not None else np.nan, spo2=r.spo2 if r is not None else np.nan,
                        news=news.get((sid, h), np.nan), dw=dw.get(h, np.nan),
                        alarm_main=stm.get(h, np.nan), alarm_sens=sts.get(h, np.nan),
                        bolus=r.block_bolus if r is not None else np.nan, iv_drug=r.block_iv if r is not None else np.nan,
                        sed_infusion=r.sed_infusion if r is not None else np.nan,
                        oral_bp=r.flag_oral_bp if r is not None else np.nan, sed_dose=r.flag_sed_dose if r is not None else np.nan))
    pd.DataFrame(out).to_csv(f"atlas/case_{i:02d}.csv", index=False)
    b = age.get(sid, np.nan)
    idx.append(dict(case=f"{i:02d}", cohort=coh, tier=A.loc[sid, "ptier"],
                    age_band=pd.cut([b], [0, 50, 65, 80, 200], right=False,
                                    labels=["<50", "50-64", "65-79", ">=80"])[0] if np.isfinite(b) else None))
pd.DataFrame(idx).to_csv("atlas/index.csv", index=False)

L = ["DESCRIBE_80 — descriptive only", "",
     "Overall trajectory (median det | median stable at same ICU hours):"]
o = TR[TR.stratum == "overall"]
for m in ["cos", "Dw_main", "share_defend", "pp_rel", "news"]:
    x = o[o.measure == m].sort_values("k", ascending=False)
    L.append(f"   {m:12s} " + "  ".join(f"-{int(r.k)}h {r.det_median:.2f}|{r.stable_median:.2f}" for _, r in x.iterrows()))
L += ["", "Per-patient alarm outcome (deteriorating):"]
for n in ("main", "sens"):
    L.append(f"   {n}: " + PER[f"{n}_cat"].value_counts().to_string().replace("\n", "; "))
    for g in ["<5", "5-8", "8-24", "24-72"]:
        x = PER[PER.tgroup == g]
        if len(x):
            L.append(f"      anchor {g} h (n={len(x)}): before {(x[f'{n}_cat'].str.startswith('before')).mean():.3f}"
                     f"  never {(x[f'{n}_cat'] == 'never').mean():.3f}  median lead {x[f'{n}_lead'].median()}")
L += ["", f"Treatment in 4 h before anchor: {PER.treatment_4h.value_counts().to_dict()}"]
for t in ["none", "flag only", "blocked"]:
    x = d2[d2.trt == t]
    a1, n1 = mauc(x, "Dw_main"); a2, n2 = mauc(x, "share_defend")
    L.append(f"   {t:9s} 2h matched AUC: Dw_main {a1:.3f} (n={n1})  share_defend {a2:.3f} (n={n2})")
L += ["", f"Case atlas: {len(pick)} cases written to atlas/ (local only; check the PhysioNet data use"
      " agreement before sharing any patient-level timeline)"]
text = "\n".join(L); print(text); open("DESCRIBE_80.txt", "w").write(text + "\n")

CHN = ["hr", "map", "rr", "spo2"]
start = v[v.hour_idx <= 2].groupby("stay_id")[CHN].mean()
RAWV = v[["stay_id", "hour_idx"] + CHN].rename(columns={"hour_idx": "hour"})
M2 = M.drop(columns=[c for c in CHN if c in M.columns]).merge(RAWV, on=["stay_id", "hour"], how="left")
for c in CHN:
    M2[f"d_{c}"] = M2[c] - M2.stay_id.map(start[c])
ALM = []
for sid, g in SG.items():
    sm, ss = counter_states(g, FL["main"]), counter_states(g, FL["sens"])
    ALM += [(sid, h, float(sm[h]), float(ss.get(h, np.nan))) for h in sm]
ALM = pd.DataFrame(ALM, columns=["stay_id", "hour", "alarm_main", "alarm_sens"])
M2 = M2.merge(ALM, on=["stay_id", "hour"], how="left")
D2, S2 = M2[M2.cohort == "det"], M2[M2.cohort == "stable"]
RAWM = CHN + [f"d_{c}" for c in CHN] + ["alarm_main", "alarm_sens"]
rows2 = []
def traj2(name, det, st):
    for k in range(13):
        d = det[det.k == k]
        if d.empty: continue
        s = st[st.hour.isin(d.hour.unique())]
        for m in RAWM:
            dv, sv = d[m].dropna(), s[m].dropna()
            rows2.append(dict(stratum=name, k=k, measure=m, n_det=len(dv),
                              det_median=dv.median() if len(dv) else np.nan, det_mean=dv.mean() if len(dv) else np.nan,
                              n_stable=len(sv), stable_median=sv.median() if len(sv) else np.nan,
                              stable_mean=sv.mean() if len(sv) else np.nan))
traj2("overall", D2, S2)
for b in ["<50", "50-64", "65-79", ">=80"]:
    traj2(f"age {b}", D2[D2.age_band == b], S2[S2.age_band == b])
for g in ["<5", "5-8", "8-24", "24-72"]:
    traj2(f"anchor {g} h", D2[D2.tgroup == g], S2)
TR2 = pd.DataFrame(rows2); TR2.to_csv("DESCRIBE_TRAJ_RAW.csv", index=False)

bol = pd.read_csv("../missh_data/bolus_cal.csv")
stable_ids = set(anc[anc.target & (anc.cohort == "stable") & anc.open_h.notna()].stay_id)
det_set = set(T.stay_id)
RV = v.set_index(["stay_id", "hour_idx"])
ALMi = ALM.set_index(["stay_id", "hour"])
brows = []
for sid, g in bol.groupby("stay_id"):
    if sid in det_set:
        g = g[g.end_h < A.loc[sid, "anchor"]]
        if g.empty: continue
        grp = "det tipped <=6h after" if A.loc[sid, "anchor"] - g.sort_values("start_h").iloc[0].end_h <= 6 else "det tipped later"
    elif sid in stable_ids: grp = "stable"
    else: continue
    b0 = g.sort_values("start_h").iloc[0]; s0, e0 = int(np.floor(b0.start_h)), int(np.floor(b0.end_h))
    pre = {c: np.nanmean([RV[c].get((sid, h), np.nan) for h in (s0 - 2, s0 - 1)]) for c in ("hr", "map", "rr")}
    dws = SG[sid].set_index("hour").dw if sid in SG else pd.Series(dtype=float)
    for j in range(-2, 7):
        h = e0 + j
        al = ALMi.loc[(sid, h)] if (sid, h) in ALMi.index else None
        brows.append(dict(group=grp, j=j, **{f"d_{c}": RV[c].get((sid, h), np.nan) - pre[c] for c in ("hr", "map", "rr")},
                          dw=dws.get(h, np.nan),
                          alarm_main=al.alarm_main if al is not None else np.nan,
                          alarm_sens=al.alarm_sens if al is not None else np.nan))
BO = pd.DataFrame(brows)
BS = BO.groupby(["group", "j"]).agg(n=("d_map", "size"), d_map=("d_map", "median"), d_hr=("d_hr", "median"),
                                     d_rr=("d_rr", "median"), dw=("dw", "median"),
                                     alarm_main=("alarm_main", "mean"), alarm_sens=("alarm_sens", "mean")).reset_index()
BS.to_csv("DESCRIBE_BOLUS.csv", index=False)

L2 = ["", "State-space path, overall (median change from own hours 0-2; det | stable at same hours):"]
o = TR2[TR2.stratum == "overall"]
for m in ["d_hr", "d_map", "d_rr", "d_spo2"]:
    x = o[o.measure == m].sort_values("k", ascending=False)
    L2.append(f"   {m:7s} " + "  ".join(f"-{int(r.k)}h {r.det_median:+.1f}|{r.stable_median:+.1f}" for _, r in x.iterrows()))
L2.append("Alarm on, share by hour (det | stable):")
for m in ["alarm_main", "alarm_sens"]:
    x = o[o.measure == m].sort_values("k", ascending=False)
    L2.append(f"   {m:10s} " + "  ".join(f"-{int(r.k)}h {r.det_mean:.3f}|{r.stable_mean:.3f}" for _, r in x.iterrows()))
L2.append("Bolus-aligned (median change from before bolus; alarm share):")
for grp, x in BS.groupby("group"):
    L2.append(f"   [{grp}] n at +0h: {int(x[x.j == 0].n.sum()) if (x.j == 0).any() else 0}")
    for _, r in x.iterrows():
        L2.append(f"      {int(r.j):+d}h  MAP {r.d_map:+.1f}  HR {r.d_hr:+.1f}  RR {r.d_rr:+.1f}  Dw {r.dw:+.2f}  "
                  f"alarm main {r.alarm_main:.3f} sens {r.alarm_sens:.3f}")
open("DESCRIBE_80.txt", "a").write("\n".join(L2) + "\n")
print("\n".join(L2))

st1 = p1[p1.cohort == "stable"]
l95 = st1.groupby("hour").D_main.quantile(0.95); l99 = st1.groupby("hour").D_main.quantile(0.99)
k0 = M2[(M2.cohort == "det") & (M2.k == 0)].set_index("stay_id")
mover = pd.Series(np.where(k0.D_main > k0.hour.map(l99), "big",
                  np.where(k0.D_main > k0.hour.map(l95), "medium", "slow/compensating")), index=k0.index)
mover[k0.D_main.isna()] = "unknown"
C = M2[M2.cohort == "det"].pivot_table(index="stay_id", columns="k", values="cos")
def pattern(r):
    c = lambda k: r.get(k, np.nan)
    grad = sum(1 for k in (4, 3, 2) if np.isfinite(c(k)) and c(k) >= 0.3) >= 2
    late = np.isfinite(c(1)) and np.isfinite(c(0)) and c(1) <= 0.2 and c(0) >= 0.5
    return "gradual climb" if grad else ("late turn" if late else "other")
patt = C.apply(pattern, axis=1)
M2["mover"] = M2.stay_id.map(mover); M2["pattern"] = M2.stay_id.map(patt)
M["mover"] = M.stay_id.map(mover); M["pattern"] = M.stay_id.map(patt)
D2, DET = M2[M2.cohort == "det"], M[M.cohort == "det"]

rows, rows2 = [], []
for grp in ["slow/compensating", "medium", "big"]:
    traj(f"mover {grp}", DET[DET.mover == grp], ST); traj2(f"mover {grp}", D2[D2.mover == grp], S2)
for grp in ["late turn", "gradual climb", "other"]:
    traj(f"pattern {grp}", DET[DET.pattern == grp], ST); traj2(f"pattern {grp}", D2[D2.pattern == grp], S2)
pd.DataFrame(rows).to_csv("DESCRIBE_TRAJ_GROUPS.csv", index=False)
pd.DataFrame(rows2).to_csv("DESCRIBE_TRAJ_RAW_GROUPS.csv", index=False)

PER2 = PER.copy(); PER2["mover"] = PER2.sid.map(mover); PER2["pattern"] = PER2.sid.map(patt)
L3 = ["", "Groups by the architecture's own reading:",
      f"   mover: {PER2.mover.value_counts().to_dict()}",
      f"   pattern: {PER2.pattern.value_counts().to_dict()}",
      f"   mover x pattern:\n{pd.crosstab(PER2.mover, PER2.pattern).to_string()}",
      "Alarm outcome by group (share alarmed before anchor | never):"]
for col in ("mover", "pattern"):
    for grp, x in PER2.groupby(col):
        for n in ("main", "sens"):
            bef = (x[f"{n}_cat"].str.startswith("before")).mean(); nev = (x[f"{n}_cat"] == "never").mean()
            L3.append(f"   {col}={grp:20s} {n}: before {bef:.3f} | never {nev:.3f}  (n={len(x)}, median lead {x[f'{n}_lead'].median()})")
o = pd.DataFrame(rows2)
L3.append("Raw path by direction pattern (median change from own hours 0-2, det):")
for grp in ["late turn", "gradual climb"]:
    x = o[o.stratum == f"pattern {grp}"]
    for m in ["d_hr", "d_map", "d_rr"]:
        y = x[x.measure == m].sort_values("k", ascending=False)
        L3.append(f"   [{grp}] {m:6s} " + "  ".join(f"-{int(r.k)}h {r.det_median:+.1f}" for _, r in y.iterrows()))
open("DESCRIBE_80.txt", "a").write("\n".join(L3) + "\n")
print("\n".join(L3))

# Part 7: stable baseline for the gradual-climb pattern
SC = M2[M2.cohort == "stable"][["stay_id", "hour", "cos", "alarm_sens"]].sort_values(["stay_id", "hour"])
win, pats = 0, 0; hit, al = 0, 0
for sid, g in SC.groupby("stay_id"):
    c = g.set_index("hour").cos; a = g.set_index("hour").alarm_sens; found = False
    for h in c.index:
        w = [c.get(h + j, np.nan) for j in range(3)]
        if sum(np.isfinite(w)) < 2: continue
        win += 1
        if sum(1 for x in w if np.isfinite(x) and x >= 0.3) >= 2:
            hit += 1; found = True
            if any(a.get(h + j, 0) == 1 for j in range(3)): al += 1
    pats += found
n_st = SC.stay_id.nunique()
L4 = ["", "Stable baseline for gradual-climb pattern:",
      f"   stable patients ever showing it: {pats} of {n_st} ({pats / max(n_st, 1):.3f})",
      f"   3-h windows showing it: {hit} of {win} ({hit / max(win, 1):.4f}); "
      f"with sensitivity alarm on in the window: {al / max(hit, 1):.3f}"]
open("DESCRIBE_80.txt", "a").write("\n".join(L4) + "\n")
print("\n".join(L4))
