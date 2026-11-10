import pandas as pd, numpy as np, os, re
P = os.environ.get("EICU_PREFIX", "eicu")
C = pd.read_csv(f"{P}_cast.csv").rename(columns={"patientunitstayid": "icustay_id"})
V = pd.read_csv(f"{P}_hourly.csv").rename(columns={"patientunitstayid": "icustay_id"})
C["vent_h"] = C.vent_h.where(C.vent_h < 1e8)
rng = np.random.default_rng(2026)
det = C[C.who.isin(["Kranthi", "Sundar", "mixed"]) & C.tip.between(5, 72)].tip.values
aj = (C.who == "Ajay").values
C.loc[aj, "tip"] = np.minimum(rng.choice(det, aj.sum()), C.loc[aj, "los_h"].values)
C = C[C.tip > 0].copy(); C["tip_c"] = C.tip
cols = ["hr", "rr", "spo2", "temp", "sbp", "dbp", "mbp", "fio2", "flow", "device", "gcs"]
Vg = {k: g.set_index("hour")[cols] for k, g in V.groupby("icustay_id")}
rows = []
for r in C.itertuples():
    T = int(min(np.ceil(r.tip), 72))
    b = Vg.get(r.icustay_id, pd.DataFrame(columns=cols)).reindex(range(-12, T))
    for c in ["fio2", "flow", "device", "gcs"]: b[c] = b[c].ffill(limit=12)
    b = b.loc[0:T - 1].reset_index().rename(columns={"index": "hour"})
    b["icustay_id"], b["who"], b["tip"], b["tip_c"], b["vaso_h"], b["vent_h"] = r.icustay_id, r.who, r.tip, r.tip_c, r.vaso_h, r.vent_h
    rows.append(b)
L = pd.concat(rows, ignore_index=True).sort_values(["icustay_id", "hour"]).reset_index(drop=True)
for c in ["hr", "rr", "spo2", "temp", "sbp", "dbp", "mbp", "fio2", "flow", "gcs"]: L[c] = pd.to_numeric(L[c], errors="coerce")
print(f"eICU table: {L.icustay_id.nunique()} stays, {len(L)} hours; by group:", L.groupby("who").icustay_id.nunique().to_dict())
def dev_f(d, fl):
    if not isinstance(d, str): return np.nan
    if re.search(r"ventilator|^vent$", d): return np.nan
    if re.search(r"^ra$|^r/a$|room air", d): return 0.21
    if re.search(r"bipap|bi-pap|cpap", d): return 0.50
    if re.search(r"hfnc|high flow", d): return 0.60
    if re.search(r"non-rebreather", d): return 0.85
    if re.search(r"venturi|face mask|simple mask|oxymask|aerosol|trach|^tc$", d): return 0.40
    if re.search(r"nasal cannula|^nc$|oxymizer|oximizer", d): return min(0.21 + 0.04 * (fl if pd.notna(fl) else 2), 0.44)
    return np.nan
est = np.array([dev_f(d, f) for d, f in zip(L.device.values, L.flow.values)], float)
L["fio2_src"] = np.where(L.fio2.notna(), "charted", np.where(~np.isnan(est), "estimated", "none"))
L["F"] = np.where(L.fio2.notna(), L.fio2, est); L["noF"] = L.fio2_src == "none"
L["si"] = np.where(L.hr.between(20, 250) & L.sbp.between(40, 260), L.hr / L.sbp, np.nan); L["pp"] = L.sbp - L.dbp; L["mp"] = L.mbp
CH = ["mp", "si", "pp"]; rec = pd.Series({"mp": 75.0, "si": 0.71, "pp": 58.0}); sh = pd.Series({"mp": 58.0, "si": 0.96, "pp": 43.0})
FR = ((L[CH] - rec) / (sh - rec)).clip(-0.5, 1.5)
g = L.groupby("icustay_id")
L["lead1"] = FR.max(axis=1); L["road"] = FR.mean(axis=1)
for c in ["lead1", "road", "rr", "spo2"]: L[c + "_3"] = g[c].transform(lambda s: s.rolling(3, min_periods=1).mean())
L["lead3"], L["road3"], L["rr3"], L["spo23"] = L.lead1_3, L.road_3, L.rr_3, L.spo2_3
L["negsf"] = -(L.spo2 / L.F)
L["bpos"] = pd.concat([(L.rr3 - 19.0) / 10.0, (97.0 - L.spo23) / 4.7], axis=1).mean(axis=1)
def pts(v, cuts):
    if pd.isna(v): return np.nan
    for lo, hi, p in cuts:
        if lo <= v <= hi: return p
    return 0
