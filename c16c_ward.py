import pandas as pd, numpy as np
src = open("c16d_lead.py").read(); exec(src.split("\nA = L[L.who")[0])
B16 = pd.read_csv("c16_hourly.csv", usecols=["icustay_id", "hour", "negsf", "news2"])
L = L.merge(B16, on=["icustay_id", "hour"], how="left").sort_values(["icustay_id", "hour"]); g = L.groupby("icustay_id")
L["news2_3"] = g.news2.transform(lambda s: s.rolling(3, min_periods=1).mean())
for c in ["negsf", "news2_3", "lead3"]: L["p_" + c] = g[c].shift(1)
A = L[L.who == "Ajay"]; W = ["Kranthi", "Sundar", "mixed"]
def nz(v): return np.nan_to_num(v, nan=-np.inf)
def st(D, lines, prev=False): return np.column_stack([nz(D[("p_" if prev else "") + c].values) >= t for c, t in lines.items()]).any(axis=1)
def cost(lines): return np.sum(st(A, lines) & ~st(A, lines, True)) / days["Ajay"]
def line1(col, b):
    cand = np.unique(np.nanquantile(A[col].values, np.linspace(0.5, 0.9999, 150)))
    return next((c for c in cand if cost({col: c}) <= b), np.inf)
def report(lab, lines):
    out, tot = [f"  {lab:34s} cost {cost(lines):.2f}"], 0
    for w in W:
        D = L[L.who == w]; tip = D.groupby("icustay_id").tip.first()
        h = D[st(D, lines)].groupby("icustay_id").hour.min().reindex(tip.index); ok = h.notna() & (h < tip); tot += ok.sum()
        out.append(f"{w} {ok.mean():.2f} ({(tip - h)[ok].median():.1f} h, through {1 - ok.mean():.2f})")
    print(" | ".join(out) + f" | TOTAL warned {tot}"); return tot
print("==== Each reading alone, and NEWS, at cost <= 1.0 ====")
report("pressure: leading channel 3-h", {"lead3": line1("lead3", 1.0)})
report("breathing: S/F", {"negsf": line1("negsf", 1.0)})
tN = report("NEWS-lite, 3-h", {"news3": line1("news3", 1.0)})
tN2 = report("NEWS with O2, 3-h", {"news2_3": line1("news2_3", 1.0)})
print("\n==== Shared setup: pressure share of budget, topped up to cost 1.0 ====")
best = (-1, None, None)
for s in np.round(np.arange(0.2, 0.81, 0.1), 1):
    k_ok = 1.0
    for k in np.arange(1.0, 2.01, 0.1):
        ln = {"lead3": line1("lead3", 1.0 * s * k), "negsf": line1("negsf", 1.0 * (1 - s) * k)}
        if cost(ln) <= 1.0: k_ok, ln_ok = k, ln
        else: break
    tot = report(f"pressure {s:.1f} / breathing {1 - s:.1f} (x{k_ok:.1f})", ln_ok)
    if tot > best[0]: best = (tot, s, ln_ok)
print(f"\nBEST split (to freeze): pressure {best[1]:.1f} / breathing {1 - best[1]:.1f}; lines {({k: round(v, 3) for k, v in best[2].items()})}; "
      f"total warned {best[0]} vs NEWS-lite {tN}, NEWS with O2 {tN2}")
