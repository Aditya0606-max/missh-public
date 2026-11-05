# fast_80.py — FAST_GROUP_PREDICTIONS P1-P5 with frozen calibration references
# (FAST_REFS.json). Runs on whichever split's data sits in ../missh_data.
import json
import numpy as np
import pandas as pd

rng = np.random.default_rng(2026)
R = json.load(open("FAST_REFS.json"))
SD = np.array(R["SD_tight"]); W = np.array([1.0, -1.0, 1.0, -1.0])
LINE = R["bend_line_95"]
REF = {k: np.array(R[k]) for k in ("cos", "block", "bend")}
CH = ["hr", "map", "rr", "spo2"]

v = pd.read_csv("../missh_data/vitals_hourly_cal.csv")
for c in ["blocked", "sedated"]:
    v[c] = v[c].astype(str).str.lower().eq("true")
out = pd.read_csv("../missh_data/outcome_cal.csv").set_index("stay_id")
news = pd.read_csv("../missh_data/news_hourly_cal.csv")
NW = news.set_index(["stay_id", "hour_idx"]).news

def snorm(d):
    m = ~np.isnan(d)
    return np.nan if m.sum() < 2 else float(np.sqrt(4.0 / m.sum() * np.sum(d[m] ** 2)))
def cosw(d):
    m = ~np.isnan(d)
    if m.sum() < 2: return np.nan
    na = np.linalg.norm(d[m])
    return np.nan if na == 0 else float(d[m] @ W[m] / (na * np.linalg.norm(W[m])))
def pct(x, k):
    return 0.5 if (x is None or not np.isfinite(x)) else float(np.searchsorted(REF[k], x, side="right") / len(REF[k]))

def clean_states(g, last_hour):
    x, raw = {}, {}
    for _, r in g.iterrows():
        h = int(r.hour_idx)
        if h > last_hour or r.blocked or r.sedated: continue
        vals = np.array([r[c] for c in CH], float)
        if (~np.isnan(vals)).sum() >= 2:
            x[h] = vals / SD; raw[h] = vals
    return x, raw

def steps(x, raw):
    st, triples = [], []
    for h in sorted(x):
        if h - 1 in x:
            a = x[h] - x[h - 1]; dr = raw[h] - raw[h - 1]
            st.append((h, a, dr))
            if h - 2 in x:
                c1, c2 = cosw(x[h - 1] - x[h - 2]), cosw(a)
                if np.isfinite(c1) and np.isfinite(c2):
                    triples.append((h, (c2 - c1) * snorm(a)))
    return st, triples

PAT = {}
for sid, g in v[v.hour_idx <= 4].groupby("stay_id"):
    if sid not in out.index: continue
    lab = out.loc[sid, "label"]
    if lab == "stable": last = 4
    elif lab == "escalated_hyperacute": last = min(4, int(np.floor(out.loc[sid, "esc_h"])) - 1)
    else: continue
    x, raw = clean_states(g, last)
    st, tr = steps(x, raw)
    PAT[sid] = dict(group="fast" if lab != "stable" else "stable", steps=st, triples=tr, x=x, raw=raw)

def boot2(fn, fast_ids, stable_ids, n=1000):
    vals = []
    for _ in range(n):
        f = rng.choice(fast_ids, len(fast_ids)); s = rng.choice(stable_ids, len(stable_ids))
        r = fn(f, s)
        if np.isfinite(r): vals.append(r)
    return np.percentile(vals, [2.5, 97.5])

F = [s for s, p in PAT.items() if p["group"] == "fast"]
S = [s for s, p in PAT.items() if p["group"] == "stable"]
L = ["FAST_80_RESULTS — P1-P5, frozen calibration references", f"fast patients {len(F)}  stable {len(S)}", ""]

def hrmap(ids):
    d = [(st[2][0], st[2][1]) for i in ids for st in PAT[i]["steps"] if np.isfinite(st[2][0]) and np.isfinite(st[2][1])]
    return np.array(d) if d else np.empty((0, 2))
def r_of(ids):
    d = hrmap(ids); return np.corrcoef(d[:, 0], d[:, 1])[0, 1] if len(d) > 2 else np.nan
def slope_of(ids):
    d = hrmap(ids); return np.polyfit(d[:, 0], d[:, 1], 1)[0] if len(d) > 2 else np.nan
rf, rs = r_of(F), r_of(S); lo, hi = boot2(lambda f, s: r_of(f) - r_of(s), F, S)
L.append(f"P1 lock: r fast {rf:.3f} vs stable {rs:.3f}  diff {rf - rs:+.3f}  CI {lo:+.3f} to {hi:+.3f}  "
         f"slope fast {slope_of(F):.3f} stable {slope_of(S):.3f}  steps {len(hrmap(F))}/{len(hrmap(S))}  "
         f"SUPPORT={'yes' if lo > 0 else 'no'}")

def rec_share(ids):
    d = hrmap(ids)
    return np.mean((d[:, 0] <= -1) & (d[:, 1] >= 1)) if len(d) else np.nan
a, b = rec_share(F), rec_share(S); lo, hi = boot2(lambda f, s: rec_share(f) - rec_share(s), F, S)
L.append(f"P2 recoveries: fast {a:.3f} vs stable {b:.3f}  diff {a - b:+.3f}  CI {lo:+.3f} to {hi:+.3f}  "
         f"SUPPORT={'yes' if hi < 0 else 'no'}")

def bend_share(ids):
    last = [PAT[i]["triples"][-1][1] for i in ids if PAT[i]["triples"]]
    return np.mean(np.array(last) >= LINE) if last else np.nan
