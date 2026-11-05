# rulers_03.py — A15: provisional ruler at hour 2, main frozen at hour 3;
# arms h2, h5, h8; C-delayed / C-origin / C-sparse per A14. No outcomes.
import numpy as np
import pandas as pd

CH = ["hr", "map", "rr", "spo2"]
SDPOP = {"hr": 3.706, "map": 5.975, "rr": 2.608, "spo2": 1.211}
PHI, FLOOR = 0.35, 1.0
NEFF = (1 - PHI) / (1 + PHI)
RANK = {"A": 0, "B": 1, "Cdelayed": 2, "Corigin": 3, "Csparse": 4, "none": 5}

df = pd.read_csv("../missh_data/vitals_hourly_cal_v2.csv")
for c in ["block_bolus", "block_iv", "sed_infusion"]:
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
def add(sid, arm, ch, tier, hs, centre, so, su, close, ot=False, unclean=np.nan):
    rows.append((sid, arm, ch, tier, len(hs), centre, so, su, close, ot, unclean))

for sid, g in df.groupby("stay_id"):
    g = g.set_index("hour_idx")
    for ch in CH:
        present = g[ch].notna()
        clean = list(g.index[present & ~g.blocked])
        c02 = [h for h in clean if h <= 2]
        c01 = [h for h in clean if h <= 1]
        c04 = [h for h in clean if h <= 4]
        c07 = [h for h in clean if h <= 7]
        c11 = [h for h in clean if h <= 11]
        w = g[g.index <= 11]
        unclean = float(((~w[ch].notna()) | w.blocked).mean()) if len(w) else np.nan
        # main (A15)
        if len(c02) >= 2:
            tier = "A" if len(c02) == 3 else "B"
            v = g.loc[c02, ch].values; so, su = blended(c02, v, ch)
            add(sid, "main", ch, tier, c02, v.mean(), so, su, 3, unclean=unclean)
            if c01:
                add(sid, "prov2", ch, tier, c01, g.loc[c01, ch].mean(), np.nan,
                    max(SDPOP[ch], FLOOR), 2)
        elif len(c11) >= 5:
            hs = c11[:5]; v = g.loc[hs, ch].values; so, su = blended(hs, v, ch)
            add(sid, "main", ch, "Cdelayed", hs, v.mean(), so, su, hs[-1] + 1, unclean=unclean)
        elif len(c11) >= 1:
            h0 = c11[0]; hs = [h0, h0 + 1] if (h0 + 1) in c11 else [h0]
            add(sid, "main", ch, "Corigin", hs, g.loc[hs, ch].mean(), np.nan,
                max(SDPOP[ch], FLOOR), hs[-1] + 1, unclean=unclean)
        else:
            anyp = [h for h in g.index[present] if h <= 11]
            if anyp:
                h0 = anyp[0]
                add(sid, "main", ch, "Csparse", [h0], g.loc[h0, ch], np.nan,
                    max(SDPOP[ch], FLOOR), h0 + 1, bool(g.loc[h0, "blocked"]), unclean)
            else:
                add(sid, "main", ch, "none", [], np.nan, np.nan, np.nan, np.nan, unclean=unclean)
        # arms
        if c01:
            add(sid, "h2", ch, "arm", c01, g.loc[c01, ch].mean(), np.nan, max(SDPOP[ch], FLOOR), 2)
        if len(c04) >= 4:
            v = g.loc[c04, ch].values; so, su = blended(c04, v, ch)
            add(sid, "h5", ch, "arm", c04, v.mean(), so, su, 5)
        if len(c07) >= 6:
            v = g.loc[c07, ch].values; so = sd_own(c07, v)
            add(sid, "h8", ch, "arm", c07, v.mean(), so, max(so, FLOOR), 8)

R = pd.DataFrame(rows, columns=["stay_id", "arm", "channel", "tier", "n_clean", "centre",
                                "sd_own", "sd_used", "close_h", "origin_treated", "unclean_0_11"])
R.to_csv("../missh_data/rulers_cal_v3.csv", index=False)

M = R[R.arm == "main"].pivot(index="stay_id", columns="channel", values="tier")
def ptier(r):
    if all(r[c] == "A" for c in CH):
        return "A"
    worst = max(RANK[r["hr"]], RANK[r["map"]])
    return {0: "B", 1: "B", 2: "Cdelayed", 3: "Corigin", 4: "Csparse", 5: "none"}[worst]
PT = M.apply(ptier, axis=1)
PT.rename("ptier").to_csv("../missh_data/patient_tiers_cal_v3.csv")

L = ["RULER_COUNTS_V3 — rulers_03.py (A15: frozen at hour 3), no outcomes",
     f"patients: {R.stay_id.nunique()}", "", "Patient tier (main):"]
for t in RANK:
    L.append(f"   {t:9s} {int((PT == t).sum()):5d}  ({(PT == t).mean():.3f})")
L += ["", "Ruler wobble (main) median, HR / MAP, by tier:"]
mm = R[R.arm == "main"]
for t in ["A", "B", "Cdelayed", "Corigin", "Csparse"]:
    s = mm[mm.tier == t]
    L.append(f"   {t:9s} HR {s[s.channel=='hr'].sd_used.median():.2f}  "
             f"MAP {s[s.channel=='map'].sd_used.median():.2f}")
L += ["", "Arms (patients with HR and MAP):"]
for arm in ["prov2", "h2", "h5", "h8"]:
    a = R[R.arm == arm].pivot(index="stay_id", columns="channel", values="sd_used")
    n = int((a["hr"].notna() & a["map"].notna()).sum()) if {"hr", "map"} <= set(a.columns) else 0
    L.append(f"   {arm}: {n}")
text = "\n".join(L)
print(text)
open("RULER_COUNTS_V3.txt", "w").write(text + "\n")
