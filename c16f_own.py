import pandas as pd, numpy as np
src = open("c16c_ward.py").read(); exec(src.split('\nA = L[L.who == "Ajay"]; W')[0])
g = L.groupby("icustay_id")
F3 = [c + "3" for c in FC]
for c in FC: L[c + "3"] = g[c].transform(lambda s: s.rolling(3, min_periods=1).mean())
for c in F3: L["p_" + c] = g[c].shift(1)
A = L[L.who == "Ajay"]
def nz(v): return np.nan_to_num(np.asarray(v, float), nan=-np.inf)
def st(D, lines, prev=False): return np.column_stack([nz(D[("p_" if prev else "") + c].values) >= t for c, t in lines.items()]).any(axis=1)
def cost(lines): return np.sum(st(A, lines) & ~st(A, lines, True)) / days["Ajay"]
def line1(col, b):
    cand = np.unique(np.nanquantile(A[col].values, np.linspace(0.5, 0.9999, 150)))
    return next((c for c in cand if cost({col: c}) <= b), np.inf)
def own(b):
    for q in np.linspace(0.5, 0.9999, 300):
        ln = {c: np.nanquantile(A[c].values, q) for c in F3}
        if cost(ln) <= b: return ln
    return None
raw = lambda ln: {"MAP <=": round(75 - ln["f_mp3"] * 17, 1), "SI >=": round(0.71 + ln["f_si3"] * 0.25, 2), "PP <=": round(58 - ln["f_pp3"] * 15, 1)}
shp = pd.read_csv("c10_shapes.csv")[["icustay_id", "shape"]].set_index("icustay_id")["shape"]
T14 = pd.read_csv("c14g_kranthi.csv", index_col=0)
Kd = L[L.who == "Kranthi"]; last6 = Kd[Kd.hour >= np.ceil(Kd.tip) - 6].groupby("icustay_id").si.mean()
groups = {"Kranthi all": Kd.icustay_id.unique(), "silent heart": shp.index[shp == "silent heart"],
          "low-SI Kranthi": last6.index[last6 < 0.8], "slippers": T14.index[T14.slip]}
def report(lab, lines):
    out, tot = [f"  {lab:36s} cost {cost(lines):.2f}"], 0
    for gl, ids in groups.items():
        D = Kd[Kd.icustay_id.isin(ids)]; tip = D.groupby("icustay_id").tip.first()
        h = D[st(D, lines)].groupby("icustay_id").hour.min().reindex(tip.index); ok = h.notna() & (h < tip)
        out.append(f"{gl} {ok.mean():.2f} (n{len(tip)})")
    for w in ["Kranthi", "Sundar", "mixed"]:
        D = L[L.who == w]; tip = D.groupby("icustay_id").tip.first()
        h = D[st(D, lines)].groupby("icustay_id").hour.min().reindex(tip.index); ok = h.notna() & (h < tip); tot += ok.sum()
        if w != "Kranthi": out.append(f"{w} {ok.mean():.2f}")
    print(" | ".join(out) + f" | TOTAL {tot}"); return tot
for b in (0.4, 1.0):
    print(f"==== Pressure reading alone, budget {b} ====")
    report("leading channel 3-h", {"lead3": line1("lead3", b)})
    ln = own(b)
    if ln: print("    own lines in raw values:", raw(ln)); report("own 3-h line per channel", ln)
    report("MAP alone 3-h", {"f_mp3": line1("f_mp3", b)})
    print()
print("==== Shared setup with S/F (split 0.4 / 0.6, topped up to 1.0); C16c total was 1502 ====")
for k in np.arange(1.0, 2.01, 0.1):
    lp = own(0.4 * k); 
    if lp is None: break
    ln = dict(lp); ln["negsf"] = line1("negsf", 0.6 * k)
    if cost(ln) <= 1.0: ok_ln, ok_k = ln, k
    else: break
print("    own pressure lines in raw values:", raw(ok_ln), "| S/F <=", round(-ok_ln["negsf"], 1))
report(f"own lines + S/F (x{ok_k:.1f})", ok_ln)
