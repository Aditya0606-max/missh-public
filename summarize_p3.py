# summarize_p1.py — part 1b: deteriorating vs tier- and clock-matched stable.
import numpy as np
import pandas as pd

rng = np.random.default_rng(2026)
M = pd.read_csv("../missh_data/measures_p3.csv", low_memory=False)
DET, ST = M[M.cohort == "det"].copy(), M[M.cohort == "stable"].copy()
MEAS = ["block_hrmap", "share_defend", "share_recover", "share_bothdown", "lead_block", "drho"]
band = lambda n: 0 if n <= 2 else 1 if n <= 4 else 2 if n <= 6 else 3
for d in (DET, ST):
    d["band"] = d.news.apply(lambda n: band(n) if pd.notna(n) else -1)
    d["full"] = d.news_items >= 4

def _matched_raw(row, meas, same_news=False):
    s = ST
    if same_news:
        s = s[s.full & (s.band == row.band)]
    for w in (1, 2, 3):
        c = s[(s.tier == row.tier) & (s.hour.between(row.hour - w, row.hour + w))][meas].dropna()
        if len(c) >= 30:
            return c.values, "tier"
    c = s[s.hour.between(row.hour - 2, row.hour + 2)][meas].dropna()
    return c.values, "all"

_CACHE = {}
def matched(row, meas, same_news=False):
    key = (row.tier, float(row.hour), meas, same_news, row.band if same_news else None)
    if key not in _CACHE:
        _CACHE[key] = _matched_raw(row, meas, same_news)
    return _CACHE[key]

def per_row(d, meas, same_news=False):
    out = []
    for _, r in d.iterrows():
        x = r[meas]
        if pd.isna(x):
            continue
        ref, kind = matched(r, meas, same_news)
        if len(ref) < 30:
            continue
        out.append((r.stay_id, x > np.quantile(ref, 0.95),
                    (ref < x).mean() + 0.5 * (ref == x).mean(), kind))
    return pd.DataFrame(out, columns=["sid", "beyond", "pwin", "kind"])

def boot(df, col, n=400):
    ids = df.sid.unique()
    if len(ids) < 5:
        return np.nan, np.nan
    by = {i: df[df.sid == i][col].values for i in ids}
    vals = [np.mean(np.concatenate([by[i] for i in rng.choice(ids, len(ids))])) for _ in range(n)]
    return np.percentile(vals, [2.5, 97.5])

L = ["SUMMARY_P3 — deteriorating vs tier- and clock-matched stable (calibration)",
     "beyond = share of det readings above the matched stable 95th line (stable ~5% by design)",
     "AUC = chance a det reading exceeds a matched stable reading (0.5 = no difference)", ""]

def block(d, title, same_news=False):
    L.append(f"=== {title} ===")
    for k in (0, 1, 2, 4, 6):
        dk = d[d.k == k]
        L.append(f"-- {k} h before anchor: det patients {dk.stay_id.nunique()}")
        for meas in MEAS:
            r = per_row(dk, meas, same_news)
            if len(r) < 10:
                L.append(f"   {meas:8s} n={len(r)} (too few)")
                continue
            blo, bhi = boot(r, "beyond"); alo, ahi = boot(r, "pwin")
            L.append(f"   {meas:8s} n={len(r):4d}  beyond {r.beyond.mean():.3f} ({blo:.3f}-{bhi:.3f})"
                     f"  AUC {r.pwin.mean():.3f} ({alo:.3f}-{ahi:.3f})  all-tier fallback {(r.kind=='all').mean():.2f}")
    L.append("")

block(DET, "ALL TARGET DETERIORATING")
block(DET[DET.full], "SAME NEWS BAND (>=4 items)", same_news=True)
block(DET[DET.anchor_type == "news"], "ANCHOR = NEWS CROSSING")
block(DET[DET.anchor_type == "event"], "ANCHOR = EVENT (NEWS never crossed)")
block(DET[~DET.dni.astype(bool)], "EXCLUDING DNI")

L.append("Tier mix of det readings at 2 h:")
L.append(DET[DET.k == 2].tier.value_counts().to_string())
text = "\n".join(L)
print(text)
open("SUMMARY_P3.txt", "w").write(text + "\n")
