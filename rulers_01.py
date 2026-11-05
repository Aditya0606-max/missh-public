# rulers_01.py — every calibration patient's ruler and tier.
# REFERENCE_RULE.md (1d5e272) + A13 (4628ccf). No outcome labels used.
# SD_pop from SD_POP.txt (56dbe50), confirmed unchanged by A10.
# Implementation details fixed here before running:
#  - clean hour (per channel) = value present, not blocked, not sedated
#  - main: hours 0-4; A = 5 clean, B = 4 clean; frozen at hour 5
#  - delayed (A13): first 5 clean hours within hours 0-11; frozen after 5th
#  - centre = mean of clean values; SD_own = residual SD after linear fit
#    on hour index (n-2 in denominator); needs >= 3 points
#  - blend: SD^2 = (n_eff*SD_own^2 + 2*SD_pop^2)/(n_eff + 2),
#    n_eff = n*(1-0.35)/(1+0.35); SD_used = max(SD, 1.0 device floor)
#  - arm h2: hours 0-1, >= 1 clean; SD_used = max(SD_pop, 1.0) (n too small)
#  - arm h8: hours 0-7, >= 6 clean; SD_used = max(SD_own, 1.0), no blend
import numpy as np
import pandas as pd

CH = ["hr", "map", "rr", "spo2"]
SDPOP = {"hr": 3.706, "map": 5.975, "rr": 2.608, "spo2": 1.211}
PHI, FLOOR = 0.35, 1.0
NEFF = (1 - PHI) / (1 + PHI)
OUT_CSV = "../missh_data/rulers_cal.csv"
OUT_TXT = "RULER_COUNTS.txt"

df = pd.read_csv("../missh_data/vitals_hourly_cal.csv")
for c in ["blocked", "sedated"]:
    df[c] = df[c].astype(str).str.lower().eq("true")
df = df.sort_values(["stay_id", "hour_idx"])

def sd_own(h, v):
    if len(v) < 3:
        return np.nan
    h, v = np.asarray(h, float), np.asarray(v, float)
    r = v - np.polyval(np.polyfit(h, v, 1), h)
    return float(np.sqrt(np.sum(r * r) / (len(v) - 2)))

def blended(h, v, ch):
    so = sd_own(h, v)
    ne = len(v) * NEFF
    if np.isnan(so):
        sd = SDPOP[ch]
    else:
        sd = np.sqrt((ne * so ** 2 + 2 * SDPOP[ch] ** 2) / (ne + 2))
    return so, max(sd, FLOOR)

rows = []
for sid, g in df.groupby("stay_id"):
    g = g.set_index("hour_idx")
    for ch in CH:
        ok = g[ch].notna() & ~g.blocked & ~g.sedated
        clean = list(g.index[ok])
        c04 = [h for h in clean if h <= 4]
        if len(c04) >= 4:
            tier = "A" if len(c04) == 5 else "B"
            hs, close = c04, 5
        else:
            c11 = [h for h in clean if h <= 11][:5]
            if len(c11) == 5:
                tier, hs, close = "Cdelayed", c11, c11[-1] + 1
            else:
                tier, hs, close = "none", [], np.nan
        if hs:
            v = g.loc[hs, ch].values
            so, su = blended(hs, v, ch)
            rows.append((sid, "main", ch, tier, len(hs), float(np.mean(v)), so, su, close))
        else:
            rows.append((sid, "main", ch, "none", 0, np.nan, np.nan, np.nan, np.nan))
        c01 = [h for h in clean if h <= 1]
        if c01:
            v = g.loc[c01, ch].values
            rows.append((sid, "h2", ch, "arm", len(c01), float(np.mean(v)), np.nan,
                         max(SDPOP[ch], FLOOR), 2))
        c07 = [h for h in clean if h <= 7]
        if len(c07) >= 6:
            v = g.loc[c07, ch].values
            so = sd_own(c07, v)
            rows.append((sid, "h8", ch, "arm", len(c07), float(np.mean(v)), so,
                         max(so, FLOOR), 8))

R = pd.DataFrame(rows, columns=["stay_id", "arm", "channel", "tier", "n_clean",
                                "centre", "sd_own", "sd_used", "close_h"])
R.to_csv(OUT_CSV, index=False)

M = R[R.arm == "main"].pivot(index="stay_id", columns="channel", values="tier")
def ptier(r):
    if all(r[c] == "A" for c in CH):
        return "A"
    if r["hr"] in ("A", "B") and r["map"] in ("A", "B"):
        return "B"
    if r["hr"] != "none" and r["map"] != "none":
        return "Cdelayed"
    return "Cdirection"
PT = M.apply(ptier, axis=1)
PT.rename("ptier").to_csv("../missh_data/patient_tiers_cal.csv")

L = ["RULER_COUNTS — rulers_01.py (REFERENCE_RULE + A13), calibration, no outcomes",
     f"patients: {R.stay_id.nunique()}", "", "Patient tier (main):"]
for t in ["A", "B", "Cdelayed", "Cdirection"]:
    L.append(f"   {t:10s} {int((PT == t).sum()):5d}  ({(PT == t).mean():.3f})")
L += ["", "Channel tier (main):"]
for ch in CH:
    vc = M[ch].value_counts()
    L.append(f"   {ch:5s} " + "  ".join(f"{t}={int(vc.get(t, 0))}" for t in ["A", "B", "Cdelayed", "none"]))
L += ["", "Ruler wobble (main, sd_used) vs SD_pop:"]
mm = R[(R.arm == "main") & (R.tier != "none")]
for ch in CH:
    s = mm[mm.channel == ch]
    L.append(f"   {ch:5s} median {s.sd_used.median():.2f}  IQR {s.sd_used.quantile(.25):.2f}-"
             f"{s.sd_used.quantile(.75):.2f}  SD_pop {SDPOP[ch]:.2f}  "
             f"floor binds {(s.sd_used <= FLOOR + 1e-9).mean():.3f}")
d = mm[mm.tier == "Cdelayed"]
if len(d):
    L.append(f"\nDelayed rulers: close hour median {d.close_h.median():.0f}, "
             f"IQR {d.close_h.quantile(.25):.0f}-{d.close_h.quantile(.75):.0f}")
L += ["", "Arms (patients with HR and MAP rulers):"]
for arm in ["h2", "h8"]:
    a = R[R.arm == arm].pivot(index="stay_id", columns="channel", values="sd_used")
    n = int((a["hr"].notna() & a["map"].notna()).sum()) if {"hr", "map"} <= set(a.columns) else 0
    L.append(f"   {arm}: {n}")
text = "\n".join(L)
print(text)
open(OUT_TXT, "w").write(text + "\n")
