import io, contextlib, math
import pandas as pd, numpy as np
buf = io.StringIO()
with contextlib.redirect_stdout(buf): exec(open("eicu_run.py").read())
K = L[L.who == "Kranthi"]; a, _ = caught(K, "arch"); n, _ = caught(K, "newsA")
print(f"Reproduced PRIMARY: architecture {a.mean():.3f} vs NEWS {n.mean():.3f} (registered: 0.845 vs 0.724)\n")
def p_one(b, c):
    m = b + c
    return sum(math.comb(m, k) for k in range(b, m + 1)) / 2 ** m if m else float("nan")
Hs = pd.read_csv("eicu_hosp.csv").set_index("patientunitstayid").hospitalid
Hi = pd.read_csv("eicu_hospital_info.csv").set_index("hospitalid")
Bd = pd.read_csv("eicu_hosp_band.csv").set_index("sid").band
D = pd.DataFrame({"arch": a, "news": n}); D["hosp"] = Hs.reindex(D.index).values
D = D.join(Hi, on="hosp"); D["o2band"] = Bd.reindex(D.index).values
for col, lab in [("region", "Region"), ("numbedscategory", "Bed size"), ("teachingstatus", "Teaching"), ("o2band", "Oxygen charting")]:
    print(f"==== {lab} ====")
    for k, g in D.groupby(D[col].fillna("unknown")):
        b, c = int((g.arch & ~g.news).sum()), int((~g.arch & g.news).sum())
        print(f"  {str(k):20s} n {len(g):4d} | architecture {g.arch.mean():.2f} | NEWS {g.news.mean():.2f} | "
              f"diff {g.arch.mean() - g.news.mean():+.2f} | discordant {b} vs {c} | p {p_one(b, c):.3g}")
    print()
Ph = D.groupby("hosp").agg(n=("arch", "size"), arch=("arch", "mean"), news=("news", "mean"))
Ph = Ph[Ph.n >= 10]; dif = Ph.arch - Ph.news
print(f"==== Hospitals with >= 10 vasopressor-first patients: {len(Ph)} ====")
print(f"  architecture >= NEWS in {(dif >= 0).mean():.2f} of them; difference median {dif.median():+.2f} "
      f"(IQR {dif.quantile(.25):+.2f} to {dif.quantile(.75):+.2f}); worst {dif.min():+.2f}, best {dif.max():+.2f}")
