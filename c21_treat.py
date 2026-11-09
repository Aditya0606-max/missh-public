import pandas as pd, numpy as np
src = open("c25_rehearsal.py").read(); exec(src.split("\ndef caught(")[0])
L["o2step"] = (L.F > L.groupby("icustay_id").F.shift(1) + 0.02).fillna(False)
B = pd.read_csv("m3_bolus.csv")[["icustay_id", "h"]]; B["hour"] = np.floor(B.h).astype(int)
bol = set(zip(B.icustay_id, B.hour)); o2s = set(zip(L.icustay_id[L.o2step], L.hour[L.o2step]))
amb = set(zip(L.icustay_id[L.arch], L.hour[L.arch]))
P = L[L.arch & (L.hour < L.tip_c)].groupby("icustay_id").agg(t0=("hour", "min"), who=("who", "first"), tip=("tip_c", "first"))
rows = []
for sid, r in P.iterrows():
    t0 = int(r.t0); tipped3 = (r.who != "Ajay") and (r.tip <= t0 + 3)
    tb = any((sid, t) in bol for t in range(t0, t0 + 3)); to = any((sid, t) in o2s for t in range(t0, t0 + 3))
    still = (sid, t0 + 3) in amb
    rows.append(dict(id=sid, who=r.who, tip=r.tip, t0=t0, treated=tb or to, bolus=tb, o2=to, tipped3=tipped3,
                     back=(not tipped3) and (not still), still=(not tipped3) and still))
R = pd.DataFrame(rows); R["R"] = R.treated & R.still; R["lead_R"] = np.where(R.R & (R.who != "Ajay"), R.tip - (R.t0 + 3), np.nan)
R["lead_S"] = np.where(R.still & (R.who != "Ajay"), R.tip - (R.t0 + 3), np.nan)
print("Per group, among patients with a first amber before the tip:\n")
for w, g in R.groupby("who"):
    tr, un = g[g.treated], g[~g.treated]
    print(f"  {w:8s} n {len(g):5d} | treated within 2 h {g.treated.mean():.2f} (bolus {g.bolus.mean():.2f}, O2 step {g.o2.mean():.2f}) | "
          f"came back by +3 h: treated {tr.back.mean():.2f}, untreated {un.back.mean():.2f} | tipped within 3 h {g.tipped3.mean():.2f}")
    print(f"           treated & not back (R) {g.R.mean():.2f}" + (f", median {np.nanmedian(g.lead_R):.1f} h before tip" if w != "Ajay" else "")
          + f" | still amber at +3 h (any) {g.still.mean():.2f}" + (f", median {np.nanmedian(g.lead_S):.1f} h before tip" if w != "Ajay" else ""))
adays = (L.who == "Ajay").sum() / 24; Aj = R[R.who == "Ajay"]
print(f"\nCost on Ajays: R {Aj.R.sum() / adays:.3f} per Ajay-day ({int(Aj.R.sum())} Ajays) | still-amber-any {Aj.still.sum() / adays:.3f} per Ajay-day")
for w in ["Kranthi", "Sundar", "mixed"]:
    tot = (L.who == w).groupby(L.icustay_id).any().sum() if False else L[L.who == w].icustay_id.nunique()
    g = R[R.who == w]
    print(f"  {w:8s} of ALL {tot}: R flags {g.R.sum() / tot:.2f} | still-amber-any flags {g.still.sum() / tot:.2f}")
