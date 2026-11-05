# hyper_01.py — fast-group path profile vs stable first 5 h
# Implements HYPERACUTE_PROFILE.md (cf1cc97). Descriptive only.
import numpy as np
import pandas as pd

CH = ["hr", "map", "rr", "spo2"]
W = np.array([1.0, -1.0, 1.0, -1.0])        # worsening direction
FLOOR = np.array([1.0, 1.0, 1.0, 1.0])      # device floors (OMEGA_SCALE_RULE)
OUT = "HYPER_RESULTS.txt"

def load(path):
    df = pd.read_csv(path)
    df["blocked"] = df["blocked"].astype(str).str.lower().eq("true")
    return df.sort_values(["stay_id", "hour_idx"])

def snorm(d):
    m = ~np.isnan(d)
    if m.sum() < 2:
        return np.nan
    return float(np.sqrt(4.0 / m.sum() * np.sum(d[m] ** 2)))

def cosw(d):
    m = ~np.isnan(d)
    if m.sum() < 2:
        return np.nan
    a, b = d[m], W[m]
    na = np.linalg.norm(a)
    return np.nan if na == 0 else float(a @ b / (na * np.linalg.norm(b)))

def pshare(d):
    sq = np.where(np.isnan(d), 0.0, d ** 2)
    t = sq.sum()
    return np.nan if t == 0 else float((sq[0] + sq[1]) / t)

def profile(g, last):
    clean = []
    for _, r in g[g.hour_idx <= last].iterrows():
        if r.blocked:
            continue
        v = np.array([r[c] for c in CH], float) / FLOOR
        if (~np.isnan(v)).sum() >= 2:
            clean.append((int(r.hour_idx), v))
    if len(clean) < 2:
        return []
    h0, x0 = clean[0]
    prev, L, pos, n, out = x0, 0.0, 0, 0, []
    for h, x in clean[1:]:
        step = x - prev
        sl = snorm(step)
        if not np.isnan(sl):
            L += sl
            c = cosw(step)
            if not np.isnan(c):
                n += 1
                pos += int(c > 0)
        prev = x
        net = x - x0
        N = snorm(net)
        out.append(dict(h=h, k=h - h0, N=N,
                        speed=N / (h - h0) if not np.isnan(N) else np.nan,
                        straight=N / L if (L > 0 and not np.isnan(N)) else np.nan,
                        cos=cosw(net), consist=pos / n if n else np.nan,
                        pshare=pshare(net)))
    return out

hyp = load("../missh_data/hyper_hourly_cal.csv")
stb = load("../missh_data/phi_hourly_cal_tight.csv")
stb = stb[stb.hour_idx < 5]

hrows = []
for sid, g in hyp.groupby("stay_id"):
    esc, dni = g.esc_h.iloc[0], g.dni_h.iloc[0]
    last = int(np.floor(esc - 1))
    fb = g[g.blocked & (g.hour_idx <= last)].hour_idx.min()
    for r in profile(g, last):
        r.update(stay_id=sid, esc=esc, first_block=fb,
                 dni=(not pd.isna(dni)) and dni < esc)
        hrows.append(r)
srows = []
for sid, g in stb.groupby("stay_id"):
    for r in profile(g, 4):
        r.update(stay_id=sid)
        srows.append(r)
H, S = pd.DataFrame(hrows), pd.DataFrame(srows)

M = ["N", "speed", "straight", "cos", "consist"]
q95 = S.groupby("k")[M].quantile(0.95)
q50 = S.groupby("k")[M].quantile(0.50)
q99 = S.groupby("k")[M].quantile(0.99)

def passes(df):
    c95 = df.k.map(q95["cos"])
    s95 = df.k.map(q95["speed"])
    return (df["cos"] >= c95) & (df["speed"] >= s95)

H["pass"], S["pass"] = passes(H), passes(S)

L = ["HYPER_RESULTS — hyper_01.py (HYPERACUTE_PROFILE cf1cc97)",
     f"fast patients with a profile: {H.stay_id.nunique()} of {hyp.stay_id.nunique()}",
     f"stable patients with a profile (first 5 h): {S.stay_id.nunique()}", ""]
L.append("By hours since first clean hour (k): fast median | stable median / 95th / 99th")
for k in sorted(H.k.unique()):
    h, s = H[H.k == k], S[S.k == k]
    L.append(f"k={k}: fast n={len(h)}  stable n={len(s)}")
    for m in M:
        if k in q95.index:
            L.append(f"   {m:9s} fast {h[m].median():7.3f} | stable "
                     f"{q50.loc[k, m]:7.3f} / {q95.loc[k, m]:7.3f} / {q99.loc[k, m]:7.3f}")
    L.append(f"   pass (cos AND speed >= stable 95th): fast {h['pass'].mean():.3f}"
             f"  stable {s['pass'].mean():.3f}")
L.append("")

def summary(Hs, tag):
    first = Hs[Hs["pass"]].sort_values("h").groupby("stay_id").first()
    hp, sp = len(first), S[S["pass"]].stay_id.nunique()
    out = [f"[{tag}] fast patients passing at any hour: {hp} of {Hs.stay_id.nunique()}",
           f"   stable patients passing in first 5 h: {sp} of {S.stay_id.nunique()}",
           f"   precision (fast / all passing): {hp / (hp + sp):.3f}" if hp + sp else "   precision: n/a"]
    if hp:
        lead_esc = first.esc - (first.h + 1)
        lead_b = first.first_block - (first.h + 1)
        out.append(f"   lead over escalation (h): median {lead_esc.median():.2f}  "
                   f"IQR {lead_esc.quantile(.25):.2f}-{lead_esc.quantile(.75):.2f}")
        hb = lead_b.dropna()
        out.append(f"   patients with a treatment block: {len(hb)}; lead over first block "
                   f"(h): median {hb.median():.2f}; share flagged before first block "
                   f"{(hb > 0).mean():.3f}" if len(hb) else "   no treatment blocks")
        ps = first.pshare
        out.append(f"   path at flag: pressure-led {(ps > 2/3).sum()}  "
                   f"breathing-led {(ps < 1/3).sum()}  mixed {((ps >= 1/3) & (ps <= 2/3)).sum()}")
    return out

L += summary(H, "all")
L += summary(H[~H.dni], "excluding DNI")
text = "\n".join(L)
print(text)
open(OUT, "w").write(text + "\n")
