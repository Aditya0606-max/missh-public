import pandas as pd, numpy as np
src = open("c16c_ward.py").read(); exec(src.split('\nA = L[L.who == "Ajay"]; W')[0])
def nz(v, f=-np.inf): return np.nan_to_num(np.asarray(v, float), nan=f)
A = L[L.who == "Ajay"].sort_values(["icustay_id", "hour"]).copy()
A["amb"] = (nz(A.lead3) >= 1.5) | (nz(A.negsf) >= -247.5)
prev = A.groupby("icustay_id").amb.shift(1).fillna(False).astype(bool)
A["ep"] = A.amb & ~prev
P = A.groupby("icustay_id").agg(hours=("hour", "size"), eps=("ep", "sum"), max_lead=("lead3", "max"),
                                min_sf=("negsf", lambda s: -s.max() if s.notna().any() else np.nan))
P["first3"] = A[A.hour <= 2].groupby("icustay_id").lead1.max().reindex(P.index)
P["days"] = P.hours / 24; total_eps = P.eps.sum()
print(f"Ajays {len(P)}, Ajay-days {P.days.sum():.0f}, amber episodes per Ajay-day overall {total_eps / P.days.sum():.2f}\n")
def table(col, bins, labels, title):
    b = pd.cut(P[col], bins, labels=labels, right=False)
    T = P.groupby(b, observed=False).agg(ajays=("eps", "size"), days=("days", "sum"), eps=("eps", "sum"))
    T["per_day"] = (T.eps / T.days).round(2); T["share_of_alarms"] = (T.eps / total_eps).round(2)
    print(f"==== {title} ====\n" + T[["ajays", "days", "per_day", "share_of_alarms"]].to_string(), "\n")
pb = [-9, 0.5, 0.8, 1.1, 1.4, 9]; pl = ["<0.5", "0.5-0.8", "0.8-1.1", "1.1-1.4", ">=1.4"]
table("max_lead", pb, pl, "By highest pressure position (leading channel, 3-h)")
table("min_sf", [-1, 200, 250, 300, 400, 9999], ["<200", "200-250", "250-300", "300-400", ">400"], "By lowest S/F")
table("first3", pb, pl, "By pressure position in first 3 hours (fast-start Ajays)")
q = (P.max_lead < 0.5) & (P.min_sf > 300)
print(f"==== Quiet Ajays (pressure < 0.5 and S/F > 300 all stay) ====\n  Ajays {q.sum()}, amber episodes per day "
      f"{P.eps[q].sum() / max(P.days[q].sum(), 1e-9):.3f}, share of all Ajay alarms {P.eps[q].sum() / total_eps:.3f}")
