import pandas as pd, numpy as np
src = open("c16h_vent.py").read(); exec(src.split('print("S/F alarm hours')[0])
L = L.merge(H[["icustay_id", "hour", "hr"]].drop_duplicates(["icustay_id", "hour"]), on=["icustay_id", "hour"], how="left")
L = L.merge(pd.read_csv("c16_hourly.csv", usecols=["icustay_id", "hour", "fio2_src", "F"]), on=["icustay_id", "hour"], how="left")
L = L.merge(pd.read_csv("m3_gcs_hourly.csv"), on=["icustay_id", "hour"], how="left")
L = L.sort_values(["icustay_id", "hour"]).reset_index(drop=True); g = L.groupby("icustay_id")
for c in ["rr", "spo2"]: L[c + "3"] = g[c].transform(lambda s: s.rolling(3, min_periods=1).mean())
L["noF"] = L.fio2_src.fillna("none") == "none"
L["bpos"] = pd.concat([(L.rr3 - 19.0) / 10.0, (97.0 - L.spo23) / 4.7], axis=1).mean(axis=1)
L["gcs_c"] = g.gcs.transform(lambda s: s.ffill(limit=12))
L["news_full"] = L.news + np.where(L.F > 0.21, 2, 0) + np.where(L.gcs_c < 15, 3, 0)
L["nf3"] = L.groupby("icustay_id").news_full.transform(lambda s: s.rolling(3, min_periods=1).mean())
def nz(v): return np.nan_to_num(np.asarray(v, float), nan=-np.inf)
L["fP"] = nz(L.lead3) >= 1.35; L["fS"] = (nz(L.negsf) >= -98.9) & ~L.noF; L["fE"] = (nz(L.bpos) >= 1.06) & L.noF
L["arch"] = L.fP | L.fS | L.fE; L["arch_e"] = L.fP | (nz(L.bpos) >= 1.06)
for c in ["lead3", "negsf", "rr3"]: L[c + "_l3"] = L.groupby("icustay_id")[c].shift(3)
def starts(D, s):
    prev = pd.Series(s, index=D.index).groupby(D.icustay_id.values).shift(1).fillna(False).values.astype(bool); return s & ~prev
A = L[L.who == "Ajay"]; adays = len(A) / 24
c_arch = starts(A, A.arch.values).sum() / adays
cand = np.unique(np.nanquantile(A.nf3, np.linspace(0.5, 0.9999, 200)))
tN = next(c for c in cand if starts(A, nz(A.nf3) >= c).sum() / adays <= c_arch)
L["newsA"] = nz(L.nf3) >= tN
print(f"Frozen alarm Ajay cost {c_arch:.2f}/day | full NEWS line {tN:.2f}, cost {starts(A, L.newsA[A.index].values).sum() / adays:.2f}/day")
print(f"Effort-only variant Ajay cost {starts(A, A.arch_e.values).sum() / adays:.2f}/day\n")
def caught(D, col):
    tip = D.groupby("icustay_id").tip_c.first()
    h = D[D[col].values & (D.hour.values < D.tip_c.values)].groupby("icustay_id").hour.min().reindex(tip.index)
    ok = h.notna() & (h < tip); return ok, (tip - h)[ok]
K = L[L.who == "Kranthi"]; a, la = caught(K, "arch"); n, ln = caught(K, "newsA")
b, c = int((a & ~n).sum()), int((~a & n).sum())
print(f"PRIMARY  Kranthis {len(a)}: architecture {a.mean():.3f} ({la.median():.1f} h) | full NEWS {n.mean():.3f} ({ln.median():.1f} h) | "
      f"difference {a.mean() - n.mean():+.3f} | discordant arch-only {b}, NEWS-only {c}, z {(b - c) / np.sqrt(max(b + c, 1)):.2f}\n")
tot = {"arch": 0, "newsA": 0, "arch_e": 0}
for w in ["Kranthi", "Sundar", "mixed"]:
    D = L[L.who == w]; row = []
    for col in tot:
        ok, ld = caught(D, col); tot[col] += ok.sum(); row.append(f"{col} {ok.mean():.2f} ({ld.median():.1f} h, through {1 - ok.mean():.2f})")
    print(f"  {w:8s} " + " | ".join(row))
