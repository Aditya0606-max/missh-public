# anchors_01.py — cohort, target group, yardstick close, T_NEWS, anchor.
# D_PRE_NEWS_BRANCHES (49e83e5), ENDPOINT_RULE (dfb9ed9), A11, A14.
# No architecture measure is computed here.
import numpy as np
import pandas as pd

out = pd.read_csv("../missh_data/outcome_cal.csv")
news = pd.read_csv("../missh_data/news_hourly_cal.csv")
rul = pd.read_csv("../missh_data/rulers_cal_v2.csv")
tiers = pd.read_csv("../missh_data/patient_tiers_cal_v2.csv")

close = (rul[rul.channel.isin(["hr", "map"])]
         .groupby("stay_id").close_h.max().rename("close_h"))
h3 = news[news.hour_idx == 3].set_index("stay_id").news.rename("news_h3")
NW = {sid: g.set_index("hour_idx").news for sid, g in news.groupby("stay_id")}

def cohort(label):
    if label in ("escalated", "death_counts"):
        return "deteriorating"
    if label == "stable":
        return "stable"
    if label == "escalated_hyperacute":
        return "fast"
    return "other"

rows = []
for _, r in out.iterrows():
    sid = r.stay_id
    c = cohort(r.label)
    cl = close.get(sid, np.nan)
    n3 = h3.get(sid, np.nan)
    target = bool(pd.notna(n3) and n3 <= 6)
    event = r.esc_h if r.label == "escalated" else (r.death_h if r.label == "death_counts" else np.nan)
    t_news, anchor, atype, high_at_close = np.nan, np.nan, "", False
    if c == "deteriorating" and pd.notna(cl) and sid in NW:
        s = NW[sid]
        if (cl - 1) in s.index and s[cl - 1] >= 5:
            high_at_close = True
        for h in s.index:
            if h >= cl and s[h] >= 5 and (h + 1) <= event:
                t_news = h + 1
                break
        if pd.notna(t_news):
            anchor, atype = t_news, "news"
        else:
            anchor, atype = event, "event"
    dni_before = bool(pd.notna(r.dni_h) and pd.notna(anchor) and r.dni_h < anchor)
    elig = {k: bool(pd.notna(anchor) and pd.notna(cl) and anchor - k >= cl) for k in (2, 4, 6)}
    rows.append((sid, r.label, c, target, cl, event, t_news, anchor, atype,
                 high_at_close, dni_before, elig[2], elig[4], elig[6]))

A = pd.DataFrame(rows, columns=["stay_id", "label", "cohort", "target", "close_h", "event_h",
                                "t_news", "anchor", "anchor_type", "news_high_at_close",
                                "dni_before", "elig2", "elig4", "elig6"])
A = A.merge(tiers, on="stay_id", how="left")
A.to_csv("../missh_data/anchors_cal.csv", index=False)

L = ["ANCHOR_COUNTS — anchors_01.py, calibration (counts only)", ""]
L.append("Cohort x target group:")
L.append(A.groupby(["cohort", "target"]).size().to_string())
D = A[(A.cohort == "deteriorating") & A.target]
S = A[(A.cohort == "stable") & A.target]
L += ["", f"Target deteriorating: {len(D)}   target stable: {len(S)}",
      f"   anchor = NEWS crossing: {int((D.anchor_type == 'news').sum())}   "
      f"anchor = event (NEWS never crossed): {int((D.anchor_type == 'event').sum())}",
      f"   NEWS already >= 5 when yardstick closed: {int(D.news_high_at_close.sum())}",
      f"   anchor hour median {D.anchor.median():.1f}  IQR {D.anchor.quantile(.25):.1f}-{D.anchor.quantile(.75):.1f}",
      f"   eligible at lookback 2h / 4h / 6h: {int(D.elig2.sum())} / {int(D.elig4.sum())} / {int(D.elig6.sum())}",
      f"   DNI before anchor: {int(D.dni_before.sum())}", "",
      "Target deteriorating by tier (eligible at 2h):"]
for t in ["A", "B", "Cdelayed", "Corigin", "Csparse", "none"]:
    d = D[D.ptier == t]
    L.append(f"   {t:9s} {len(d):4d}  (eligible 2h: {int(d.elig2.sum())})")
L += ["", "Target stable by tier:"]
for t in ["A", "B", "Cdelayed", "Corigin", "Csparse", "none"]:
    L.append(f"   {t:9s} {int((S.ptier == t).sum()):4d}")
text = "\n".join(L)
print(text)
open("ANCHOR_COUNTS.txt", "w").write(text + "\n")
