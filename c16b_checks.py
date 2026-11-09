import pandas as pd, numpy as np
L = pd.read_csv("c16_hourly.csv").sort_values(["icustay_id", "hour"])
days = L.groupby("who").size() / 24
g = L.groupby("icustay_id")
BC = ["rr", "spo2"]
rec = L[(L.who == "Ajay") & ((np.ceil(L.tip) - 1 - L.hour).between(0, 11))][BC].median()
sh = L[(L.who == "Sundar") & ((np.ceil(L.tip) - 1 - L.hour) == 0)][BC].median()
FB = ((L[BC] - rec) / (sh - rec)).clip(-0.5, 1.5)
L["nf"] = FB.mean(axis=1); L["nf3"] = g.nf.transform(lambda s: s.rolling(3, min_periods=1).mean())
L["rr3"] = g.rr.transform(lambda s: s.rolling(3, min_periods=1).mean())
L["negspo23"] = -g.spo2.transform(lambda s: s.rolling(3, min_periods=1).mean())
for c in ["nf3", "rr3", "negspo23"]: L["p_" + c] = g[c].shift(1)
A = L[L.who == "Ajay"]
def nz(v): return np.nan_to_num(v, nan=-np.inf)
def cost(col, t): return np.sum((nz(A[col].values) >= t) & (nz(A["p_" + col].values) < t)) / days["Ajay"]
def line(col, b):
    cand = np.unique(np.nanquantile(A[col].values, np.linspace(0.5, 0.9999, 300)))
    return next((c for c in cand if cost(col, c) <= b), np.inf)
def first(D, col, t): return D[nz(D[col].values) >= t].groupby("icustay_id").hour.min()
print("No-FiO2 anchors recovery:", rec.round(1).to_dict(), "| Sundar end:", sh.round(1).to_dict(), "\n")
S = L[L.who == "Sundar"]; tipS = S.groupby("icustay_id").tip.first()
S2 = S.assign(prevF=S.groupby("icustay_id").F.shift(1))
step = S2[(S2.F > S2.prevF + 0.02)].groupby("icustay_id").hour.min().reindex(tipS.index)
print(f"Sundars with an oxygen step-up before tip: {(step.notna() & (step < tipS)).mean():.2f}")
for b in (0.44, 1.0):
    t = line("negsf", b); h = first(S, "negsf", t).reindex(tipS.index); ok = h.notna() & (h < tipS)
    before = ok & (step.isna() | (h < step)); gap = (step - h)[ok & step.notna() & (h < step)]
    print(f"  S/F at budget {b}: Sundars warned {ok.mean():.2f}; warned BEFORE first O2 step-up {before.sum() / max(ok.sum(), 1):.2f} "
          f"of warned (median {gap.median():.1f} h before); at or after step-up {(ok & ~before).sum() / max(ok.sum(), 1):.2f}")
print()
SC = [("negsf", "S/F"), ("nf3", "RR+SpO2 road (no FiO2)"), ("rr3", "RR alone"), ("negspo23", "SpO2 alone")]
for b in (0.44, 1.0):
    print(f"==== Budget {b} ====")
    for col, lab in SC:
        t = line(col, b); out = [f"  {lab:24s} cost {cost(col, t):.2f}"]
        for w in ["Sundar", "Kranthi", "mixed"]:
            D = L[L.who == w]; tip = D.groupby("icustay_id").tip.first(); h = first(D, col, t).reindex(tip.index)
            ok = h.notna() & (h < tip); out.append(f"{w} {ok.mean():.2f} ({(tip - h)[ok].median():.1f} h)")
        print(" | ".join(out))
    print()
print("==== Both readings on every patient: pressure road3 + S/F, each at half the budget, either fires ====")
for b in (0.44, 1.0):
    tr, ts = line("road3", b / 2), line("negsf", b / 2)
    st = lambda D, p="": (nz(D[p + "road3"].values) >= tr) | (nz(D[p + "negsf"].values) >= ts)
    c = np.sum(st(A) & ~st(A, "p_")) / days["Ajay"]; out = [f"  budget {b} (actual {c:.2f})"]
    for w in ["Kranthi", "Sundar", "mixed"]:
        D = L[L.who == w]; tip = D.groupby("icustay_id").tip.first()
        h = D[st(D)].groupby("icustay_id").hour.min().reindex(tip.index); ok = h.notna() & (h < tip)
        out.append(f"{w} warned {ok.mean():.2f}, sneaked through {1 - ok.mean():.2f}")
    print(" | ".join(out))
