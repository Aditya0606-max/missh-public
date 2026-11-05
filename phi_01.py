# phi_01.py — lag-1 autocorrelation (phi) of detrended clean stretches
# Implements PHI_PROTOCOL.md (9ea7371) + PHI_TREATMENT_ADDENDUM.md on
# missh.phi_hourly_cal (built by phi_01.sql, 031935a). Outcome-blind.
import sys
import numpy as np
import pandas as pd

SRC = sys.argv[1] if len(sys.argv) > 1 else "../missh_data/phi_hourly_cal.csv"
OUT_STRETCH = "../missh_data/phi_stretches.csv"
OUT_SUMMARY = "PHI_RESULTS.txt"
CHANNELS = ["hr", "map", "rr", "spo2"]
MIN_LEN = 8

df = pd.read_csv(SRC)
df["blocked"] = df["blocked"].astype(str).str.lower().eq("true")
df = df.sort_values(["stay_id", "hour_idx"])

def runs(hours, vals, ok):
    out, cur, last = [], [], None
    for h, v, k in zip(hours, vals, ok):
        if k and cur and h == last + 1:
            cur.append(v)
        else:
            if len(cur) >= MIN_LEN:
                out.append(cur)
            cur = [v] if k else []
        last = h
    if len(cur) >= MIN_LEN:
        out.append(cur)
    return out

def phi(x):
    x = np.asarray(x, float)
    t = np.arange(len(x))
    r = x - np.polyval(np.polyfit(t, x, 1), t)
    d = np.sum(r * r)
    if d == 0:
        return np.nan
    return float(np.sum(r[:-1] * r[1:]) / d)

rows = []
for stay, g in df.groupby("stay_id"):
    for ch in CHANNELS:
        ok = (~g["blocked"]) & g[ch].notna()
        for s in runs(g["hour_idx"].tolist(), g[ch].tolist(), ok.tolist()):
            rows.append({"stay_id": stay, "channel": ch,
                         "length": len(s), "phi": phi(s)})

st = pd.DataFrame(rows)
st.to_csv(OUT_STRETCH, index=False)

def pct(s):
    s = s.dropna()
    if len(s) == 0:
        return "n=0"
    return (f"n={len(s)}  p10={s.quantile(.1):.3f}  "
            f"median={s.median():.3f}  p90={s.quantile(.9):.3f}")

lines = ["PHI_RESULTS — phi_01.py on phi_hourly_cal (031935a)",
         f"stable calibration stays: {df['stay_id'].nunique()}", ""]
for ch in CHANNELS:
    c = st[st["channel"] == ch]
    flat = int(c["phi"].isna().sum())
    per_patient = c.groupby("stay_id")["phi"].median()
    lines.append(f"[{ch.upper()}]")
    lines.append(f"  patients with >=1 stretch: {c['stay_id'].nunique()}"
                 f"   stretches: {len(c)}   flat (no variation): {flat}")
    lines.append(f"  stretch-level   {pct(c['phi'])}")
    lines.append(f"  patient-level   {pct(per_patient)}")
    for lo, hi, lab in [(8, 11, "8-11h"), (12, 15, "12-15h"), (16, 10**6, "16h+")]:
        b = c[(c["length"] >= lo) & (c["length"] <= hi)]
        lines.append(f"  length {lab:7s} {pct(b['phi'])}")
    lines.append("")

text = "\n".join(lines)
print(text)
open(OUT_SUMMARY, "w").write(text + "\n")
