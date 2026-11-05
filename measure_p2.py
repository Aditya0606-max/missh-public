# measure_p2.py — part 2a: path measures (consistency, straightness, speed,
# bend with rate, counter, hours since return). Step-based, SD_pop scaling,
# clean = not blocked (A14). Det lookbacks k = 0,1,2,4,6; stable every hour.
import numpy as np
import pandas as pd

CH = ["hr", "map", "rr", "spo2"]
SDPOP = np.array([3.706, 5.975, 2.608, 1.211])
W = np.array([1.0, -1.0, 1.0, -1.0])
LOOK = (0, 1, 2, 4, 6)

v = pd.read_csv("../missh_data/vitals_hourly_cal_v2.csv")
for c in ["block_bolus", "block_iv", "sed_infusion"]:
    v[c] = v[c].astype(str).str.lower().eq("true")
v["blocked"] = v.block_bolus | v.block_iv | v.sed_infusion
anc = pd.read_csv("../missh_data/anchors_cal_v2.csv")
news = pd.read_csv("../missh_data/news_hourly_cal.csv").set_index(["stay_id", "hour_idx"])

C = {}
for sid, g in v.groupby("stay_id"):
    d = {}
    for _, r in g.iterrows():
        x = np.array([r[c] for c in CH], float)
        if not r.blocked and (~np.isnan(x)).sum() >= 2:
            d[int(r.hour_idx)] = x / SDPOP
    C[sid] = d

def snorm(a):
    m = ~np.isnan(a)
    return np.nan if m.sum() < 2 else float(np.sqrt(4.0 / m.sum() * np.sum(a[m] ** 2)))

def cosw(a):
    m = ~np.isnan(a)
    if m.sum() < 2:
        return np.nan
    na = np.linalg.norm(a[m])
    return np.nan if na == 0 else float(a[m] @ W[m] / (na * np.linalg.norm(W[m])))

def counter_series(sid, open_h):
    c, last_ret, out = 0, open_h, {}
    d = C.get(sid, {})
    for h in range(int(open_h), 72):
        if h in d and (h - 1) in d:
            a = d[h] - d[h - 1]
            L, cs = snorm(a), cosw(a)
            if not np.isnan(L) and not np.isnan(cs) and L >= 1:
                if cs > 0:
                    c += 1
                elif cs < 0:
                    c = max(0, c - 1)
                    last_ret = h
        out[h] = (c, h - last_ret)
    return out

def path(sid, h, cser):
    d = C.get(sid, {})
    out = {}
    cos_list = [cosw(d[hh] - d[hh - 1]) for hh in range(h - 3, h + 1) if hh in d and (hh - 1) in d]
    cos_list = [x for x in cos_list if not np.isnan(x)]
    out["consist"] = float(np.mean([x > 0 for x in cos_list])) if len(cos_list) >= 2 else np.nan
    hs = [hh for hh in range(h - 4, h + 1) if hh in d]
    if len(hs) >= 3:
        net = snorm(d[hs[-1]] - d[hs[0]])
        pl = sum(snorm(d[hs[i]] - d[hs[i - 1]]) for i in range(1, len(hs)))
        out["straight"] = net / pl if pl and pl > 0 else np.nan
        out["speed"] = net / (hs[-1] - hs[0])
    else:
        out["straight"] = out["speed"] = np.nan
    if all(x in d for x in (h, h - 1, h - 2)):
        a1, a2 = d[h - 1] - d[h - 2], d[h] - d[h - 1]
        c1, c2 = cosw(a1), cosw(a2)
        out["bend"] = (c2 - c1) * snorm(a2) if not (np.isnan(c1) or np.isnan(c2)) else np.nan
    else:
        out["bend"] = np.nan
    cv = cser.get(h)
    out["counter"], out["since_ret"] = (cv if cv else (np.nan, np.nan))
    nw = news.loc[(sid, h)] if (sid, h) in news.index else None
    out["news"] = float(nw.news) if nw is not None else np.nan
    out["news_items"] = float(nw.n_items) if nw is not None else np.nan
    return out

rows = []
T = anc[anc.target & anc.open_h.notna()]
for _, a in T[T.cohort == "deteriorating"].iterrows():
    cser = counter_series(a.stay_id, a.open_h)
    for k in LOOK:
        if pd.isna(a.anchor):
            continue
        h = int(np.floor(a.anchor - k)) - 1
        if h < a.open_h:
            continue
        rows.append(dict(stay_id=a.stay_id, cohort="det", k=k, hour=h, tier=a.ptier,
                         anchor_type=str(a.anchor_type), dni=bool(a.dni_before), **path(a.stay_id, h, cser)))
for _, a in T[T.cohort == "stable"].iterrows():
    cser = counter_series(a.stay_id, a.open_h)
    for h in range(int(a.open_h), 72):
        if True:
            rows.append(dict(stay_id=a.stay_id, cohort="stable", k=np.nan, hour=h, tier=a.ptier,
                             anchor_type="", dni=False, **path(a.stay_id, h, cser)))

M = pd.DataFrame(rows)
M.to_csv("../missh_data/measures_p2.csv", index=False)
d = M[M.cohort == "det"]
print("MEASURE_P2 table built")
print(d.groupby("k").stay_id.nunique().rename("det patients per lookback").to_string())
print(f"stable rows {int((M.cohort=='stable').sum())}  patients {M[M.cohort=='stable'].stay_id.nunique()}")
print("non-missing share:", M[["consist", "straight", "speed", "bend", "counter", "since_ret"]].notna().mean().round(3).to_dict())
