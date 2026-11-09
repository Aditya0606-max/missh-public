import pandas as pd, numpy as np
src = open("c14_replay.py").read(); exec(src.split("B = pd.read_csv")[0])
NK = pd.read_csv("naveen_kind.csv")[["icustay_id", "kind", "esc_h"]].rename(columns={"esc_h": "tip"})
N = pd.read_csv("naveen_hourly.csv").merge(NK, on="icustay_id")
N = N[(N.kind == "medical emergency") & N.tip.between(1, 3) & (N.hour < np.ceil(N.tip))].copy()
N["who"] = "Naveen"
N["si"] = np.where(N.hr.between(20, 250) & N.sbp.between(40, 260), N.hr / N.sbp, np.nan); N["pp"] = N.sbp - N.dbp; N["mp"] = N.mbp
FN = ((N[CH] - rec) / (sh - rec)).clip(-0.5, 1.5); FN.columns = FC; N = pd.concat([N, FN], axis=1)
PN = pd.DataFrame({"a": N.rr.map(lambda v: pts(v, RRc)), "b": N.spo2.map(lambda v: pts(v, SPc)), "c": N.sbp.map(lambda v: pts(v, SBc)),
                   "d": N.hr.map(lambda v: pts(v, HRc)), "e": N.temp.map(lambda v: pts(v, TPc))})
N["news"] = np.where(PN.notna().sum(axis=1) >= 3, PN.sum(axis=1), np.nan)
cols = ["icustay_id", "who", "tip", "hour", "news"] + FC
W = pd.concat([H[H.who.isin(["Ajay", "Kranthi"])][cols], N[cols]], ignore_index=True)
W["road"] = W[FC].mean(axis=1)
Pt = {}
for sid, g in W.groupby("icustay_id"):
    end = int(min(np.ceil(g.tip.iloc[0]), 48)); g = g.groupby("hour").first().reindex(range(end))
    if g.who.notna().sum() == 0: continue
    Pt[sid] = dict(who=g.who.dropna().iloc[0], tip=float(g.tip.dropna().iloc[0]), end=end,
                   road=g.road.rolling(3, min_periods=1).mean().ffill().values,
                   news=g.news.rolling(3, min_periods=1).mean().ffill().values)
pools = {w: [s for s, d in Pt.items() if d["who"] == w] for w in ["Ajay", "Kranthi", "Naveen"]}
print("Pools:", {w: len(v) for w, v in pools.items()})
tot = sum(len(v) for v in pools.values())
real = {w: max(1, round(100 * len(v) / tot)) for w, v in pools.items()}
rng = np.random.default_rng(7)
def run(score, mix, nsim=200):
    first, slots, aeps, ahours = [], {"Ajay": 0, "Kranthi": 0, "Naveen": 0}, 0, 0
    for _ in range(nsim):
        pick = [p for w, n in mix.items() for p in rng.choice(pools[w], n, replace=False)]
        fr, prev = {}, set()
        for h in range(48):
            pres = [p for p in pick if h < Pt[p]["end"]]
            if not pres: break
            v = np.array([Pt[p][score][h] for p in pres], float); v = np.where(np.isnan(v), -np.inf, v) + rng.random(len(v)) * 1e-6
            k = max(1, int(np.ceil(0.05 * len(pres)))); top = {pres[i] for i in np.argsort(-v)[:k] if np.isfinite(v[i])}
            for p in top:
                slots[Pt[p]["who"]] += 1; fr.setdefault(p, h)
                if Pt[p]["who"] == "Ajay" and p not in prev: aeps += 1
            ahours += sum(Pt[p]["who"] == "Ajay" for p in pres); prev = top
        first += [(Pt[p]["who"], fr.get(p), Pt[p]["tip"]) for p in pick if Pt[p]["who"] != "Ajay"]
    F_ = pd.DataFrame(first, columns=["who", "first", "tip"]); F_["caught"] = F_["first"].notna() & (F_["first"] < F_.tip)
    out = []
    for w in ["Kranthi", "Naveen"]:
        g = F_[F_.who == w]; out.append(f"{w} red before tip {g.caught.mean():.2f}, lead {(g.tip - g['first'])[g.caught].median():.1f} h")
    s = sum(slots.values()); out.append("red slots " + ", ".join(f"{w} {slots[w] / s:.2f}" for w in slots))
    out.append(f"Ajay red episodes/Ajay-day {aeps / (ahours / 24):.2f}")
    return " | ".join(out)
for mixname, mix in [("30/30/30", {"Ajay": 30, "Kranthi": 30, "Naveen": 30}), (f"real mix {real}", real)]:
    print(f"\n==== Ward {mixname}, top 5% red each hour ====")
    for sc, lab in [("road", "road (3-h)"), ("news", "NEWS-lite (3-h)")]:
        print(f"  {lab:16s} " + run(sc, mix))
