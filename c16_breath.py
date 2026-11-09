import pandas as pd, numpy as np, re
src = open("c14b_budget.py").read(); exec(src.split("A = L[L.who")[0])
V = H[["icustay_id", "hour", "rr", "spo2"]].drop_duplicates(["icustay_id", "hour"])
L = L.merge(V, on=["icustay_id", "hour"], how="left")
E = pd.read_csv("m3_o2_events_all.csv"); E = E[E.icustay_id.isin(L.icustay_id.unique())].copy()
E["hour"] = np.floor(E.h).clip(lower=0).astype(int); E = E.sort_values("h")
last = lambda k, c: E[E.kind == k].groupby(["icustay_id", "hour"])[c].last().rename(k)
O = pd.concat([last("device", "value"), last("flow", "num"), last("fio2", "num")], axis=1).reset_index()
L = L.merge(O, on=["icustay_id", "hour"], how="left").sort_values(["icustay_id", "hour"])
for c in ["device", "flow", "fio2"]: L[c] = L.groupby("icustay_id")[c].ffill(limit=12)
def dev_f(d, fl):
    if not isinstance(d, str): return np.nan
    d = d.lower()
    if re.search(r"endotrach|ett|ventilator", d): return np.nan
    if re.search(r"none|room air", d): return 0.21
    if re.search(r"bipap|cpap|niv|non-invasive", d): return 0.50
    if re.search(r"high flow|hi flow|hfnc|optiflow", d): return 0.60
    if re.search(r"non-rebreather|nonrebreather|nrb", d): return 0.85
    if re.search(r"venti|face tent|aerosol|trach|mask", d): return 0.40
    if re.search(r"cannula|nasal|\bnc\b|oxymizer", d): return min(0.21 + 0.04 * (fl if pd.notna(fl) else 2), 0.44)
    return np.nan
fc = L.fio2.where(L.fio2 <= 1, L.fio2 / 100)
est = np.array([dev_f(d, f) for d, f in zip(L.device.values, L.flow.values)])
L["fio2_src"] = np.where(fc.notna(), "charted", np.where(~np.isnan(est), "estimated", "none"))
L["F"] = np.where(fc.notna(), fc, est)
L["sf"] = L.spo2 / L.F; L["rox"] = L.sf / L.rr
L["news2"] = L.news + np.where(L.F > 0.21, 2, 0)
BC = ["sf", "rr", "F"]
rec = L[(L.who == "Ajay") & ((np.ceil(L.tip) - 1 - L.hour).between(0, 11))][BC].median()
sh = L[(L.who == "Sundar") & ((np.ceil(L.tip) - 1 - L.hour) == 0)][BC].median()
FB = ((L[BC] - rec) / (sh - rec)).clip(-0.5, 1.5)
L["rb"] = FB.mean(axis=1); L["rb3"] = L.groupby("icustay_id").rb.transform(lambda s: s.rolling(3, min_periods=1).mean())
L["negrox"] = -L.rox; L["negsf"] = -L.sf
for c in ["rb3", "news2", "negrox", "negsf"]: L["p_" + c] = L.groupby("icustay_id")[c].shift(1)
print("Breathing anchors recovery:", rec.round(2).to_dict(), "| failure end (Sundar):", sh.round(2).to_dict())
print("FiO2 source share of hours:", L.groupby("who").fio2_src.value_counts(normalize=True).unstack().round(2).to_dict("index"), "\n")
L.to_csv("c16_hourly.csv", index=False)
A = L[L.who == "Ajay"]
def cost(col, t):
    x = np.nan_to_num(A[col].values, nan=-np.inf); p = np.nan_to_num(A["p_" + col].values, nan=-np.inf)
    return np.sum((x >= t) & (p < t)) / days["Ajay"]
SC = [("rb3", "breathing road"), ("road3", "pressure road"), ("news", "NEWS-lite"), ("news2", "NEWS with O2"),
      ("negrox", "ROX"), ("negsf", "S/F")]
for b in (0.44, 1.0):
    print(f"==== Budget {b} episodes per Ajay-day ====")
    for col, lab in SC:
        cand = np.unique(np.nanquantile(A[col].values, np.linspace(0.5, 0.9999, 300)))
        t = next((c for c in cand if cost(col, c) <= b), np.inf)
        out = [f"  {lab:15s} cost {cost(col, t):.2f}"]
        for w in ["Sundar", "Kranthi", "mixed"]:
            D = L[L.who == w]; tip = D.groupby("icustay_id").tip.first()
            hit = D[np.nan_to_num(D[col].values, nan=-np.inf) >= t].groupby("icustay_id").hour.min().reindex(tip.index)
            ok = hit.notna() & (hit < tip)
            out.append(f"{w} {ok.mean():.2f} ({(tip - hit)[ok].median():.1f} h)")
        print(" | ".join(out))
    print()
