import pandas as pd, numpy as np
src = open("c16e_wardpace.py").read(); exec(src.split('\nA = L[L.who == "Ajay"]; W')[0])
L["road_w"] = Wp[FC].mean(axis=1).values
def nzb(v): return np.nan_to_num(np.asarray(v, float), nan=-np.inf)
L["amb_icu"] = (nzb(L.lead3) >= 1.5) | (nzb(L.negsf) >= -247.5)
L["amb_ward"] = (nzb(L.lead3_w) >= 1.42) | (nzb(L.negsf_w) >= -287.88)
L["arr_icu"] = (L.hour <= 2) & (nzb(L.road) >= 0.6); L["arr_ward"] = (L.hour <= 2) & (nzb(L.road_w) >= 0.6)
K4 = ["amb_icu", "amb_ward", "arr_icu", "arr_ward"]
P = {sid: dict(who=g.who.iloc[0], tip=float(g.tip.iloc[0]), T=len(g), **{k: g[k].values.astype(bool) for k in K4})
     for sid, g in L.groupby("icustay_id", sort=False)}
NK = pd.read_csv("naveen_kind.csv")[["icustay_id", "kind", "esc_h"]]
NK = NK[(NK.kind == "medical emergency") & NK.esc_h.between(1, 3)].set_index("icustay_id").esc_h
N = pd.read_csv("naveen_hourly.csv"); N = N[N.icustay_id.isin(NK.index)].copy()
N["si"] = np.where(N.hr.between(20, 250) & N.sbp.between(40, 260), N.hr / N.sbp, np.nan); N["pp"] = N.sbp - N.dbp; N["mp"] = N.mbp
FN = ((N[CH] - rec) / (sh - rec)).clip(-0.5, 1.5); N["lead1"] = FN.max(axis=1).values; N["road"] = FN.mean(axis=1).values
rng0 = np.random.default_rng(11)
for sid, g in N.groupby("icustay_id"):
    tip = float(NK[sid]); T = int(np.ceil(tip)); g = g.groupby("hour")[["lead1", "road"]].first().reindex(range(T))
    keep = (np.arange(T) % 4) == rng0.integers(0, 4)
    lw = pd.Series(np.where(keep, g.lead1.values, np.nan)).ffill(limit=3); rw = pd.Series(np.where(keep, g.road.values, np.nan)).ffill(limit=3)
    hrs = np.arange(T)
    P[sid] = dict(who="Naveen", tip=tip, T=T, amb_icu=nzb(g.lead1.rolling(3, min_periods=1).mean().values) >= 1.5,
                  amb_ward=nzb(lw.rolling(3, min_periods=1).mean().values) >= 1.42,
                  arr_icu=(hrs <= 2) & (nzb(g.road.values) >= 0.6), arr_ward=(hrs <= 2) & (nzb(rw.values) >= 0.6))
pools = {w: [s for s, d in P.items() if d["who"] == w] for w in ["Ajay", "Kranthi", "Sundar", "mixed", "Naveen"]}
print("Pools:", {w: len(v) for w, v in pools.items()})
names = list(pools); probs = np.array([len(pools[w]) for w in names], float); probs /= probs.sum()
print("Real mix:", {w: round(p, 2) for w, p in zip(names, probs)}, "\n")
def run(pace, beds=20, H=720, nsim=100):
    a, r = f"amb_{pace}", f"arr_{pace}"; rng = np.random.default_rng(7)
    shifts, caught = [], []; ae = ah = 0
    for _ in range(nsim):
        bed, pos, first, arrf = [None] * beds, [0] * beds, [None] * beds, [False] * beds
        ns = H // 12; c_amb, c_real, c_arr = np.zeros(ns), np.zeros(ns), np.zeros(ns)
        for h in range(H):
            s = h // 12
            for b in range(beds):
                if bed[b] is None or pos[b] >= P[bed[b]]["T"]:
                    if bed[b] is not None and P[bed[b]]["who"] != "Ajay":
                        p = P[bed[b]]; caught.append((p["who"], first[b], p["tip"]))
                    w = names[rng.choice(len(names), p=probs)]; bed[b] = pools[w][rng.integers(len(pools[w]))]
                    pos[b], first[b], arrf[b] = 0, None, False
                p, t = P[bed[b]], pos[b]
                amb = p[a][t]; prev = p[a][t - 1] if t > 0 else False
                if amb and not prev:
                    c_amb[s] += 1
                    if p["who"] != "Ajay" and t < p["tip"]: c_real[s] += 1
                    if p["who"] == "Ajay": ae += 1
                if p[r][t] and not arrf[b]: c_arr[s] += 1; arrf[b] = True
                if (amb or p[r][t]) and first[b] is None: first[b] = t
                if p["who"] == "Ajay": ah += 1
                pos[b] += 1
        shifts.append((c_amb, c_real, c_arr))
    amb = np.concatenate([x[0] for x in shifts]); real = np.concatenate([x[1] for x in shifts]); arr = np.concatenate([x[2] for x in shifts])
    print(f"==== {pace.upper()} pace, 20-bed ward ====")
    print(f"  Amber alarms per 12-h shift: mean {amb.mean():.1f}, busy shift (90th pct) {np.percentile(amb, 90):.0f}; "
          f"on a patient who later tipped {real.sum() / max(amb.sum(), 1):.2f} | arrival flags per shift {arr.mean():.1f}")
    print(f"  Ajay amber episodes per Ajay-day: {ae / (ah / 24):.2f}")
    C = pd.DataFrame(caught, columns=["who", "first", "tip"]); C["ok"] = C["first"].notna() & (C["first"] < C.tip)
    for w, g in C.groupby("who"):
        print(f"  {w:8s} n {len(g):5d}  caught {g.ok.mean():.2f}  lead {(g.tip - g['first'])[g.ok].median():.1f} h  sneaked through {1 - g.ok.mean():.2f}")
    print()
run("icu"); run("ward")
