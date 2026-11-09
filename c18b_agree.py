import pandas as pd, numpy as np
src = open("c16e_wardpace.py").read(); exec(src.split('\nA = L[L.who == "Ajay"]; W')[0])
def nz(v, f=-np.inf): return np.nan_to_num(np.asarray(v, float), nan=f)
L = L.sort_values(["icustay_id", "hour"]).reset_index(drop=True)
L["amb"] = (nz(L.lead3) >= 1.5) | (nz(L.negsf) >= -247.5)
NK = pd.read_csv("naveen_kind.csv"); NK = NK[(NK.kind == "medical emergency") & NK.esc_h.between(1, 3)]
N = pd.read_csv("naveen_hourly.csv").merge(NK[["icustay_id", "esc_h"]], on="icustay_id").rename(columns={"esc_h": "tip"})
N = N[N.hour < np.ceil(N.tip)].groupby(["icustay_id", "hour"]).first().reset_index().sort_values(["icustay_id", "hour"])
N["si"] = np.where(N.hr.between(20, 250) & N.sbp.between(40, 260), N.hr / N.sbp, np.nan); N["pp"] = N.sbp - N.dbp; N["mp"] = N.mbp
N["lead1"] = ((N[CH] - rec) / (sh - rec)).clip(-0.5, 1.5).max(axis=1).values
PN = pd.DataFrame({"a": N.rr.map(lambda v: pts(v, RRc)), "b": N.spo2.map(lambda v: pts(v, SPc)), "c": N.sbp.map(lambda v: pts(v, SBc)),
                   "d": N.hr.map(lambda v: pts(v, HRc)), "e": N.temp.map(lambda v: pts(v, TPc))})
N["news"] = np.where(PN.notna().sum(axis=1) >= 3, PN.sum(axis=1), np.nan)
gN = N.groupby("icustay_id")
N["lead3"] = gN.lead1.transform(lambda s: s.rolling(3, min_periods=1).mean())
N["news3"] = gN.news.transform(lambda s: s.rolling(3, min_periods=1).mean())
N["amb"] = nz(N.lead3) >= 1.5; N["who"] = "Naveen"
A = L[L.who == "Ajay"]
def eps(D, s):
    prev = pd.Series(s, index=D.index).groupby(D.icustay_id.values).shift(1).fillna(False).values.astype(bool)
    return np.sum(s & ~prev)
def acost(fn): return eps(A, fn(A)) / days["Ajay"]
red = lambda t: (lambda D: D.amb.values & (nz(D.news3) >= t))
alone = lambda t: (lambda D: nz(D.news3) >= t)
cands = np.unique(np.round(A.news3.dropna().values, 2))
pick = lambda mk, b: next((t for t in cands if acost(mk(t)) <= b), np.inf)
def report(lab, fn):
    out, tot = [f"  {lab:34s} Ajay cost {acost(fn):.2f}"], 0
    for w, D in [("Kranthi", L[L.who == "Kranthi"]), ("Sundar", L[L.who == "Sundar"]), ("mixed", L[L.who == "mixed"]), ("Naveen", N)]:
        tip = D.groupby("icustay_id").tip.first(); s = fn(D)
        h = D[s].groupby("icustay_id").hour.min().reindex(tip.index); ok = h.notna() & (h < tip); tot += ok.sum()
        am = D[D.amb.values].groupby("icustay_id").hour.min().reindex(tip.index)
        out.append(f"{w} {ok.mean():.2f} ({(tip - h)[ok].median():.1f} h; amber->red {(h - am)[ok & am.notna()].median():.1f} h)")
    print(" | ".join(out) + f" | TOTAL {tot}")
for b in (0.2, 0.28):
    tr, ta = pick(red, b), pick(alone, b)
    print(f"==== Red budget {b} per Ajay-day ====")
    report(f"RED = amber AND NEWS-3h >= {tr:.2f}", red(tr))
    report(f"NEWS-3h alone >= {ta:.2f}", alone(ta))
    print()
report("NEWS-lite >= 7 (clinical, single hour)", lambda D: nz(D.news) >= 7)
