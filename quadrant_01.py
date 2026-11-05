# quadrant_01.py — EXPLORATORY E3b (post-result): HR-MAP step quadrants.
import numpy as np
import pandas as pd

OUT = "QUADRANT_RESULTS.txt"

def load(p):
    d = pd.read_csv(p)
    d["blocked"] = d["blocked"].astype(str).str.lower().eq("true")
    return d.sort_values(["stay_id", "hour_idx"])

sed = pd.read_csv("../missh_data/sed_hours_cal.csv")
sed["sedated"] = sed["sedated"].astype(str).str.lower().eq("true")
SED = set(zip(sed.stay_id[sed.sedated], sed.hour_idx[sed.sedated]))

def steps(df, last_fn, esc=False):
    rows = []
    for sid, g in df.groupby("stay_id"):
        e = g.esc_h.iloc[0] if esc else np.nan
        g = g[g.hour_idx <= last_fn(g)].set_index("hour_idx")
        for h in g.index:
            if h + 1 not in g.index:
                continue
            a, b = g.loc[h], g.loc[h + 1]
            if a.blocked or b.blocked or (sid, h) in SED or (sid, h + 1) in SED:
                continue
            if pd.isna(a.hr) or pd.isna(b.hr) or pd.isna(a["map"]) or pd.isna(b["map"]):
                continue
            rows.append((sid, b.hr - a.hr, b["map"] - a["map"], e - (h + 2) if esc else np.nan))
    return pd.DataFrame(rows, columns=["stay_id", "dhr", "dmap", "h_before_esc"])

def quad(d):
    hr, mp = d.dhr, d.dmap
    flat = (hr.abs() < 1) | (mp.abs() < 1)
    q = np.select([flat, (hr > 0) & (mp < 0), (hr < 0) & (mp > 0),
                   (hr < 0) & (mp < 0), (hr > 0) & (mp > 0)],
                  ["flat", "defending", "recovering", "both_down", "both_up"], "flat")
    return pd.Series(q).value_counts(normalize=True).reindex(
        ["defending", "recovering", "both_down", "both_up", "flat"]).fillna(0)

hyp = load("../missh_data/hyper_hourly_cal.csv")
stb = load("../missh_data/phi_hourly_cal_tight.csv")
F = steps(hyp, lambda g: int(np.floor(g.esc_h.iloc[0] - 1)), esc=True)
S = steps(stb, lambda g: 4)

L = ["QUADRANT_RESULTS — EXPLORATORY E3b (post-result)", ""]
sets = [("stable first 5 h", S), ("fast all", F),
        ("fast last 2 h before escalation", F[F.h_before_esc < 2]),
        ("fast earlier", F[F.h_before_esc >= 2])]
for name, d in sets:
    L.append(f"[{name}] steps={len(d)} patients={d.stay_id.nunique()}")
    if len(d):
        for k, v in quad(d).items():
            L.append(f"   {k:11s} {v:.3f}  (~{int(round(v * len(d)))})")
    L.append("")
text = "\n".join(L)
print(text)
open(OUT, "w").write(text + "\n")
