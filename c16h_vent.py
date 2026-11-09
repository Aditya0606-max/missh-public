import pandas as pd, numpy as np
src = open("c16c_ward.py").read(); exec(src.split('\nA = L[L.who == "Ajay"]; W')[0])
dv = pd.read_csv("c16_hourly.csv", usecols=["icustay_id", "hour", "device", "spo2", "rr"])
L = L.drop(columns=[c for c in ["device", "spo2", "rr"] if c in L]).merge(dv, on=["icustay_id", "hour"], how="left")
L["vent_dev"] = L.device.astype(str).str.lower().str.contains(r"endotrach|\bett\b|ventilator|intubat", regex=True)
fv = L[L.vent_dev].groupby("icustay_id").hour.min()
L["first_vent"] = L.icustay_id.map(fv); L["tip_c"] = np.fmin(L.tip, L.first_vent.fillna(np.inf))
def nz(v): return np.nan_to_num(np.asarray(v, float), nan=-np.inf)
L["sf_amb"] = nz(L.negsf) >= -247.5; L["amb"] = (nz(L.lead3) >= 1.5) | L.sf_amb
L["has_read"] = L[["spo2", "rr"]].notna().any(axis=1)
print("S/F alarm hours that were vent-device hours:", f"{(L.sf_amb & L.vent_dev).sum()} of {L.sf_amb.sum()} ({(L.sf_amb & L.vent_dev).mean() / max(L.sf_amb.mean(), 1e-9):.2f})")
for w in ["Ajay", "Kranthi", "Sundar", "mixed"]:
    D = L[L.who == w]; t = D.groupby("icustay_id")[["tip", "tip_c"]].first()
    sh_ = (t.tip_c < t.tip); print(f"  {w:8s} tip moved earlier {sh_.mean():.2f} (median {(t.tip - t.tip_c)[sh_].median():.1f} h)")
print()
def catch(D, s, tipcol, before_only):
    tip = D.groupby("icustay_id")[tipcol].first()
    E = D[s & ((D.hour < D[tipcol]) if before_only else True)]
    h = E.groupby("icustay_id").hour.min().reindex(tip.index); ok = h.notna() & (h < tip)
    return ok.mean(), (tip - h)[ok].median()
print("Caught before tip (lead): original vs corrected (only hours before first tube/vent)")
tot_o = tot_c = 0
for w in ["Kranthi", "Sundar", "mixed"]:
    D = L[L.who == w]
    a, la = catch(D, D.amb.values, "tip", False); b, lb = catch(D, D.amb.values, "tip_c", True)
    c, lc = catch(D, D.sf_amb.values, "tip", False); d, ld = catch(D, D.sf_amb.values, "tip_c", True)
    n = D.icustay_id.nunique(); tot_o += a * n; tot_c += b * n
    nr = D[D.hour < D.tip_c].groupby("icustay_id").has_read.any().reindex(D.icustay_id.unique()).fillna(False)
    print(f"  {w:8s} frozen setup {a:.2f} ({la:.1f} h) -> {b:.2f} ({lb:.1f} h) | S/F alone {c:.2f} ({lc:.1f} h) -> {d:.2f} ({ld:.1f} h) "
          f"| no readings before corrected tip {1 - nr.mean():.2f}")
print(f"\n  Frozen setup total warned: original {tot_o:.0f} -> corrected {tot_c:.0f} (C16c reported 1502 incl. this definition)")
A = L[L.who == "Ajay"]; print(f"  Ajay hours with a vent device (should be ~0): {A.vent_dev.mean():.3f}")
