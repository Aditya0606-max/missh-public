# Cuff check (MIMIC3_COVERAGE_RULE.md). Descriptive.
import pandas as pd, numpy as np
G = pd.read_csv("c13_groups.csv"); G = G[G.tip >= 6]
E = pd.read_csv("cuff_check_events.csv")
E["hb"] = np.floor(E.tip - E.h).clip(0, 5).astype(int)          # 0 = last hour before tip
rows = []
for sid, who in zip(G.icustay_id, G.who):
    e = E[E.icustay_id == sid] if sid in E.icustay_id.values else E.iloc[0:0]
    c, a = e[e.src == "cuff"], e[e.src == "art"]
    rows.append(dict(icustay_id=sid, who=who, cuff_h=c.hb.nunique(), art_h=a.hb.nunique(),
        any_h=e.hb.nunique(), cuff_rate=len(c) / 6,
        cuff_last2=(c.hb <= 1).sum() / 2, cuff_first4=(c.hb >= 2).sum() / 4))
R = pd.DataFrame(rows); R["art_line"] = R.art_h >= 4
def summary(R, title):
    print(f"\n==== {title} ====")
    S = R.groupby("who").agg(stays=("who", "size"), art_line=("art_line", "mean"),
        any_bp_6of6=("any_h", lambda s: (s == 6).mean())).round(2)
    C = R[~R.art_line].groupby("who").agg(cuff_only=("who", "size"),
        cuff_6of6=("cuff_h", lambda s: (s == 6).mean()), cuff_4of6=("cuff_h", lambda s: (s >= 4).mean()),
        cuff_per_h=("cuff_rate", "mean"), last2_per_h=("cuff_last2", "mean"), first4_per_h=("cuff_first4", "mean")).round(2)
    print(S.join(C).to_string())
    if "Ajay" in C.index:
        r = (C.cuff_per_h / C.loc["Ajay", "cuff_per_h"]).round(2)
        print("Cuff readings/hour vs Ajay (cuff-only):", r.to_dict())
        F = r[(r - 1).abs() >= 0.25]
        print("FLAGS:", "none" if F.empty else F.to_dict())
summary(R, "All stays with tip >= 6 h (charted BP)")
try:
    U = pd.read_csv("m3_usable.csv")
    wf = U[(U.tip_h >= 6) & (U.cov_any >= 0.8)].icustay_id
    summary(R[R.icustay_id.isin(wf)], "Waveform-recorded subset (m3_usable: tip >= 6, cov_any >= 0.8)")
except Exception as ex:
    print("\nWaveform subset skipped:", ex)
