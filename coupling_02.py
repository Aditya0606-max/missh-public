# coupling_02.py — EXPLORATORY E3a (post-result): E3 without sedated hours.
import numpy as np
import pandas as pd

rng = np.random.default_rng(2026)
OUT = "COUPLING_SED_RESULTS.txt"

def load(p):
    d = pd.read_csv(p)
    d["blocked"] = d["blocked"].astype(str).str.lower().eq("true")
    return d.sort_values(["stay_id", "hour_idx"])

sed = pd.read_csv("../missh_data/sed_hours_cal.csv")
sed["sedated"] = sed["sedated"].astype(str).str.lower().eq("true")
SED = set(zip(sed.stay_id[sed.sedated], sed.hour_idx[sed.sedated]))

def steps(df, last_fn):
    rows = []
    for sid, g in df.groupby("stay_id"):
        g = g[g.hour_idx <= last_fn(g)].set_index("hour_idx")
        for h in g.index:
            if h + 1 not in g.index:
                continue
            a, b = g.loc[h], g.loc[h + 1]
            if a.blocked or b.blocked:
                continue
            if pd.isna(a.hr) or pd.isna(b.hr) or pd.isna(a["map"]) or pd.isna(b["map"]):
                continue
            s = ((sid, h) in SED) or ((sid, h + 1) in SED)
            rows.append((sid, b.hr - a.hr, b["map"] - a["map"], s))
    return pd.DataFrame(rows, columns=["stay_id", "dhr", "dmap", "sed"])

def stats(s):
    if len(s) < 3:
        return np.nan, np.nan, np.nan, 0
    f = s[s.dmap <= -5]
    ans = (f.dhr >= 2).mean() if len(f) else np.nan
    return ans, s.dhr.corr(s.dmap), np.polyfit(s.dmap, s.dhr, 1)[0], len(f)

def boot(s, n=2000):
    ids = s.stay_id.unique()
    by = {i: s[s.stay_id == i] for i in ids}
    out = [stats(pd.concat([by[i] for i in rng.choice(ids, len(ids))]))[:3]
           for _ in range(n)]
    a = np.array(out, float)
    return np.nanpercentile(a, 2.5, axis=0), np.nanpercentile(a, 97.5, axis=0)

hyp = load("../missh_data/hyper_hourly_cal.csv")
stb = load("../missh_data/phi_hourly_cal_tight.csv")
F = steps(hyp, lambda g: int(np.floor(g.esc_h.iloc[0] - 1)))
S = steps(stb, lambda g: 4)

L = ["COUPLING_SED_RESULTS — EXPLORATORY E3a (post-result)", ""]
for name, d in [("fast", F), ("stable first 5 h", S)]:
    L.append(f"[{name}] steps={len(d)}  sedated steps={int(d.sed.sum())} "
             f"({d.sed.mean():.3f})")
    for tag, sub in [("all steps", d), ("NOT sedated", d[~d.sed]), ("sedated only", d[d.sed])]:
        ans, r, sl, nf = stats(sub)
        if len(sub) >= 10 and sub.stay_id.nunique() >= 5:
            lo, hi = boot(sub)
            L.append(f"   {tag:12s} n={len(sub):5d} pts={sub.stay_id.nunique():5d}  "
                     f"r={r:.3f} ({lo[1]:.3f}-{hi[1]:.3f})  "
                     f"slope={sl:.3f} ({lo[2]:.3f}-{hi[2]:.3f})  "
                     f"answer={ans:.3f} [falls {nf}]")
        else:
            L.append(f"   {tag:12s} n={len(sub)} (too few)")
    L.append("")
text = "\n".join(L)
print(text)
open(OUT, "w").write(text + "\n")