RRc = [(-1, 8, 3), (9, 11, 1), (12, 20, 0), (21, 24, 2), (25, 999, 3)]
SPc = [(-1, 91, 3), (92, 93, 2), (94, 95, 1), (96, 101, 0)]
SBc = [(-1, 90, 3), (91, 100, 2), (101, 110, 1), (111, 219, 0), (220, 999, 3)]
HRc = [(-1, 40, 3), (41, 50, 1), (51, 90, 0), (91, 110, 1), (111, 130, 2), (131, 999, 3)]
TPc = [(-1, 35.0, 3), (35.01, 36.0, 1), (36.01, 38.0, 0), (38.01, 39.0, 1), (39.01, 99, 2)]
PP = pd.DataFrame({"a": L.rr.map(lambda v: pts(v, RRc)), "b": L.spo2.map(lambda v: pts(v, SPc)),
                   "c": L.sbp.map(lambda v: pts(v, SBc)), "d": L.hr.map(lambda v: pts(v, HRc)),
                   "e": L.temp.map(lambda v: pts(v, TPc))})
L["news"] = np.where(PP.notna().sum(axis=1) >= 3, PP.sum(axis=1), np.nan); L["gcs_c"] = L.gcs
L["news_full"] = L.news + np.where(L.F > 0.21, 2, 0) + np.where(L.gcs_c < 15, 3, 0)
L["nf3"] = L.groupby("icustay_id").news_full.transform(lambda s: s.rolling(3, min_periods=1).mean())
K_ = L[L.who == "Kranthi"]; fa = K_[K_.road3 >= 0.53].groupby("icustay_id").hour.min(); tK = K_.groupby("icustay_id").tip.first()
pd.DataFrame({"slip": fa.reindex(tK.index).isna() | ((tK - fa.reindex(tK.index)) < 2)}).to_csv("eicu_slip.csv")
NAVEEN_EICU = r'''print("\n==== NAVEEN (eICU) ====")
okN, ldN = caught(L[L.who == "Naveen"], "arch")
Nn = L[L.who == "Naveen"].groupby("icustay_id")[["vaso_h", "vent_h"]].first().reindex(okN.index)
route = np.where(Nn.vaso_h.notna() & Nn.vent_h.notna() & ((Nn.vaso_h - Nn.vent_h).abs() <= 1), "both",
                 np.where(Nn.vaso_h.fillna(1e9) < Nn.vent_h.fillna(1e9), "pressor first", "vent first"))
print(f"  Naveens {len(okN)}: caught before tip {okN.mean():.2f} (median {ldN.median():.1f} h)")
for r_ in ["pressor first", "both", "vent first"]: print(f"    {r_:14s} n {(route == r_).sum():4d}: caught {okN[route == r_].mean():.2f}")
'''
src = open("c25_rehearsal.py").read()
an = src[src.index("def nz(v)"):]
s0, s1 = an.index('print("\\n==== NAVEEN'), an.index('print("\\n==== NEWS re-check, matched')
an = (an[:s0] + NAVEEN_EICU + "\n" + an[s1:]).replace("c14g_kranthi.csv", "eicu_slip.csv")
exec(an)
print("\n==== VENTILATION-FIRST by hospital oxygen-charting band ====")
HB = pd.read_csv(f"{P}_hosp_band.csv").set_index("sid").band
L["_vA"], L["_vB"] = list(VER.values())[0], list(VER.values())[1]
S_ = L[L.who == "Sundar"]; cats = ["rarely <10%", "sometimes 10-30%", "often 30-60%", "mostly >60%"]
for col, lab in [("arch", "frozen alarm"), ("_vA", "S/F-forward A"), ("_vB", "S/F-forward B"), ("newsA", "full NEWS (frozen cost)")]:
    ok, _ = caught(S_, col); b = HB.reindex(ok.index)
    print(f"  {lab:24s} " + " | ".join(f"{k} {ok[b == k].mean():.2f} (n{int((b == k).sum())})" for k in cats))
