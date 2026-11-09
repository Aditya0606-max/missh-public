import pandas as pd, numpy as np
G = pd.read_csv("c13_groups.csv")
H = pd.read_csv("c13d_hourly.csv").merge(G, on="icustay_id")
H = H[(H.hour >= 0) & (H.hour < np.minimum(np.ceil(H.tip), 72))].copy()
H["si"] = np.where(H.hr.between(20, 250) & H.sbp.between(40, 260), H.hr / H.sbp, np.nan)
H["pp"] = H.sbp - H.dbp; H["mp"] = H.mbp
H["hb"] = (np.ceil(H.tip) - 1 - H.hour).astype(int)
CH = ["mp", "si", "pp"]
rec = H[(H.who == "Ajay") & H.hb.between(0, 11)][CH].median(); sh = H[(H.who == "Kranthi") & (H.hb == 0)][CH].median()
F = ((H[CH] - rec) / (sh - rec)).clip(-0.5, 1.5); FC = ["f_mp", "f_si", "f_pp"]; F.columns = FC
H = pd.concat([H, F], axis=1)
line = H[H.who == "Ajay"][FC].quantile(0.90)
print("Anchors recovery:", rec.round(2).to_dict(), "| shock:", sh.round(2).to_dict())
print("Amber lines (Ajay 90th pct of fraction):", line.round(2).to_dict(), "\n")
def pts(v, cuts):
    if pd.isna(v): return np.nan
    for lo, hi, p in cuts:
        if lo <= v <= hi: return p
    return 0
RRc = [(-1, 8, 3), (9, 11, 1), (12, 20, 0), (21, 24, 2), (25, 999, 3)]; SPc = [(-1, 91, 3), (92, 93, 2), (94, 95, 1), (96, 101, 0)]
SBc = [(-1, 90, 3), (91, 100, 2), (101, 110, 1), (111, 219, 0), (220, 999, 3)]; HRc = [(-1, 40, 3), (41, 50, 1), (51, 90, 0), (91, 110, 1), (111, 130, 2), (131, 999, 3)]
TPc = [(-1, 35.0, 3), (35.01, 36.0, 1), (36.01, 38.0, 0), (38.01, 39.0, 1), (39.01, 99, 2)]
P = pd.DataFrame({"a": H.rr.map(lambda v: pts(v, RRc)), "b": H.spo2.map(lambda v: pts(v, SPc)), "c": H.sbp.map(lambda v: pts(v, SBc)),
                  "d": H.hr.map(lambda v: pts(v, HRc)), "e": H.temp.map(lambda v: pts(v, TPc))})
H["news"] = np.where(P.notna().sum(axis=1) >= 3, P.sum(axis=1), np.nan)
H["A"] = (H.si >= 1) & (H.mp <= 65)
H = H.sort_values(["icustay_id", "hour"])
B = pd.read_csv("m3_bolus.csv")[["icustay_id", "h"]]; fb = B[B.h >= 0].groupby("icustay_id").h.min()
def first(s):
    i = np.flatnonzero(s.values); return float(i[0]) if len(i) else np.nan
def eps(s):
    v = s.values.astype(bool); return int(np.sum(v & ~np.r_[False, v[:-1]]))
rows = []
for sid, g in H.groupby("icustay_id"):
    who, tip = g.who.iloc[0], g.tip.iloc[0]; T = int(min(np.ceil(tip), 72))
    g = g.set_index("hour").reindex(range(T))
    pastL = g[FC].ge(line.values); w = g[FC].ge(0.5).sum(axis=1)
    agree = pastL.any(axis=1) & (w >= 3)
    redA = agree & agree.shift(1, fill_value=False)
    dwell = (w >= 2).astype(int).rolling(4).min().fillna(0).astype(bool)
    fade = (g.hr.shift(3) - g.hr) >= 5
    red = redA | (dwell & fade); amber = pastL.any(axis=1)
    news5 = g.news >= 5; ruleA = g.A == True
    road = g[FC].mean(axis=1).rolling(3, min_periods=1).mean()
    rows.append(dict(icustay_id=sid, who=who, tip=tip, hours=T, first_red=first(red), first_amber=first(amber),
        first_news=first(news5), first_A=first(ruleA), eps_red=eps(red), eps_amber=eps(amber), eps_news=eps(news5),
        eps_A=eps(ruleA), first_bolus=fb.get(sid, np.nan), furthest=road.max()))
R = pd.DataFrame(rows)
R.to_csv("c14_replay.csv", index=False); R["days"] = R.hours / 24
AL = [("red", "RED"), ("amber", "amber"), ("news", "NEWS-lite>=5"), ("A", "rule A")]
for w in ["Kranthi", "Sundar", "mixed", "Ajay"]:
    S = R[R.who == w]
    print(f"==== {w} (n {len(S)}, patient-days {S.days.sum():.0f}) ====")
    for k, lab in AL:
        f = S[f"first_{k}"]; lead = (S.tip - f).dropna()
        print(f"  {lab:13s} fired {f.notna().mean():.2f}  median lead {lead.median():5.1f} h  episodes/day {S[f'eps_{k}'].sum() / S.days.sum():.2f}")
K = R[R.who == "Kranthi"]
b = K.dropna(subset=["first_red", "first_news"])
print(f"\nKranthi red vs NEWS-lite>=5 (n {len(b)}): red earlier {(b.first_red < b.first_news).mean():.2f}, same {(b.first_red == b.first_news).mean():.2f}, "
      f"median red lead over NEWS {(b.first_news - b.first_red).median():+.1f} h")
b = K.dropna(subset=["first_red", "first_bolus"])
print(f"Kranthi red vs first bolus (n {len(b)}): red before bolus {(b.first_red < b.first_bolus).mean():.2f}, "
      f"median {(b.first_bolus - b.first_red).median():+.1f} h")
b = K.dropna(subset=["first_news", "first_bolus"])
print(f"Kranthi NEWS-lite>=5 vs first bolus (n {len(b)}): NEWS before bolus {(b.first_news < b.first_bolus).mean():.2f}")
A_ = R[R.who == "Ajay"].copy(); A_["band"] = pd.cut(A_.furthest, [-9, 0.2, 0.4, 0.6, 0.8, 9], labels=["<0.2", "0.2-0.4", "0.4-0.6", "0.6-0.8", "0.8+"])
C = A_.groupby("band", observed=False).agg(ajays=("who", "size"), days=("days", "sum"), red=("eps_red", "sum"), amber=("eps_amber", "sum"))
C["red/day"] = (C.red / C.days).round(3); C["amber/day"] = (C.amber / C.days).round(3)
print("\nAjay false alarms by furthest 3-h road position:\n" + C[["ajays", "days", "red/day", "amber/day"]].to_string())
