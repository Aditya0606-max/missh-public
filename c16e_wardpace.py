import pandas as pd, numpy as np
src = open("c16c_ward.py").read(); exec(src.split('\nA = L[L.who == "Ajay"]; W')[0])
L["sf"] = -L.negsf
rng = np.random.default_rng(7); ids = L.icustay_id.unique(); off = pd.Series(rng.integers(0, 4, len(ids)), index=ids)
obs = (L.hour % 4) == L.icustay_id.map(off)
cols = FC + ["sf", "news"]
Wp = L[cols].where(obs, axis=0); Wp["icustay_id"] = L.icustay_id.values
Wp = Wp.groupby("icustay_id")[cols].ffill(limit=3)
g = L.assign(**{c + "_w": Wp[c].values for c in cols}).groupby("icustay_id")
L["lead1_w"] = Wp[FC].max(axis=1).values
L["lead3_w"] = L.groupby("icustay_id").lead1_w.transform(lambda s: s.rolling(3, min_periods=1).mean())
L["negsf_w"] = -Wp["sf"].values; L["news_w"] = Wp["news"].values
L["news3_w"] = L.groupby("icustay_id").news_w.transform(lambda s: s.rolling(3, min_periods=1).mean())
for c in ["lead3_w", "negsf_w", "news_w", "news3_w"]: L["p_" + c] = L.groupby("icustay_id")[c].shift(1)
A = L[L.who == "Ajay"]; W = ["Kranthi", "Sundar", "mixed"]
def nz(v): return np.nan_to_num(v, nan=-np.inf)
def st(D, lines, prev=False): return np.column_stack([nz(D[("p_" if prev else "") + c].values) >= t for c, t in lines.items()]).any(axis=1)
def cost(lines): return np.sum(st(A, lines) & ~st(A, lines, True)) / days["Ajay"]
def line1(col, b):
    cand = np.unique(np.nanquantile(A[col].values, np.linspace(0.5, 0.9999, 150)))
    return next((c for c in cand if cost({col: c}) <= b), np.inf)
def report(lab, lines):
    out, tot = [f"  {lab:38s} cost {cost(lines):.2f}"], 0
    for w in W:
        D = L[L.who == w]; tip = D.groupby("icustay_id").tip.first()
        h = D[st(D, lines)].groupby("icustay_id").hour.min().reindex(tip.index); ok = h.notna() & (h < tip); tot += ok.sum()
        out.append(f"{w} {ok.mean():.2f} ({(tip - h)[ok].median():.1f} h)")
    print(" | ".join(out) + f" | TOTAL {tot}"); return tot
print(f"Ward pace: observed share of hours {obs.mean():.2f}\n")
print("==== (a) Frozen lines at ward pace ====")
report("frozen: lead3 >= 1.5 OR S/F <= 247.5", {"lead3_w": 1.5, "negsf_w": -247.5})
print("\n==== (b) Re-matched to cost 1.0 at ward pace (split 0.4/0.6, topped up) ====")
for k in np.arange(1.0, 2.01, 0.1):
    ln = {"lead3_w": line1("lead3_w", 0.4 * k), "negsf_w": line1("negsf_w", 0.6 * k)}
    if cost(ln) <= 1.0: ok_ln, ok_k = ln, k
    else: break
report(f"re-matched (x{ok_k:.1f}) lines {({c: round(v, 2) for c, v in ok_ln.items()})}", ok_ln)
print("\n==== (c) NEWS at ward pace ====")
report("NEWS-lite 3-h, cost <= 1.0", {"news3_w": line1("news3_w", 1.0)})
report("NEWS-lite >= 5 (clinical)", {"news_w": 5})
