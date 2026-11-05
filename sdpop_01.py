# sdpop_01.py — SD_pop for REFERENCE_RULE.md (1d5e272)
# Typical detrended wobble of stable calibration patients, measured the same
# way as a ruler: clean 5-hour blocks, linear trend removed, residual SD.
# Input: missh.phi_hourly_cal export (phi_01.sql, 031935a). Outcome-blind.
import sys
import numpy as np
import pandas as pd

SRC = sys.argv[1] if len(sys.argv) > 1 else "../missh_data/phi_hourly_cal.csv"
OUT = "SD_POP.txt"
CHANNELS = ["hr", "map", "rr", "spo2"]
BLOCK = 5

df = pd.read_csv(SRC)
df["blocked"] = df["blocked"].astype(str).str.lower().eq("true")
df = df.sort_values(["stay_id", "hour_idx"])

def runs(hours, vals, ok):
    out, cur, last = [], [], None
    for h, v, k in zip(hours, vals, ok):
        if k and cur and h == last + 1:
            cur.append(v)
        else:
            if len(cur) >= BLOCK:
                out.append(cur)
            cur = [v] if k else []
        last = h
    if len(cur) >= BLOCK:
        out.append(cur)
    return out

def resid_sd(x):
    x = np.asarray(x, float)
    t = np.arange(len(x))
    r = x - np.polyval(np.polyfit(t, x, 1), t)
    return float(np.sqrt(np.sum(r * r) / (len(x) - 2)))

rows = []
for stay, g in df.groupby("stay_id"):
    for ch in CHANNELS:
        ok = (~g["blocked"]) & g[ch].notna()
        for run in runs(g["hour_idx"].tolist(), g[ch].tolist(), ok.tolist()):
            for i in range(0, len(run) - BLOCK + 1, BLOCK):
                rows.append({"stay_id": stay, "channel": ch,
                             "sd": resid_sd(run[i:i + BLOCK])})

b = pd.DataFrame(rows)
lines = ["SD_POP — sdpop_01.py on phi_hourly_cal (031935a), 5h clean blocks",
         f"stable calibration stays: {df['stay_id'].nunique()}", ""]
for ch in CHANNELS:
    c = b[b["channel"] == ch]
    per_pt = c.groupby("stay_id")["sd"].median()
    lines.append(f"[{ch.upper()}] patients={len(per_pt)} blocks={len(c)}  "
                 f"SD_pop (median of patient medians) = {per_pt.median():.3f}  "
                 f"p10={per_pt.quantile(.1):.3f}  p90={per_pt.quantile(.9):.3f}")
text = "\n".join(lines)
print(text)
open(OUT, "w").write(text + "\n")
