# calibrate_01.py — evaluate the flag grid and choose by CALIBRATION_RULE.md
import json
import numpy as np
import pandas as pd

S = pd.read_csv("../missh_data/series_dw.csv")
ST = S[S.cohort == "stable"]
QS, PS = (0.90, 0.95, 0.975, 0.99), (1, 2, 3, 4)
lines = {q: ST.groupby("hour").dw.quantile(q) for q in QS}

def fire_time(g, q, p):
    c = 0
    for _, r in g.iterrows():
        if np.isnan(r.dw):
            continue
        L = lines[q].get(r.hour, np.nan)
        if np.isnan(L):
            continue
        c = c + 1 if r.dw > L else max(0, c - 1)
        if c >= p:
            return r.hour + 1
    return np.nan

G = {sid: g.sort_values("hour") for sid, g in S.groupby("stay_id")}
coh = S.groupby("stay_id").cohort.first(); anc = S.groupby("stay_id").anchor.first()
res = []
for q in QS:
    for p in PS:
        ft = pd.Series({sid: fire_time(g, q, p) for sid, g in G.items()})
        st, dt = ft[coh == "stable"], ft[coh == "deteriorating"]
        lead = anc[dt.index] - dt
        days = ST.groupby("stay_id").hour.count().sum() / 24
        res.append(dict(q=q, p=p, stable_ever=st.notna().mean(),
                        stable_per_day=st.notna().sum() / days,
                        det_ge1h=(lead >= 1).mean(), det_ge2h=(lead >= 2).mean(),
                        median_lead=lead[lead >= 1].median()))
R = pd.DataFrame(res)
ok = R[R.stable_ever <= 0.10]
pick = (ok.sort_values(["det_ge1h", "p", "q"], ascending=False).iloc[0] if len(ok)
        else R.sort_values("stable_ever").iloc[0])
L = ["CALIBRATION — flag grid (calibration split), rule CALIBRATION_RULE.md", R.round(3).to_string(), "",
     f"CHOSEN: q={pick.q}, p={int(pick.p)}  stable_ever={pick.stable_ever:.3f}  "
     f"det >=1h={pick.det_ge1h:.3f}  >=2h={pick.det_ge2h:.3f}  median lead={pick.median_lead}"]
text = "\n".join(L); print(text); open("CALIBRATION.txt", "w").write(text + "\n")
json.dump({"q": float(pick.q), "p": int(pick.p),
           "lines": {int(h): float(v) for h, v in lines[pick.q].items()}},
          open("FLAG_FROZEN.json", "w"), indent=1)