print(f"WHOLE-WARD TOTAL: architecture {tot['arch']} | full NEWS {tot['newsA']} | effort-only {tot['arch_e']}\n")
S = L[(L.who == "Sundar") & (L.hour < L.tip_c)]
o2 = S.groupby("icustay_id").noF.apply(lambda s: 1 - s.mean())
band = pd.cut(o2, [-0.01, 0.25, 0.5, 0.75, 1.01], labels=["<25%", "25-50%", "50-75%", ">75%"])
aS, _ = caught(L[L.who == "Sundar"], "arch"); nS, _ = caught(L[L.who == "Sundar"], "newsA")
aS, nS = aS.reindex(band.index), nS.reindex(band.index)
print("SUNDAR by oxygen-recorded share: " + " | ".join(f"{b_} n{int((band == b_).sum())}: arch {aS[band == b_].mean():.2f}, NEWS {nS[band == b_].mean():.2f}"
      for b_ in band.cat.categories))
D = L[L.who.isin(["Kranthi", "Sundar", "mixed"]) & (L.hour < L.tip_c)]
fh = {k: D[D[k]].groupby("icustay_id").hour.min() for k in ["fP", "fS", "fE"]}
F_ = pd.DataFrame(fh).dropna(how="all"); first = F_.idxmin(axis=1).map({"fP": "pressure", "fS": "S/F", "fE": "effort"})
print("FIRST READING (all warned): " + ", ".join(f"{k} {v:.2f}" for k, v in first.value_counts(normalize=True).items()))
allp = L[L.who != "Ajay"]
for col, lab in [("arch", "architecture"), ("newsA", "full NEWS")]:
    st = starts(L, L[col].values); imp = (nz(L.lead3) < nz(L.lead3_l3)) | (nz(L.negsf) < nz(L.negsf_l3)) | (nz(L.rr3) < nz(L.rr3_l3))
    print(f"ON IMPROVING ({lab}): {(st & imp).sum() / max(st.sum(), 1):.2f} of alarm episodes started while improving")
pd_all = len(L) / 24
print(f"LOAD: architecture {starts(L, L.arch.values).sum() / pd_all * 10:.1f} ambers per 20-bed 12-h shift | "
      f"full NEWS {starts(L, L.newsA.values).sum() / pd_all * 10:.1f}\n")
T14 = pd.read_csv("c14g_kranthi.csv", index_col=0); last6 = K[K.hour >= np.ceil(K.tip) - 6].groupby("icustay_id").si.mean()
for lab, ids in [("low-SI Kranthis", last6.index[last6 < 0.8]), ("sudden slippers", T14.index[T14.slip])]:
    ok, ld = caught(K[K.icustay_id.isin(ids)], "arch"); okN, _ = caught(K[K.icustay_id.isin(ids)], "newsA")
    print(f"{lab}: n {len(ok)}, architecture {ok.mean():.2f} ({ld.median():.1f} h), full NEWS {okN.mean():.2f}")
print("\n==== EXPLORATORY: re-check red (amber still present 3 h after each amber episode starts) ====")
rowof = {k: i for i, k in enumerate(zip(L.icustay_id.values, L.hour.values))}
def recheck(col):
    s = L[col].values; on = set(zip(L.icustay_id.values[s], L.hour.values[s])); red = np.zeros(len(L), bool)
    for i in np.where(starts(L, s))[0]:
        k = (L.icustay_id.values[i], L.hour.values[i] + 3)
        if k in on: red[rowof[k]] = True
    return red
L["red_rc"] = recheck("arch"); L["red_rcN"] = recheck("newsA")
A = L[L.who == "Ajay"]
cR = starts(A, A.red_rc.values).sum() / adays; cRN = starts(A, A.red_rcN.values).sum() / adays
cand = np.unique(np.nanquantile(A.nf3, np.linspace(0.5, 0.9999, 300)))
tR = next(c for c in cand if starts(A, nz(A.nf3) >= c).sum() / adays <= cR)
L["redN_alone"] = nz(L.nf3) >= tR
print(f"Red cost per Ajay-day: architecture re-check {cR:.3f} | NEWS re-check {cRN:.3f} | NEWS alone (line {tR:.2f}) "
      f"{starts(A, L.redN_alone[A.index].values).sum() / adays:.3f}")
