# coupling_01.py — EXPLORATORY E3 (post-result): pooled HR-MAP answer.
import numpy as np
import pandas as pd

rng = np.random.default_rng(2026)
OUT = "COUPLING_RESULTS.txt"

def load(p):
    d = pd.read_csv(p)
    d["blocked"] = d["blocked"].astype(str).str.lower().eq("true")
    return d.sort_values(["stay_id", "hour_idx"])

def steps(df, last_by_stay):
    rows = []
    for sid, g in df.groupby("stay_id"):
        last = last_by_stay(g)
        g = g[g.hour_idx <= last].set_index("hour_idx")
        for h in g.index:
            if h + 1 in g.index:
                a, b = g.loc[h], g.loc[h + 1]
                if a.blocked or b.blocked:
                    continue
                if pd.notna(a.hr) and pd.notna(b.hr) and pd.notna(a["map"]) and pd.notna(b["map"]):
                    rows.append((sid, b.hr - a.hr, b["map"] - a["map"]))
    return pd.DataFrame(rows, columns=["stay_id", "dhr", "dmap"])

def stats(s):
    falls = s[s.dmap <= -5]
    ans = (falls.dhr >= 2).mean() if len(falls) else np.nan
    r = s.dhr.corr(s.dmap) if len(s) > 2 else np.nan
    slope = np.polyfit(s.dmap, s.dhr, 1)[0] if len(s) > 2 else np.nan
    return ans, r, slope, len(falls)

def boot(s, n=2000):
    ids = s.stay_id.unique()
    by = {i: s[s.stay_id == i] for i in ids}
    out = []
    for _ in range(n):
        pick = rng.choice(ids, len(ids), replace=True)
        out.append(stats(pd.concat([by[i] for i in pick]))[:3])
    a = np.array(out, float)
    return np.nanpercentile(a, 2.5, axis=0), np.nanpercentile(a, 97.5, axis=0)

hyp = load("../missh_data/hyper_hourly_cal.csv")
stb = load("../missh_data/phi_hourly_cal_tight.csv")

F = steps(hyp, lambda g: int(np.floor(g.esc_h.iloc[0] - 1)))
S5 = steps(stb, lambda g: 4)
SA = steps(stb, lambda g: g.hour_idx.max())

L = ["COUPLING_RESULTS — EXPLORATORY E3 (post-result), pooled HR-MAP answer", ""]
for name, s in [("fast (before escalation)", F),
                ("stable first 5 h", S5),
                ("stable all hours", SA)]:
    ans, r, slope, nf = stats(s)
    lo, hi = boot(s, 1000 if len(s) > 20000 else 2000)
    L.append(f"[{name}] patients={s.stay_id.nunique()} steps={len(s)} MAP-falls>=5={nf}")
    L.append(f"   answer rate (HR +2 when MAP -5): {ans:.3f}  CI {lo[0]:.3f}-{hi[0]:.3f}")
    L.append(f"   step correlation dHR~dMAP:       {r:.3f}  CI {lo[1]:.3f}-{hi[1]:.3f}")
    L.append(f"   slope (bpm per mmHg):            {slope:.3f}  CI {lo[2]:.3f}-{hi[2]:.3f}")
    L.append("")
text = "\n".join(L)
print(text)
open(OUT, "w").write(text + "\n")
