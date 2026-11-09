import pandas as pd, numpy as np
src = open("c16h_vent.py").read(); exec(src.split('print("S/F alarm hours')[0])
E = pd.read_csv("m3_dbsource.csv"); L = L.merge(E, on="icustay_id", how="left")
L = L.merge(pd.read_csv("c16_hourly.csv", usecols=["icustay_id", "hour", "fio2_src"]), on=["icustay_id", "hour"], how="left")
L = L.sort_values(["icustay_id", "hour"]).reset_index(drop=True)
setup = lambda D: (nz(D.lead3) >= 1.5) | (nz(D.negsf) >= -247.5)
news = lambda D: nz(D.news3) >= 4.50
def eps(D, s):
    prev = pd.Series(s, index=D.index).groupby(D.icustay_id.values).shift(1).fillna(False).values.astype(bool)
    return np.sum(s & ~prev)
print("Stays by era:", L.groupby("dbsource").icustay_id.nunique().to_dict(), "\n")
for era, Z in L.groupby("dbsource"):
    A = Z[Z.who == "Ajay"]; ad = len(A) / 24
    print(f"==== {era.upper()} ====  Ajays {A.icustay_id.nunique()}, Ajay-days {ad:.0f}")
    print("  FiO2 source share of hours:", Z.fio2_src.fillna("none").value_counts(normalize=True).round(2).to_dict())
    for lab, fn in [("frozen setup", setup), ("NEWS-lite 3-h >= 4.50", news)]:
        out, tot = [f"  {lab:22s} Ajay cost {eps(A, fn(A)) / max(ad, 1e-9):.2f}"], 0
        for w in ["Kranthi", "Sundar", "mixed"]:
            D = Z[Z.who == w]
            if D.empty: out.append(f"{w} n0"); continue
            tip = D.groupby("icustay_id").tip_c.first(); s = fn(D) & (D.hour.values < D.tip_c.values)
            h = D[s].groupby("icustay_id").hour.min().reindex(tip.index); ok = h.notna() & (h < tip); tot += ok.sum()
            out.append(f"{w} {ok.mean():.2f} (n{len(tip)})")
        print(" | ".join(out) + f" | TOTAL {tot}")
    print()
