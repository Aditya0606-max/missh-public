# bolus_01.py — E12: how long does a bolus lift MAP, stable vs deteriorating?
import numpy as np
import pandas as pd

b = pd.read_csv("../missh_data/bolus_cal.csv")
v = pd.read_csv("../missh_data/vitals_hourly_cal.csv")
anc = pd.read_csv("../missh_data/anchors_cal_v2.csv")
MAP = v.set_index(["stay_id", "hour_idx"])["map"]
HR = v.set_index(["stay_id", "hour_idx"])["hr"]
T = anc[anc.target & anc.cohort.isin(["deteriorating", "stable"])].set_index("stay_id")

rows = []
for sid, g in b.groupby("stay_id"):
    if sid not in T.index:
        continue
    a = T.loc[sid]
    g = g.sort_values("start_h")
    if a.cohort == "deteriorating":
        g = g[g.end_h < a.anchor]
    if g.empty:
        continue
    bo = g.iloc[0]
    s, e = int(np.floor(bo.start_h)), int(np.floor(bo.end_h))
    pre = [MAP.get((sid, h), np.nan) for h in (s - 2, s - 1)]
    pre = np.nanmean(pre) if np.isfinite(pre).any() else np.nan
    post = [MAP.get((sid, e + k), np.nan) for k in range(0, 7)]
    hrpre = np.nanmean([HR.get((sid, h), np.nan) for h in (s - 2, s - 1)])
    hrpost = [HR.get((sid, e + k), np.nan) for k in range(0, 7)]
    if not np.isfinite(pre) or not np.isfinite(post[:3]).any():
        continue
    peak_i = int(np.nanargmax(post[:3])); lift = post[peak_i] - pre
    wear = np.nan
    for k in range(peak_i + 1, 7):
        if np.isfinite(post[k]) and post[k] <= pre:
            wear = k; break
    to_anchor = a.anchor - (bo.end_h) if a.cohort == "deteriorating" else np.nan
    rows.append(dict(sid=sid, cohort=a.cohort, start_h=bo.start_h, pre=pre, lift=lift, wear=wear,
                     to_anchor=to_anchor, hr_pre=hrpre,
                     **{f"map_{k}": post[k] - pre for k in range(7)},
                     **{f"hr_{k}": hrpost[k] - hrpre if np.isfinite(hrpre) else np.nan for k in range(7)}))
R = pd.DataFrame(rows)
L = ["BOLUS_RESPONSE — E12 (calibration, descriptive)", ""]
for c in ("stable", "deteriorating"):
    d = R[R.cohort == c]
    L.append(f"[{c}] patients with a first bolus: {len(d)}")
    L.append(f"   MAP before: median {d.pre.median():.1f}   lift: median {d.lift.median():.1f} mmHg")
    L.append(f"   MAP change vs before, by hour after bolus end (median): " +
             "  ".join(f"+{k}h {d[f'map_{k}'].median():+.1f}" for k in range(7)))
    L.append(f"   HR change vs before, by hour (median): " +
             "  ".join(f"+{k}h {d[f'hr_{k}'].median():+.1f}" for k in range(7)))
    L.append(f"   lift worn off within 6 h: {d.wear.notna().mean():.3f}   median hours to wear-off {d.wear.median()}")
    if c == "deteriorating":
        L.append(f"   hours from bolus end to anchor: median {d.to_anchor.median():.1f}  IQR "
                 f"{d.to_anchor.quantile(.25):.1f}-{d.to_anchor.quantile(.75):.1f}")
        w = d.dropna(subset=["wear"])
        L.append(f"   anchor after wear-off: {(w.to_anchor > w.wear).mean():.3f} of those whose lift wore off "
                 f"(n={len(w)})")
    L.append("")
text = "\n".join(L); print(text); open("BOLUS_RESPONSE.txt", "w").write(text + "\n")
