# anchors_02.py — as anchors_01, with watching open = 2 for tiers A/B (A15).
import numpy as np
import pandas as pd

out = pd.read_csv("../missh_data/outcome_cal.csv")
news = pd.read_csv("../missh_data/news_hourly_cal.csv")
rul = pd.read_csv("../missh_data/rulers_cal_v3.csv")
tiers = pd.read_csv("../missh_data/patient_tiers_cal_v3.csv")

m = rul[(rul.arm == "main") & rul.channel.isin(["hr", "map"])].copy()
m["open_h"] = np.where(m.tier.isin(["A", "B"]), 2, m.close_h)
open_h = m.groupby("stay_id").open_h.max()
h3 = news[news.hour_idx == 3].set_index("stay_id").news
NW = {sid: g.set_index("hour_idx").news for sid, g in news.groupby("stay_id")}
coh = lambda l: ("deteriorating" if l in ("escalated", "death_counts") else
                 "stable" if l == "stable" else "fast" if l == "escalated_hyperacute" else "other")

rows = []
for _, r in out.iterrows():
    sid, c = r.stay_id, coh(r.label)
    op = open_h.get(sid, np.nan); n3 = h3.get(sid, np.nan)
    target = bool(pd.notna(n3) and n3 <= 6)
    event = r.esc_h if r.label == "escalated" else (r.death_h if r.label == "death_counts" else np.nan)
    t_news, anchor, atype, high = np.nan, np.nan, "", False
    if c == "deteriorating" and pd.notna(op) and sid in NW:
        s = NW[sid]
        high = bool((op - 1) in s.index and s[op - 1] >= 5)
        for h in s.index:
            if h >= op and s[h] >= 5 and (h + 1) <= event:
                t_news = h + 1; break
        anchor, atype = (t_news, "news") if pd.notna(t_news) else (event, "event")
    dni = bool(pd.notna(r.dni_h) and pd.notna(anchor) and r.dni_h < anchor)
    el = {k: bool(pd.notna(anchor) and pd.notna(op) and anchor - k >= op) for k in (2, 4, 6)}
    rows.append((sid, r.label, c, target, op, event, t_news, anchor, atype, high, dni,
                 el[2], el[4], el[6]))

A = pd.DataFrame(rows, columns=["stay_id", "label", "cohort", "target", "open_h", "event_h",
                                "t_news", "anchor", "anchor_type", "news_high_at_open",
                                "dni_before", "elig2", "elig4", "elig6"]).merge(tiers, on="stay_id", how="left")
A.to_csv("../missh_data/anchors_cal_v2.csv", index=False)

D = A[(A.cohort == "deteriorating") & A.target]; S = A[(A.cohort == "stable") & A.target]
L = ["ANCHOR_COUNTS_V2 — anchors_02.py (watching opens at 2 for A/B)",
     f"target deteriorating: {len(D)}   target stable: {len(S)}",
     f"   anchor NEWS: {int((D.anchor_type=='news').sum())}  event: {int((D.anchor_type=='event').sum())}",
     f"   NEWS >= 5 already at watching open: {int(D.news_high_at_open.sum())}",
     f"   anchor median {D.anchor.median():.1f}  IQR {D.anchor.quantile(.25):.1f}-{D.anchor.quantile(.75):.1f}",
     f"   eligible 2h / 4h / 6h: {int(D.elig2.sum())} / {int(D.elig4.sum())} / {int(D.elig6.sum())}",
     f"   DNI before anchor: {int(D.dni_before.sum())}", "", "By tier: deteriorating (elig 2h) | stable"]
for t in ["A", "B", "Cdelayed", "Corigin", "Csparse", "none"]:
    d = D[D.ptier == t]
    L.append(f"   {t:9s} {len(d):4d} ({int(d.elig2.sum()):4d}) | {int((S.ptier == t).sum()):4d}")
text = "\n".join(L); print(text); open("ANCHOR_COUNTS_V2.txt", "w").write(text + "\n")
