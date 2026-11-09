import pandas as pd, numpy as np
src = open("c24c_freeze.py").read(); exec(src.split('\nprint(f"FROZEN')[0])
tN = thr_gen("news3", 1.0, lambda D: np.ones(len(D), bool))
S = L[(L.who == "Sundar") & (L.hour < L.tip_c)].copy()
S["fP"] = nzl(S.lead3) >= tp; S["fS"] = (nzl(S.negsf) >= ts) & hasF(S); S["fE"] = (nzl(S.bpos) >= te) & noF(S)
S["arch"] = S.fP | S.fS | S.fE; S["news"] = nzl(S.news3) >= tN
tip = S.groupby("icustay_id").tip_c.first()
P = pd.DataFrame({"tip": tip, "o2share": S.groupby("icustay_id").noF.apply(lambda s: 1 - s.mean())})
for c in ["arch", "news", "fP", "fS", "fE"]: P["h_" + c] = S[S[c]].groupby("icustay_id").hour.min().reindex(P.index)
P["band"] = pd.cut(P.o2share, [-0.01, 0.25, 0.5, 0.75, 1.01], labels=["<25%", "25-50%", "50-75%", ">75%"])
print(f"Sundars {len(P)} (thinned to eICU-like oxygen). Frozen lines: pressure {tp:.2f}, S/F <= {-ts:.0f}, effort {te:.2f}; NEWS-lite {tN:.2f}\n")
print("1) By share of pre-tip hours with oxygen recorded:")
for b, g in P.groupby("band", observed=False):
    a, n = g.h_arch.notna(), g.h_news.notna()
    print(f"   {b:7s} n {len(g):4d} | architecture {a.mean():.2f} ({(g.tip - g.h_arch)[a].median():.1f} h) | NEWS {n.mean():.2f} ({(g.tip - g.h_news)[n].median():.1f} h)")
c = P[P.h_arch.notna()].copy()
first = c[["h_fP", "h_fS", "h_fE"]].idxmin(axis=1).map({"h_fP": "pressure", "h_fS": "S/F", "h_fE": "effort"})
print(f"\n2) First reading to speak, among {len(c)} caught Sundars:")
for r, g in c.groupby(first):
    print(f"   {r:9s} {len(g) / len(c):.2f}  (median {(g.tip - g.h_arch).median():.1f} h before tube)")
S["hb"] = np.ceil(S.tip_c) - 1 - S.hour; S["caught"] = S.icustay_id.map(P.h_arch.notna())
S["SF"] = -S.negsf; S["o2rec"] = ~S.noF
W = S[S.hb.isin([12, 10, 8, 6, 4, 2, 0])]
print("\n3) Last 12 hours, medians (hours before tube): caught vs missed Sundars")
T = W.groupby(["caught", "hb"])[["lead3", "SF", "rr3", "spo23", "bpos", "o2rec"]].median().round(2)
print(T.rename(index={True: "caught", False: "missed"}).to_string())
