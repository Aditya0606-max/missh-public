# measure_pp.py — E8: pulse pressure and effort at det lookbacks and every stable hour.
import numpy as np
import pandas as pd

bp = pd.read_csv("../missh_data/bp_hourly_cal.csv")
v = pd.read_csv("../missh_data/vitals_hourly_cal_v2.csv")
for c in ["block_bolus", "block_iv", "sed_infusion"]:
    v[c] = v[c].astype(str).str.lower().eq("true")
v["blocked"] = v.block_bolus | v.block_iv | v.sed_infusion
v = v.merge(bp, on=["stay_id", "hour_idx"], how="left")
v["pp"] = v.sbp - v.dbp
anc = pd.read_csv("../missh_data/anchors_cal_v2.csv")
news = pd.read_csv("../missh_data/news_hourly_cal.csv").set_index(["stay_id", "hour_idx"])
SHR, SMAP = 3.706, 5.975

D = {}
for sid, g in v[~v.blocked].groupby("stay_id"):
    D[sid] = {int(r.hour_idx): (r.hr, r["map"], r.pp, r.art_share) for _, r in g.iterrows()}

def val(d, h, j, back=1):
    for hh in range(h, h - back - 1, -1):
        if hh in d and np.isfinite(d[hh][j]):
            return d[hh][j], hh
    return np.nan, None

def feats(sid, h):
    d = D.get(sid, {})
    out = {}
    base = [d[x][2] for x in (0, 1, 2) if x in d and np.isfinite(d[x][2])]
    pp_now, hn = val(d, h, 2)
    out["pp_rel"] = pp_now - np.mean(base) if base and np.isfinite(pp_now) else np.nan
    out["pp_rel_abs"] = abs(out["pp_rel"]) if np.isfinite(out["pp_rel"]) else np.nan
    for j, name in ((2, "dpp4"), (0, "dhr4"), (1, "dmap4")):
        now, _ = val(d, h, j)
        then, _ = val(d, h - 4, j)
        out[name] = now - then if np.isfinite(now) and np.isfinite(then) else np.nan
    out["effort"] = (out["dhr4"] / SHR - abs(out["dmap4"]) / SMAP
                     if np.isfinite(out["dhr4"]) and np.isfinite(out["dmap4"]) else np.nan)
    out["art"] = d[hn][3] if hn is not None else np.nan
    nw = news.loc[(sid, h)] if (sid, h) in news.index else None
    out["news"] = float(nw.news) if nw is not None else np.nan
    out["news_items"] = float(nw.n_items) if nw is not None else np.nan
    return out

rows = []
T = anc[anc.target & anc.open_h.notna()]
for _, a in T[T.cohort == "deteriorating"].iterrows():
    for k in (0, 1, 2, 4):
        if pd.isna(a.anchor):
            continue
        h = int(np.floor(a.anchor - k)) - 1
        if h >= a.open_h:
            rows.append(dict(stay_id=a.stay_id, cohort="det", k=k, hour=h, tier=a.ptier,
                             anchor_type=str(a.anchor_type), dni=bool(a.dni_before), **feats(a.stay_id, h)))
for _, a in T[T.cohort == "stable"].iterrows():
    for h in range(int(a.open_h), 72):
        rows.append(dict(stay_id=a.stay_id, cohort="stable", k=np.nan, hour=h, tier=a.ptier,
                         anchor_type="", dni=False, **feats(a.stay_id, h)))
M = pd.DataFrame(rows)
M.to_csv("../missh_data/measures_pp.csv", index=False)
cols = ["pp_rel", "pp_rel_abs", "dpp4", "dhr4", "dmap4", "effort"]
print("MEASURE_PP built; det per k:", M[M.cohort == "det"].groupby("k").stay_id.nunique().to_dict())
print("non-missing:", M[cols].notna().mean().round(3).to_dict())
print("median arterial share (rows with pp):", round(M.art.median(), 2))
