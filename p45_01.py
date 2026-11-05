# p45_01.py — rehearsal of P4 and P5 (FAST_GROUP_PREDICTIONS) on calibration.
import numpy as np
import pandas as pd

rng = np.random.default_rng(2026)
CH = ["hr", "map", "rr", "spo2"]
SD = np.array([3.743, 5.941, 2.600, 1.211])
W = np.array([1.0, -1.0, 1.0, -1.0])

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
    if m.sum() < 2:
        return np.nan
    a, b = d[m], W[m]; na = np.linalg.norm(a)
    return np.nan if na == 0 else float(a @ b / (na * np.linalg.norm(b)))

def patient_features(g):
    x = {}
    for _, r in g.iterrows():
        if r.blocked or r.sedated:
            continue
        vec = np.array([r[c] for c in CH], float) / SD
        if (~np.isnan(vec)).sum() >= 2:
            x[int(r.hour_idx)] = vec
    feats = {}
    for h in sorted(x):
        if h - 1 in x:
            a = x[h] - x[h - 1]
            blk = a[0] * a[1] if not (np.isnan(a[0]) or np.isnan(a[1])) else np.nan
            bend = np.nan
            if h - 2 in x:
                a1 = x[h - 1] - x[h - 2]
                c1, c2 = cosw(a1), cosw(a)
                if not (np.isnan(c1) or np.isnan(c2)):
                    bend = (c2 - c1) * snorm(a)
            feats[h] = (cosw(a), blk, bend)
    return feats

F = {sid: patient_features(g) for sid, g in v[v.hour_idx <= 4].groupby("stay_id")}

stable = [s for s in out.index if out.loc[s, "label"] == "stable"]
ref = {k: np.array([f[k] for s in stable for f in F.get(s, {}).values()
                    if not np.isnan(f[k])]) for k in range(3)}
def pct(val, k):
    return 0.5 if (val is None or np.isnan(val)) else float((ref[k] <= val).mean())

def score_at(sid, t, use_cos):
    f = F.get(sid, {})
    hs = [h for h in f if h <= t - 1]
    if not hs:
        return 0.5, False
    c, b, bd = f[max(hs)]
    parts = ([pct(c, 0)] if use_cos else []) + [pct(b, 1), pct(bd, 2)]
    return float(np.mean(parts)), True

def auc(y, s):
    y, s = np.asarray(y), np.asarray(s)
    n1, n0 = y.sum(), (1 - y).sum()
    if n1 == 0 or n0 == 0:
        return np.nan
    r = pd.Series(s).rank().values
    return float((r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))

def boot(df, fn, n=500):
    vals = [fn(df.sample(len(df), replace=True, random_state=int(rng.integers(1e9)))) for _ in range(n)]
    return np.nanpercentile(vals, [2.5, 97.5])

L = ["P45_RESULTS — rehearsal on calibration (E5)", ""]

# P4: fast not yet escalated at t vs stable; NEWS(t-1) vs NEWS + 3*S
for t in (2, 3):
    rows = []
    for sid in out.index:
        lab = out.loc[sid, "label"]
        if lab == "stable" or (lab == "escalated_hyperacute" and out.loc[sid, "esc_h"] > t):
            nw = NW.get((sid, t - 1), np.nan)
            if np.isnan(nw):
                continue
            S, meas = score_at(sid, t, use_cos=False)
            rows.append((sid, int(lab != "stable"), nw, nw + 3 * S, meas))
    d = pd.DataFrame(rows, columns=["sid", "y", "news", "comb", "meas"])
    a0, a1 = auc(d.y, d.news), auc(d.y, d.comb)
    lo, hi = boot(d, lambda x: auc(x.y, x.comb) - auc(x.y, x.news))
    L.append(f"[P4 t={t}] fast={int(d.y.sum())} stable={int((d.y==0).sum())} "
             f"measurable fast={int(d[d.y==1].meas.sum())}")
    L.append(f"   AUC NEWS {a0:.3f}  NEWS+3S {a1:.3f}  diff {a1-a0:+.3f}  CI {lo:+.3f} to {hi:+.3f}")
L.append("")

# P5: target patients at t=2, within NEWS bands; deteriorating within 72 h vs stable
h3 = news[news.hour_idx == 3].set_index("stay_id").news
rows = []
for sid in out.index:
    lab = out.loc[sid, "label"]
    if lab not in ("stable", "escalated", "death_counts", "escalated_hyperacute"):
        continue
    if not (sid in h3.index and h3[sid] <= 6):
        continue
    nw = NW.get((sid, 1), np.nan)
    if np.isnan(nw):
        continue
    band = 0 if nw <= 2 else 1 if nw <= 4 else 2 if nw <= 6 else 3
    S, meas = score_at(sid, 2, use_cos=True)
    ev = out.loc[sid, "esc_h"] if lab != "death_counts" else out.loc[sid, "death_h"]
    vmap = v[(v.stay_id == sid) & (v.hour_idx == 1)]["map"]
    mp = float(vmap.iloc[0]) if len(vmap) and pd.notna(vmap.iloc[0]) else np.nan
    rows.append((sid, int(lab != "stable"), band, S, meas, ev, mp))
P = pd.DataFrame(rows, columns=["sid", "y", "band", "S", "meas", "event", "map1"])

def strat_auc(x):
    num = den = 0.0
    for _, b in x.groupby("band"):
        n1, n0 = b.y.sum(), (1 - b.y).sum()
        if n1 and n0:
            r = b.S.rank().values
            num += r[b.y.values == 1].sum() - n1 * (n1 + 1) / 2
            den += n1 * n0
    return num / den if den else np.nan

def cindex(x):
    d = x[x.y == 1].dropna(subset=["event"])
    e, s = d.event.values, d.S.values
    comp = e[:, None] < e[None, :]
    conc = ((s[:, None] > s[None, :]) & comp).sum() + 0.5 * ((s[:, None] == s[None, :]) & comp).sum()
    return conc / comp.sum() if comp.sum() else np.nan

for tag, x in [("all", P), ("excluding MAP <= 66 at hour 1", P[~(P.map1 <= 66)])]:
    lo, hi = boot(x, strat_auc); clo, chi = boot(x, cindex)
    L.append(f"[P5 {tag}] patients={len(x)} deteriorating={int(x.y.sum())} "
             f"measurable={int(x.meas.sum())}")
    L.append(f"   (a) within-NEWS-band AUC {strat_auc(x):.3f}  CI {lo:.3f}-{hi:.3f}")
    L.append(f"   (b) concordance with earlier event {cindex(x):.3f}  CI {clo:.3f}-{chi:.3f}")
L.append("")
L.append("NEWS bands at hour 1 (patients, deteriorating):")
L.append(P.groupby("band").agg(n=("y", "size"), det=("y", "sum")).to_string())
text = "\n".join(L)
print(text)
open("P45_RESULTS.txt", "w").write(text + "\n")
