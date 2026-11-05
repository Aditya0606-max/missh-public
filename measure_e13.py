# measure_e13.py — E13 compensation panel: stickiness, degrees of freedom,
# variability, RR trend, RR-MAP cosine, shock index, DBP trend.
import numpy as np
import pandas as pd

SDP = {"hr": 3.706, "map": 5.975, "rr": 2.608}
v = pd.read_csv("../missh_data/vitals_hourly_cal_v2.csv")
for c in ["block_bolus", "block_iv", "sed_infusion"]:
    v[c] = v[c].astype(str).str.lower().eq("true")
v["blocked"] = v.block_bolus | v.block_iv | v.sed_infusion
bp = pd.read_csv("../missh_data/bp_hourly_cal.csv")
v = v.merge(bp[["stay_id", "hour_idx", "sbp", "dbp"]], on=["stay_id", "hour_idx"], how="left")
anc = pd.read_csv("../missh_data/anchors_cal_v2.csv")
news = pd.read_csv("../missh_data/news_hourly_cal.csv").set_index(["stay_id", "hour_idx"])
COLS = ["hr", "map", "rr", "sbp", "dbp"]
D = {}
for sid, g in v[~v.blocked].groupby("stay_id"):
    D[sid] = {int(r.hour_idx): np.array([r[c] for c in COLS], float) for _, r in g.iterrows()}

def lag1(hs, x):
    hs, x = np.asarray(hs, float), np.asarray(x, float)
    m = np.isfinite(x)
    if m.sum() < 5: return np.nan
    res = x[m] - np.polyval(np.polyfit(hs[m], x[m], 1), hs[m])
    hh = hs[m]; prs = [(res[i - 1], res[i]) for i in range(1, len(hh)) if hh[i] - hh[i - 1] == 1]
    if len(prs) < 4: return np.nan
    a = np.array(prs)
    if a[:, 0].std() == 0 or a[:, 1].std() == 0: return np.nan
    return float(np.corrcoef(a[:, 0], a[:, 1])[0, 1])

def slope(hs, x):
    hs, x = np.asarray(hs, float), np.asarray(x, float); m = np.isfinite(x)
    return float(np.polyfit(hs[m], x[m], 1)[0]) if m.sum() >= 4 else np.nan

def panel(sid, h):
    d = D.get(sid, {}); hs = [x for x in range(h - 7, h + 1) if x in d]
    out = dict.fromkeys(["stick", "stick_hr", "stick_map", "dof", "sd_hr", "sd_map", "rr_slope",
                         "rrmap_cos", "si", "si_slope", "dbp_slope"], np.nan)
    if len(hs) < 6: return out
    X = np.array([d[x] for x in hs])
    out["stick_hr"], out["stick_map"] = lag1(hs, X[:, 0]), lag1(hs, X[:, 1])
    out["stick"] = np.nanmean([out["stick_hr"], out["stick_map"]]) if np.isfinite([out["stick_hr"], out["stick_map"]]).any() else np.nan
    st = [(d[x][:3] - d[x - 1][:3]) / np.array([SDP["hr"], SDP["map"], SDP["rr"]]) for x in hs if x - 1 in d]
    st = np.array([s for s in st if np.isfinite(s).all()])
    if len(st) >= 4:
        lam = np.clip(np.linalg.eigvalsh(np.cov(st.T)), 0, None)
        out["dof"] = float(lam.sum() ** 2 / (lam ** 2).sum()) if (lam ** 2).sum() > 0 else np.nan
        out["sd_hr"], out["sd_map"] = float(st[:, 0].std() * SDP["hr"]), float(st[:, 1].std() * SDP["map"])
    out["rr_slope"] = slope(hs, X[:, 2])
    f = [i for i in range(len(hs)) if np.isfinite(X[i, 1]) and np.isfinite(X[i, 2])]
    if len(f) >= 2:
        net = np.array([(X[f[-1], 2] - X[f[0], 2]) / SDP["rr"], (X[f[-1], 1] - X[f[0], 1]) / SDP["map"]])
        n = np.linalg.norm(net)
        out["rrmap_cos"] = float(net @ np.array([1, -1]) / (n * np.sqrt(2))) if n > 0 else 0.0
    si = X[:, 0] / X[:, 3]
    if h in d and np.isfinite(d[h][0]) and np.isfinite(d[h][3]) and d[h][3] > 0: out["si"] = d[h][0] / d[h][3]
    out["si_slope"] = slope(hs, si); out["dbp_slope"] = slope(hs, X[:, 4])
    return out