for col, lab in [("red_rc", "architecture re-check"), ("red_rcN", "NEWS re-check"), ("redN_alone", "NEWS alone, same cost")]:
    out, tot = [], 0
    for w in ["Kranthi", "Sundar", "mixed"]:
        ok, ld = caught(L[L.who == w], col); tot += ok.sum(); out.append(f"{w} {ok.mean():.2f} ({ld.median():.1f} h)")
    print(f"  {lab:24s} " + " | ".join(out) + f" | TOTAL {tot}")
print("\n==== NAVEEN (descriptive; no oxygen or GCS data) ====")
NK = pd.read_csv("naveen_kind.csv"); NK = NK[(NK.kind == "medical emergency") & NK.esc_h.between(1, 3)].set_index("icustay_id")
N = pd.read_csv("naveen_hourly.csv"); N = N[N.icustay_id.isin(NK.index)].copy(); N["tip"] = N.icustay_id.map(NK.esc_h)
N = N[N.hour < np.ceil(N.tip)].groupby(["icustay_id", "hour"]).first().reset_index().sort_values(["icustay_id", "hour"])
N["si"] = np.where(N.hr.between(20, 250) & N.sbp.between(40, 260), N.hr / N.sbp, np.nan); N["pp"] = N.sbp - N.dbp; N["mp"] = N.mbp
N["lead1"] = ((N[CH] - rec) / (sh - rec)).clip(-0.5, 1.5).max(axis=1).values
gN = N.groupby("icustay_id")
N["lead3"] = gN.lead1.transform(lambda s: s.rolling(3, min_periods=1).mean())
for c in ["rr", "spo2"]: N[c + "3"] = gN[c].transform(lambda s: s.rolling(3, min_periods=1).mean())
N["bpos"] = pd.concat([(N.rr3 - 19.0) / 10.0, (97.0 - N.spo23) / 4.7], axis=1).mean(axis=1)
N["archN"] = (nz(N.lead3) >= 1.35) | (nz(N.bpos) >= 1.06)
tipN = N.groupby("icustay_id").tip.first(); hN = N[N.archN].groupby("icustay_id").hour.min().reindex(NK.index)
okN = hN.notna() & (hN < NK.esc_h)
print(f"  Naveens {len(NK)}: caught before tip {okN.mean():.2f} (median {(NK.esc_h - hN)[okN].median():.1f} h); "
      f"no reading before tip {1 - NK.index.isin(tipN.index).mean():.2f}")
for r, g in NK.groupby("route"):
    print(f"    {r:14s} n {len(g):4d}: caught {okN.reindex(g.index).mean():.2f}")
print("\n==== NEWS re-check, matched cost (comparator) ====")
KI = pd.MultiIndex.from_arrays([L.icustay_id.values, L.hour.values])
def recheck_v(s):
    st = starts(L, s); on = pd.Series(s, index=KI)
    ahead = on.reindex(pd.MultiIndex.from_arrays([L.icustay_id.values, L.hour.values + 3])).fillna(False).astype(bool).values
    hit = (np.asarray(st, bool) & ahead); red = np.zeros(len(L), bool)
    tgt = pd.MultiIndex.from_arrays([L.icustay_id.values[hit], L.hour.values[hit] + 3])
    red[KI.get_indexer(tgt)] = True; return red
Aidx = (L.who == "Ajay").values
cand = np.unique(np.nanquantile(L.nf3[Aidx], np.linspace(0.5, 0.9999, 200)))
cand = cand[cand >= tN]
for t in cand:
    red = recheck_v(nz(L.nf3) >= t)
    c = starts(L[Aidx], red[Aidx]).sum() / adays
    if c <= cR: break
L["red_rcNm"] = red
out, tot = [], 0
for w in ["Kranthi", "Sundar", "mixed"]:
    ok, ld = caught(L[L.who == w], "red_rcNm"); tot += ok.sum(); out.append(f"{w} {ok.mean():.2f} ({ld.median():.1f} h)")