a, b = bend_share(F), bend_share(S); lo, hi = boot2(lambda f, s: bend_share(f) - bend_share(s), F, S)
nf = sum(1 for i in F if PAT[i]["triples"]); ns = sum(1 for i in S if PAT[i]["triples"])
L.append(f"P3 bend >= {LINE}: fast {a:.3f} (n={nf}) vs stable {b:.3f} (n={ns})  diff {a - b:+.3f}  "
         f"CI {lo:+.3f} to {hi:+.3f}  SUPPORT={'yes' if lo > 0 else 'no'}")

from sklearn.metrics import roc_auc_score
def latest(sid, t):
    st = [s for s in PAT[sid]["steps"] if s[0] <= t - 1]
    tr = [b for h, b in PAT[sid]["triples"] if h <= t - 1]
    if not st: return None, None, tr[-1] if tr else None
    a = st[-1][1]
    blk = a[0] * a[1] if np.isfinite(a[0]) and np.isfinite(a[1]) else None
    return cosw(a), blk, (tr[-1] if tr else None)

def boot_auc_diff(d, c1, c0, n=1000):
    ids = d.sid.unique(); idx = {i: np.where(d.sid.values == i)[0] for i in ids}; vals = []
    for _ in range(n):
        sel = np.concatenate([idx[i] for i in rng.choice(ids, len(ids))]); x = d.iloc[sel]
        if x.y.nunique() < 2: continue
        vals.append(roc_auc_score(x.y, x[c1]) - roc_auc_score(x.y, x[c0]))
    return np.percentile(vals, [2.5, 97.5])

for t in (2, 3):
    rows = []
    for sid in F + S:
        if PAT[sid]["group"] == "fast" and not out.loc[sid, "esc_h"] > t: continue
        nw = NW.get((sid, t - 1), np.nan)
        if not np.isfinite(nw): continue
        _, blk, bend = latest(sid, t)
        Sx = np.mean([pct(blk, "block"), pct(bend, "bend")])
        rows.append((sid, int(PAT[sid]["group"] == "fast"), nw, nw + 3 * Sx, blk is not None or bend is not None))
    d = pd.DataFrame(rows, columns=["sid", "y", "news", "comb", "meas"])
    a0, a1 = roc_auc_score(d.y, d.news), roc_auc_score(d.y, d.comb); lo, hi = boot_auc_diff(d, "comb", "news")
    L.append(f"P4 t={t}: fast {int(d.y.sum())} stable {int((d.y==0).sum())}  no measurable step: "
             f"fast {int(((d.y==1) & ~d.meas).sum())}  AUC NEWS {a0:.3f}  NEWS+3S {a1:.3f}  "
             f"diff {a1 - a0:+.3f} CI {lo:+.3f} to {hi:+.3f}  SUPPORT={'yes' if lo > 0 else 'no'}")

h3 = news[news.hour_idx == 3].set_index("stay_id").news
MAPV = v.set_index(["stay_id", "hour_idx"])["map"]
rows = []
for sid, g in v[v.hour_idx <= 1].groupby("stay_id"):
    if sid not in out.index: continue
    lab = out.loc[sid, "label"]
    if lab not in ("stable", "escalated", "death_counts", "escalated_hyperacute"): continue
    if not (sid in h3.index and h3[sid] <= 6): continue
    nw = NW.get((sid, 1), np.nan)
    if not np.isfinite(nw): continue
    x, raw = clean_states(g, 1); st, tr = steps(x, raw)
    c = blk = bend = None
    if st:
        a = st[-1][1]; c = cosw(a)
        blk = a[0] * a[1] if np.isfinite(a[0]) and np.isfinite(a[1]) else None
    Sx = np.mean([pct(c, "cos"), pct(bend, "bend"), pct(blk, "block")])
    band = 0 if nw <= 2 else 1 if nw <= 4 else 2 if nw <= 6 else 3
    ev = out.loc[sid, "death_h"] if lab == "death_counts" else out.loc[sid, "esc_h"]
    rows.append((sid, int(lab != "stable"), band, Sx, ev, MAPV.get((sid, 1), np.nan)))
P = pd.DataFrame(rows, columns=["sid", "y", "band", "S", "event", "map1"])

def strat_auc(x):
    num = den = 0.0
    for _, b in x.groupby("band"):
        n1, n0 = b.y.sum(), (1 - b.y).sum()
        if n1 and n0:
            r = b.S.rank().values; num += r[b.y.values == 1].sum() - n1 * (n1 + 1) / 2; den += n1 * n0
    return num / den if den else np.nan
def cindex(x):
    d = x[x.y == 1].dropna(subset=["event"]); e, s = d.event.values, d.S.values
    comp = e[:, None] < e[None, :]
    return (((s[:, None] > s[None, :]) & comp).sum() + 0.5 * ((s[:, None] == s[None, :]) & comp).sum()) / comp.sum()
def bootP(x, fn, n=1000):
    vals = [fn(x.sample(len(x), replace=True, random_state=int(rng.integers(1e9)))) for _ in range(n)]
    return np.nanpercentile(vals, [2.5, 97.5])
for tag, x in (("all", P), ("excluding MAP <= 66", P[~(P.map1 <= 66)])):
    a, (lo, hi) = strat_auc(x), bootP(x, strat_auc)
    c, (clo, chi) = cindex(x), bootP(x, cindex)
    L.append(f"P5 [{tag}] n={len(x)} det={int(x.y.sum())}  (a) within-band AUC {a:.3f} CI {lo:.3f}-{hi:.3f} "
             f"SUPPORT={'yes' if lo > 0.5 else 'no'}  (b) C {c:.3f} CI {clo:.3f}-{chi:.3f} "
             f"SUPPORT={'yes' if clo > 0.5 else 'no'}")
text = "\n".join(L); print(text); open("FAST_80_RESULTS.txt", "w").write(text + "\n")