def nw(sid, h):
    r = news.loc[(sid, h)] if (sid, h) in news.index else None
    return (float(r.news), float(r.n_items)) if r is not None else (np.nan, np.nan)

rows = []
T = anc[anc.target & anc.open_h.notna()]
for _, a in T[T.cohort == "deteriorating"].iterrows():
    for k in (0, 2, 4, 6):
        if pd.isna(a.anchor): continue
        h = int(np.floor(a.anchor - k)) - 1
        if h >= a.open_h:
            n1, n2 = nw(a.stay_id, h)
            rows.append(dict(stay_id=a.stay_id, cohort="det", k=k, hour=h, tier=a.ptier, anchor_type=str(a.anchor_type),
                             dni=bool(a.dni_before), news=n1, news_items=n2, **panel(a.stay_id, h)))
for _, a in T[T.cohort == "stable"].iterrows():
    for h in range(int(a.open_h), 72):
        n1, n2 = nw(a.stay_id, h)
        rows.append(dict(stay_id=a.stay_id, cohort="stable", k=np.nan, hour=h, tier=a.ptier, anchor_type="",
                         dni=False, news=n1, news_items=n2, **panel(a.stay_id, h)))
M = pd.DataFrame(rows)
p1 = pd.read_csv("../missh_data/measures_p1.csv", low_memory=False)[["stay_id", "cohort", "k", "hour", "D_main"]]
p0 = pd.read_csv("../missh_data/measures_p1_k0.csv", low_memory=False)[["stay_id", "cohort", "k", "hour", "D_main"]]
p0 = p0[p0.cohort == "det"]
P = pd.concat([p1, p0]); P["kk"] = P.k.fillna(-1); M["kk"] = M.k.fillna(-1)
M = M.merge(P[["stay_id", "cohort", "kk", "hour", "D_main"]].drop_duplicates(), on=["stay_id", "cohort", "kk", "hour"], how="left")
ST = M[M.cohort == "stable"]
med_D = ST.groupby("hour").D_main.median(); q75 = ST.groupby("hour").stick.quantile(0.75); q25 = ST.groupby("hour").dof.quantile(0.25)
M["pinned"] = ((M.D_main <= M.hour.map(med_D)) & (M.stick >= M.hour.map(q75)) &
               (M.dof <= M.hour.map(q25)) & (M.rr_slope >= 0.5)).astype(float)
M.loc[M[["D_main", "stick", "dof", "rr_slope"]].isna().any(axis=1), "pinned"] = np.nan
M.drop(columns="kk").to_csv("../missh_data/measures_e13.csv", index=False)
cols = ["stick", "dof", "sd_hr", "sd_map", "rr_slope", "rrmap_cos", "si", "si_slope", "dbp_slope", "pinned"]
print("E13 built; det per k:", M[M.cohort == "det"].groupby("k").stay_id.nunique().to_dict())
print("non-missing:", M[cols].notna().mean().round(3).to_dict())
d = M[M.cohort == "det"]
print("pinned share — stable per hour:", round(ST.assign(p=M.pinned)[ "p"].mean() if False else M[M.cohort=='stable'].pinned.mean(), 4),
      " det by k:", d.groupby("k").pinned.mean().round(4).to_dict())