print(f"  NEWS amber line {t:.2f}, re-check red cost {c:.3f} (architecture {cR:.3f})")
print("  NEWS re-check, matched  " + " | ".join(out) + f" | TOTAL {tot}")
print("\n==== SECONDARY: S/F-forward versions (previously tested, no new tuning) ====")
hasF_ = ~L.noF.values
VER = {"A (C16c): pressure 1.5 | S/F 247.5": (nz(L.lead3) >= 1.5) | ((nz(L.negsf) >= -247.5) & hasF_),
       "B (C16i): pressure 1.5 | S/F 209 | RR 23.3": (nz(L.lead3) >= 1.5) | ((nz(L.negsf) >= -209) & hasF_) | ((nz(L.rr3) >= 23.3) & ~hasF_)}
S_ = L[(L.who == "Sundar") & (L.hour < L.tip_c)]
o2s = S_.groupby("icustay_id").noF.apply(lambda s: 1 - s.mean())
bandS = pd.cut(o2s, [-0.01, 0.25, 0.5, 0.75, 1.01], labels=["<25%", "25-50%", "50-75%", ">75%"])
for lab, s in VER.items():
    L["_v"] = s; A = L[L.who == "Ajay"]; cv = starts(A, A._v.values).sum() / adays
    cand = np.unique(np.nanquantile(A.nf3, np.linspace(0.3, 0.9999, 300)))
    tv = next((c for c in cand if starts(A, nz(A.nf3) >= c).sum() / adays <= cv), np.inf); L["_n"] = nz(L.nf3) >= tv
    print(f"{lab}: Ajay cost {cv:.2f} | full NEWS matched line {tv:.2f}, cost {starts(A, L._n[A.index].values).sum() / adays:.2f}")
    for col, nm in [("_v", "version"), ("_n", "full NEWS")]:
        out, tot = [], 0
        for w in ["Kranthi", "Sundar", "mixed"]:
            ok, ld = caught(L[L.who == w], col); tot += ok.sum(); out.append(f"{w} {ok.mean():.2f} ({ld.median():.1f} h)")
        okS, _ = caught(L[L.who == "Sundar"], col); okS = okS.reindex(bandS.index)
        print(f"  {nm:10s} " + " | ".join(out) + f" | TOTAL {tot} | Sundar by O2 band: "
              + ", ".join(f"{b} {okS[bandS == b].mean():.2f}" for b in bandS.cat.categories))
print("\n==== PAIRED TIMING (same patients, warned by both; + = architecture earlier) ====")
L["_vB"] = list(VER.values())[1]
def firsth(D, col):
    t = D.groupby("icustay_id").tip_c.first(); h = D[D[col].values & (D.hour.values < D.tip_c.values)].groupby("icustay_id").hour.min()
    return h.reindex(t.index)
def paired(D, col, lab):
    a, n = firsth(D, col), firsth(D, "newsA"); both = a.notna() & n.notna(); d = (n - a)[both]
    if both.sum() == 0: return f"{lab}: none warned by both"
    return (f"{lab}: n {int(both.sum())} | architecture first {(d > 0).mean():.2f}, same hour {(d == 0).mean():.2f}, "
            f"NEWS first {(d < 0).mean():.2f} | median {d.median():+.1f} h")
for w, nm in [("Kranthi", "vasopressor-first"), ("Sundar", "ventilation-first"), ("mixed", "combined")]:
    D = L[L.who == w]
    for col, lab in [("arch", "frozen alarm"), ("_vB", "S/F-forward B")]: print(f"  {nm:18s} {paired(D, col, lab)}")
print("\n==== PRECISION (share of amber episodes starting on a patient who later escalated, before escalation) ====")
for col, lab in [("arch", "frozen alarm"), ("_vB", "S/F-forward B"), ("newsA", "full NEWS")]:
    st = starts(L, L[col].values); real = st & (L.who.values != "Ajay") & (L.hour.values < L.tip_c.values)
    print(f"  {lab:16s} {real.sum() / max(st.sum(), 1):.2f} of {int(st.sum())} episodes")
