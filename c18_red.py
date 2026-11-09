import pandas as pd, numpy as np
src = open("c16e_wardpace.py").read(); exec(src.split('\nA = L[L.who == "Ajay"]; W')[0])
def nz(v, f=-np.inf): return np.nan_to_num(np.asarray(v, float), nan=f)
L = L.sort_values(["icustay_id", "hour"]).reset_index(drop=True); g = L.groupby("icustay_id")
L["amb"] = (nz(L.lead3) >= 1.5) | (nz(L.negsf) >= -247.5)
blk = (~L.amb).groupby(L.icustay_id).cumsum(); L["run"] = L.amb.groupby([L.icustay_id, blk]).cumsum()
L["lead3_3"] = g.lead3.shift(3); L["negsf_3"] = g.negsf.shift(3)
L["noteasing"] = (nz(L.lead3) >= nz(L.lead3_3, np.inf)) | (nz(L.negsf) >= nz(L.negsf_3, np.inf))
L["dlead"] = L.lead1 - g.lead1.shift(1); L["dsf"] = L.negsf - g.negsf.shift(1)
A = L[L.who == "Ajay"]
def eps(D, s):
    prev = pd.Series(s, index=D.index).groupby(D.icustay_id.values).shift(1).fillna(False).values.astype(bool)
    return np.sum(s & ~prev)
def acost(s): return eps(A, s) / days["Ajay"]
slow = lambda D, Dh, ne: D.amb.values & (D.run.values >= Dh) & (D.noteasing.values if ne else True)
fast_p = lambda D, J: (nz(D.dlead) >= J) & (nz(D.lead1) >= 1.0)
fast_b = lambda D, J: (nz(D.dsf) >= J) & (nz(D.negsf) >= -300)
def pick(fn, cands, b): return next((c for c in cands if acost(fn(A, c)) <= b), None)
D1 = pick(lambda D, d: slow(D, d, False), range(1, 25), 0.2); D2 = pick(lambda D, d: slow(D, d, True), range(1, 25), 0.2)
Jp = pick(fast_p, np.unique(np.nanquantile(A.dlead, np.linspace(0.8, 0.9999, 200))), 0.05)
Js = pick(fast_b, np.unique(np.nanquantile(A.dsf, np.linspace(0.8, 0.9999, 200))), 0.05)
print(f"Slow red: dwell-only D={D1} h, dwell+not-easing D={D2} h | Fast red: pressure jump >= {Jp:.2f}, S/F drop >= {Js:.1f} in 1 h\n")
red = lambda D: slow(D, D2, True) | fast_p(D, Jp) | fast_b(D, Js)
NK = pd.read_csv("naveen_kind.csv")[["icustay_id", "kind", "esc_h"]]
NK = NK[(NK.kind == "medical emergency") & NK.esc_h.between(1, 3)].set_index("icustay_id").esc_h
N = pd.read_csv("naveen_hourly.csv"); N = N[N.icustay_id.isin(NK.index)].copy()
N["si"] = np.where(N.hr.between(20, 250) & N.sbp.between(40, 260), N.hr / N.sbp, np.nan); N["pp"] = N.sbp - N.dbp; N["mp"] = N.mbp
N["lead1"] = ((N[CH] - rec) / (sh - rec)).clip(-0.5, 1.5).max(axis=1).values
N = N.groupby(["icustay_id", "hour"]).lead1.first().reset_index().sort_values(["icustay_id", "hour"])
N["dlead"] = N.lead1 - N.groupby("icustay_id").lead1.shift(1); N["tip"] = N.icustay_id.map(NK); N = N[N.hour < np.ceil(N.tip)]
print("Naveen frame ready:", N.icustay_id.nunique(), "Naveens")
def report(lab, fn):
    out = [f"  {lab:34s} Ajay cost {acost(fn(A)):.2f}"]
    for w in ["Kranthi", "Sundar", "mixed"]:
        D = L[L.who == w]; tip = D.groupby("icustay_id").tip.first()
        h = D[fn(D)].groupby("icustay_id").hour.min().reindex(tip.index); ok = h.notna() & (h < tip)
        am = D[D.amb].groupby("icustay_id").hour.min().reindex(tip.index)
        out.append(f"{w} {ok.mean():.2f} ({(tip - h)[ok].median():.1f} h; amber->red {(h - am)[ok & am.notna()].median():.1f} h)")
    print(" | ".join(out))
report("slow red, dwell only", lambda D: slow(D, D1, False))
report("slow red, dwell + not easing", lambda D: slow(D, D2, True))
report("fast red (pressure or S/F jump)", lambda D: fast_p(D, Jp) | fast_b(D, Js))
report("RED = slow (not easing) OR fast", red)
c_red = acost(red(A))
nh = N[fast_p(N, Jp)].groupby("icustay_id").hour.min(); okN = nh < N.groupby("icustay_id").tip.first().reindex(nh.index)
print(f"  Naveen, fast red (pressure only): caught {okN.sum() / N.icustay_id.nunique():.2f}, lead {(N.groupby('icustay_id').tip.first()[okN[okN].index] - nh[okN]).median():.1f} h\n")
print(f"==== NEWS comparators (red's Ajay cost {c_red:.2f}) ====")
report("NEWS-lite >= 7 (clinical)", lambda D: nz(D.news) >= 7)
cand = np.unique(np.nanquantile(A.news3, np.linspace(0.5, 0.9999, 150)))
tN = next((c for c in cand if acost(nz(A.news3) >= c) <= c_red), np.inf)
report(f"NEWS-lite 3-h at red's cost (>= {tN:.2f})", lambda D: nz(D.news3) >= tN)
