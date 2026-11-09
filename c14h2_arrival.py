import pandas as pd, numpy as np
src = open("c14h_naveen.py").read(); exec(src.split('print(f"Naveens')[0])
R = pd.read_csv("naveen_kind.csv")[["icustay_id", "route"]].set_index("icustay_id")
Nb = N[N.hour < np.ceil(N.tip)]
nread = Nb.groupby("icustay_id").road.apply(lambda s: s.notna().sum()).reindex(Nf.index).fillna(0)
print(f"Naveens with no road reading before tip: {(nread == 0).mean():.2f} ({int((nread == 0).sum())}/{len(Nf)})\n")
w = lambda D: D[D.hour <= 2]
aA = w(A).groupby("icustay_id").road.max(); aK = w(Kr).groupby("icustay_id").road.max()
Nw = w(Nb)
def first_cross(D, t): return D[D.road >= t].groupby("icustay_id").hour.min()
rows = []
for t in np.round(np.arange(0.2, 1.21, 0.1), 2):
    fc = first_cross(Nw, t).reindex(Nf.index); lead = (Nf.tip - fc).where(fc.notna())
    row = {"line": t, "Ajays flagged": (aA >= t).mean(), "Kranthis flagged": (aK >= t).mean()}
    for r in ["pressor first", "both", "vent first"]:
        idx = R.index[R.route == r].intersection(Nf.index)
        row[f"{r} caught"] = fc.reindex(idx).notna().mean()
    row["Naveen lead (median h)"] = lead.median()
    rows.append(row)
pd.set_option("display.width", 220)
print("Arrival trade-off (road max in first readings, up to 3 h):\n" + pd.DataFrame(rows).round(2).to_string(index=False), "\n")
nA = w(A).groupby("icustay_id").news.max(); nN = Nw.groupby("icustay_id").news.max().reindex(Nf.index)
for t in (5, 7):
    print(f"NEWS-lite >= {t} at arrival: Ajays flagged {(nA >= t).mean():.2f} | Naveens caught: " +
          ", ".join(f"{r} {(nN.reindex(R.index[R.route == r].intersection(Nf.index)) >= t).mean():.2f}" for r in ["pressor first", "both", "vent first"]))
