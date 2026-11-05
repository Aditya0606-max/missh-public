# e4_bend_time.py — EXPLORATORY E4: bend with rate, time left to MAP 65.
import numpy as np
import pandas as pd

CH = ["hr", "map", "rr", "spo2"]
SD = np.array([3.743, 5.941, 2.600, 1.211])
W = np.array([1.0, -1.0, 1.0, -1.0])
OUT = "E4_RESULTS.txt"

def load(p):
    d = pd.read_csv(p)
    d["blocked"] = d["blocked"].astype(str).str.lower().eq("true")
    return d.sort_values(["stay_id", "hour_idx"])

sed = pd.read_csv("../missh_data/sed_hours_cal.csv")
sed["sedated"] = sed["sedated"].astype(str).str.lower().eq("true")
SED = set(zip(sed.stay_id[sed.sedated], sed.hour_idx[sed.sedated]))

def snorm(d):
    m = ~np.isnan(d)
    return np.nan if m.sum() < 2 else float(np.sqrt(4.0 / m.sum() * np.sum(d[m] ** 2)))

def cosw(d):
    m = ~np.isnan(d)
    if m.sum() < 2:
        return np.nan
    a, b = d[m], W[m]
    na = np.linalg.norm(a)
    return np.nan if na == 0 else float(a @ b / (na * np.linalg.norm(b)))

def tleft(m_now, fall_per_h):
    if m_now <= 65:
        return 0.0
    return (m_now - 65) / (-fall_per_h) if fall_per_h < 0 else np.inf

def patient(sid, g, last):
    x, mp = {}, {}
    for _, r in g[g.hour_idx <= last].iterrows():
        h = int(r.hour_idx)
        if r.blocked or (sid, h) in SED:
            continue
        v = np.array([r[c] for c in CH], float) / SD
        if (~np.isnan(v)).sum() >= 2:
            x[h] = v
        if pd.notna(r["map"]):
            mp[h] = float(r["map"])
    bends, t1, t2 = [], [], []
    for h in sorted(x):
        if h + 1 in x and h + 2 in x:
            a1, a2 = x[h + 1] - x[h], x[h + 2] - x[h + 1]
            c1, c2 = cosw(a1), cosw(a2)
            if not (np.isnan(c1) or np.isnan(c2)):
                bends.append((h + 2, (c2 - c1) * snorm(a2)))
    for h in sorted(mp):
        if h + 1 in mp:
            t1.append((h + 1, tleft(mp[h + 1], mp[h + 1] - mp[h])))
        if h + 1 in mp and h + 2 in mp:
            t2.append((h + 2, tleft(mp[h + 2], (mp[h + 2] - mp[h]) / 2)))
    return bends, t1, t2

def collect(df, last_fn):
    B, T1, T2 = [], [], []
    for sid, g in df.groupby("stay_id"):
        b, t1, t2 = patient(sid, g, last_fn(g))
        B += [(sid, h, v) for h, v in b]
        T1 += [(sid, h, v) for h, v in t1]
        T2 += [(sid, h, v) for h, v in t2]
    mk = lambda r: pd.DataFrame(r, columns=["stay_id", "h", "v"])
    return mk(B), mk(T1), mk(T2)

hyp = load("../missh_data/hyper_hourly_cal.csv")
stb = load("../missh_data/phi_hourly_cal_tight.csv")
FB, FT1, FT2 = collect(hyp, lambda g: int(np.floor(g.esc_h.iloc[0] - 1)))
SB, ST1, ST2 = collect(stb, lambda g: 4)

def last_per_patient(d):
    return d.sort_values("h").groupby("stay_id").v.last()

L = ["E4_RESULTS — EXPLORATORY (bend with rate, time left to MAP 65)", ""]

q95 = SB.v.quantile(0.95) if len(SB) else np.nan
L.append("[bend with rate] (3 consecutive clean hours)")
L.append(f"   fast: triples={len(FB)} patients={FB.stay_id.nunique()}  "
         f"median={FB.v.median():.3f}")
L.append(f"   stable: triples={len(SB)} patients={SB.stay_id.nunique()}  "
         f"median={SB.v.median():.3f}  95th={q95:.3f}")
if len(FB):
    fl, sl = last_per_patient(FB), last_per_patient(SB)
    L.append(f"   share of triples >= stable 95th: fast {(FB.v >= q95).mean():.3f}  "
             f"stable {(SB.v >= q95).mean():.3f}")
    L.append(f"   last triple per patient >= stable 95th: fast {(fl >= q95).mean():.3f} "
             f"(n={len(fl)})  stable {(sl >= q95).mean():.3f} (n={len(sl)})")
    L.append(f"   share with positive bend (turning toward worsening): "
             f"fast {(FB.v > 0).mean():.3f}  stable {(SB.v > 0).mean():.3f}")
L.append("")

for tag, F, S in [("time left, 1 arrow (from hour 2)", FT1, ST1),
                  ("time left, 2 arrows (from hour 3)", FT2, ST2)]:
    L.append(f"[{tag}]")
    fl, sl = last_per_patient(F), last_per_patient(S)
    L.append(f"   fast: steps={len(F)} patients={len(fl)}   stable: steps={len(S)} patients={len(sl)}")
    for lim in [0, 2, 4]:
        lab = "MAP <= 65 now" if lim == 0 else f"<= {lim} h"
        L.append(f"   {lab:14s} per step: fast {(F.v <= lim).mean():.3f}  stable {(S.v <= lim).mean():.3f}"
                 f"   | last per patient: fast {(fl <= lim).mean():.3f}  stable {(sl <= lim).mean():.3f}")
    fin_f, fin_s = F.v[np.isfinite(F.v) & (F.v > 0)], S.v[np.isfinite(S.v) & (S.v > 0)]
    L.append(f"   median time left when falling: fast {fin_f.median():.2f} h  stable {fin_s.median():.2f} h")
    L.append(f"   share falling at all: fast {np.isfinite(F.v).mean():.3f}  stable {np.isfinite(S.v).mean():.3f}")
    L.append("")

text = "\n".join(L)
print(text)
open(OUT, "w").write(text + "\n")
