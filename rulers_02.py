# rulers_02.py — rulers and tiers under A14 (block vs flag; C-origin; C-sparse).
# Input: vitals_hourly_cal_v2 (vitals_02.sql). No outcome labels.
import numpy as np
import pandas as pd

CH = ["hr", "map", "rr", "spo2"]
SDPOP = {"hr": 3.706, "map": 5.975, "rr": 2.608, "spo2": 1.211}
PHI, FLOOR = 0.35, 1.0
NEFF = (1 - PHI) / (1 + PHI)
RANK = {"A": 0, "B": 1, "Cdelayed": 2, "Corigin": 3, "Csparse": 4, "none": 5}

df = pd.read_csv("../missh_data/vitals_hourly_cal_v2.csv")
for c in ["block_bolus", "block_iv", "sed_infusion", "flag_oral_bp", "flag_sed_dose"]:
    df[c] = df[c].astype(str).str.lower().eq("true")
df["blocked"] = df.block_bolus | df.block_iv | df.sed_infusion
df = df.sort_values(["stay_id", "hour_idx"])

def sd_own(h, v):
    if len(v) < 3:
        return np.nan
    h, v = np.asarray(h, float), np.asarray(v, float)
    r = v - np.polyval(np.polyfit(h, v, 1), h)
    return float(np.sqrt(np.sum(r * r) / (len(v) - 2)))

def blended(h, v, ch):
    so, ne = sd_own(h, v), len(v) * NEFF
    sd = SDPOP[ch] if np.isnan(so) else np.sqrt((ne * so**2 + 2 * SDPOP[ch]**2) / (ne + 2))
    return so, max(sd, FLOOR)

rows = []
for sid, g in df.groupby("stay_id"):
    g = g.set_index("hour_idx")
    for ch in CH:
        present = g[ch].notna()
        clean = list(g.index[present & ~g.blocked])
        c04 = [h for h in clean if h <= 4]
        c11 = [h for h in clean if h <= 11]
        so, origin_treated = np.nan, False
        if len(c04) >= 4:
            tier, hs, close = ("A" if len(c04) == 5 else "B"), c04, 5
            v = g.loc[hs, ch].values; so, su = blended(hs, v, ch); centre = v.mean()
        elif len(c11) >= 5:
            tier, hs, close = "Cdelayed", c11[:5], c11[4] + 1
            v = g.loc[hs, ch].values; so, su = blended(hs, v, ch); centre = v.mean()
        elif len(c11) >= 1:
            h0 = c11[0]
            hs = [h0, h0 + 1] if (h0 + 1) in c11 else [h0]
            tier, close = "Corigin", hs[-1] + 1
            centre, su = g.loc[hs, ch].mean(), max(SDPOP[ch], FLOOR)
        else:
            anyp = [h for h in g.index[present] if h <= 11]
            if anyp:
                h0 = anyp[0]
                tier, hs, close = "Csparse", [h0], h0 + 1
                centre, su = g.loc[h0, ch], max(SDPOP[ch], FLOOR)
                origin_treated = bool(g.loc[h0, "blocked"])
            else:
                tier, hs, close, centre, su = "none", [], np.nan, np.nan, np.nan
        w = g[g.index <= 11]
        unclean = float(((~w[ch].notna()) | w.blocked).mean()) if len(w) else np.nan
        rows.append((sid, ch, tier, len(hs), centre, so, su, close, origin_treated, unclean))

R = pd.DataFrame(rows, columns=["stay_id", "channel", "tier", "n_clean", "centre",
                                "sd_own", "sd_used", "close_h", "origin_treated", "unclean_0_11"])
R.to_csv("../missh_data/rulers_cal_v2.csv", index=False)

M = R.pivot(index="stay_id", columns="channel", values="tier")
def ptier(r):
    if all(r[c] == "A" for c in CH):
        return "A"
    worst = max(RANK[r["hr"]], RANK[r["map"]])
    return {0: "B", 1: "B", 2: "Cdelayed", 3: "Corigin", 4: "Csparse", 5: "none"}[worst]
PT = M.apply(ptier, axis=1)
PT.rename("ptier").to_csv("../missh_data/patient_tiers_cal_v2.csv")

L = ["RULER_COUNTS_V2 — rulers_02.py (A14), calibration, no outcomes",
     f"patients: {R.stay_id.nunique()}", "", "Patient tier:"]
for t in ["A", "B", "Cdelayed", "Corigin", "Csparse", "none"]:
    L.append(f"   {t:9s} {int((PT == t).sum()):5d}  ({(PT == t).mean():.3f})")
L += ["", "Channel tier:"]
for ch in CH:
    vc = M[ch].value_counts()
    L.append(f"   {ch:5s} " + "  ".join(f"{t}={int(vc.get(t, 0))}" for t in RANK))
L += ["", "Ruler wobble (sd_used) median by tier, HR / MAP:"]
for t in ["A", "B", "Cdelayed", "Corigin", "Csparse"]:
    s = R[R.tier == t]
    hr, mp = s[s.channel == "hr"].sd_used.median(), s[s.channel == "map"].sd_used.median()
    L.append(f"   {t:9s} HR {hr:.2f}  MAP {mp:.2f}")
d = R[R.tier.isin(["Cdelayed", "Corigin", "Csparse"])]
for t in ["Cdelayed", "Corigin", "Csparse"]:
    s = d[(d.tier == t) & (d.channel == "map")]
    if len(s):
        L.append(f"   {t:9s} MAP close/origin hour median {s.close_h.median():.0f}; "
                 f"unclean share 0-11 median {s.unclean_0_11.median():.2f}")
s = R[(R.tier == "Csparse") & (R.channel == "map")]
if len(s):
    L.append(f"   Csparse MAP origins taken in a treated hour: {s.origin_treated.mean():.3f}")
text = "\n".join(L)
print(text)
open("RULER_COUNTS_V2.txt", "w").write(text + "\n")
