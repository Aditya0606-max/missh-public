# measure_p1.py — part 1a: D and D_w from main ruler, arms h2/h5/h8 and
# origin, at lookbacks (det) and every hour (stable). Saves a table only.
# REFERENCE_RULE + A13-A15; PRIMARY_COMPARISON (directed distance, origin).
import numpy as np
import pandas as pd

CH = ["hr", "map", "rr", "spo2"]
SDPOP = np.array([3.706, 5.975, 2.608, 1.211])
W = np.array([1.0, -1.0, 1.0, -1.0]) / 2.0
LOOK = (1, 2, 4, 6)

v = pd.read_csv("../missh_data/vitals_hourly_cal_v2.csv")
for c in ["block_bolus", "block_iv", "sed_infusion"]:
    v[c] = v[c].astype(str).str.lower().eq("true")
v["blocked"] = v.block_bolus | v.block_iv | v.sed_infusion
rul = pd.read_csv("../missh_data/rulers_cal_v3.csv")
anc = pd.read_csv("../missh_data/anchors_cal_v2.csv")
news = pd.read_csv("../missh_data/news_hourly_cal.csv").set_index(["stay_id", "hour_idx"])

VAL, BLK = {}, {}
for sid, g in v.groupby("stay_id"):
    g = g.set_index("hour_idx")
    VAL[sid] = {int(h): g.loc[h, CH].values.astype(float) for h in g.index}
    BLK[sid] = set(int(h) for h in g.index[g.blocked])

RUL = {}
for (sid, arm), g in rul.groupby(["stay_id", "arm"]):
    g = g.set_index("channel")
    cen = np.array([g.centre.get(c, np.nan) for c in CH], float)
    sdu = np.array([g.sd_used.get(c, np.nan) for c in CH], float)
    tier = g.tier.iloc[0]
    close = float(np.nanmax(g.close_h.values)) if g.close_h.notna().any() else np.nan
    RUL[(sid, arm)] = (cen, sdu, tier, close)

def state(sid, h):
    for hh in (h, h - 1, h - 2):
        x = VAL.get(sid, {}).get(hh)
        if x is not None and hh not in BLK.get(sid, set()) and (~np.isnan(x)).sum() >= 2:
            return x
    return None

def dist(x, cen, sdu):
    z = (x - cen) / sdu
    m = ~np.isnan(z)
    if m.sum() < 2:
        return np.nan, np.nan
    D = float(np.sqrt(4.0 / m.sum() * np.sum(z[m] ** 2)))
    nz = np.linalg.norm(z[m])
    cos = float(z[m] @ W[m] / (nz * np.linalg.norm(W[m]))) if nz > 0 else 0.0
    return D, D * cos

ORIG = {}
for sid, vals in VAL.items():
    hs = sorted(vals)
    clean = [h for h in hs if h not in BLK[sid] and (~np.isnan(vals[h])).sum() >= 2]
    anyp = [h for h in hs if (~np.isnan(vals[h])).sum() >= 2]
    if clean:
        ORIG[sid] = (clean[0], vals[clean[0]], False)
    elif anyp:
        ORIG[sid] = (anyp[0], vals[anyp[0]], True)


def dw_main(sid, h):
    x = state(sid, h)
    if x is None:
        return np.nan
    main = RUL.get((sid, "main"))
    if not main:
        return np.nan
    tier = main[2]
    if tier in ("A", "B") and h < 3 and (sid, "prov2") in RUL:
        cen, sdu = RUL[(sid, "prov2")][:2]
    elif tier in ("A", "B") or (pd.notna(main[3]) and h >= main[3]):
        cen, sdu = main[:2]
    else:
        return np.nan
    return dist(x, cen, sdu)[1]

rows = []
T = anc[anc.target & anc.open_h.notna()]
for _, a in T.iterrows():
    if a.cohort == "deteriorating" and pd.notna(a.anchor):
        last = int(np.floor(a.anchor)) - 1
    elif a.cohort == "stable":
        last = 71
    else:
        continue
    for h in range(int(a.open_h), last + 1):
        rows.append((a.stay_id, a.cohort, h, a.anchor if a.cohort == "deteriorating" else np.nan,
                     dw_main(a.stay_id, h)))
S = pd.DataFrame(rows, columns=["stay_id", "cohort", "hour", "anchor", "dw"])
S.to_csv("../missh_data/series_dw.csv", index=False)
print("series built:", S.groupby("cohort").stay_id.nunique().to_dict(), "rows", len(S))
