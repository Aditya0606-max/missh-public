import pandas as pd, numpy as np
src = open("c14b_budget.py").read(); exec(src.split("A = L[L.who")[0])
L["jump"] = L.road - L.p_road; L["map_drop"] = L.negmap - L.p_negmap; L["si_rise"] = L.si - L.p_si
A = L[L.who == "Ajay"]; K = L[L.who == "Kranthi"]
def eps(D, col, t):
    x = np.nan_to_num(D[col].values, nan=-np.inf); p = np.nan_to_num(D["p_" + col].values, nan=-np.inf)
    return np.sum((x >= t) & (p < t))
cand = np.unique(np.nanquantile(A.road3.values, np.linspace(0.5, 0.9999, 300)))
tr = next(t for t in cand if eps(A, "road3", t) / days["Ajay"] <= 1.0)
tip = K.groupby("icustay_id").tip.first()
first = lambda m: K[m].groupby("icustay_id").hour.min()
T = pd.DataFrame({"tip": tip, "amb": first(K.road3 >= tr), "n5": first(K.news >= 5)})
def cls(f): return np.where(f.isna(), "never", np.where(T.tip - f >= 2, "early", "late"))
T["road_cls"] = cls(T.amb); T["news_cls"] = cls(T.n5)
print(f"Road amber line {tr:.2f}. Kranthis {len(T)}\n")
print("Road amber class x NEWS>=5 class:\n" + pd.crosstab(T.road_cls, T.news_cls, margins=True).to_string(), "\n")
last = K[K.hour >= np.ceil(K.tip) - 3].groupby("icustay_id")[["jump", "map_drop", "si_rise"]].max()
T = T.join(last); T["slip"] = T.road_cls.isin(["late", "never"])
print("Last 3 h before pressor (medians of each patient's biggest one-hour change):")
print(T.groupby("slip")[["jump", "map_drop", "si_rise"]].median().rename(index={True: "sudden slippers", False: "caught early"}).round(2).to_string(), "\n")
J_c = np.unique(np.nanquantile(A.jump.values, np.linspace(0.8, 0.9999, 300)))
def ft(D, J): return (np.nan_to_num(D.jump.values, nan=-np.inf) >= J) & (np.nan_to_num(D.road.values, nan=-np.inf) >= 0.5)
J = next(j for j in J_c if ft(A, j).sum() / days["Ajay"] <= 0.2)
print(f"Fast track: road jump >= {J:.2f} in one hour and road >= 0.5 | Ajay firing hours/day {ft(A, J).sum() / days['Ajay']:.2f}")
print(f"  Ajay share of hours with a jump that big: {(np.nan_to_num(A.jump.values, nan=-np.inf) >= J).mean():.3f}")
T["ft"] = first(ft(K, J)); T["ft_ok"] = T.ft.notna() & (T.ft < T.tip)
s = T[T.slip]
print(f"  Sudden slippers caught by fast track: {s.ft_ok.sum()} of {len(s)} ({s.ft_ok.mean():.2f}), median lead {(s.tip - s.ft)[s.ft_ok].median():.1f} h")
print(f"  All Kranthis caught by fast track: {T.ft_ok.mean():.2f}")
both = T.amb.notna() | T.ft_ok
print(f"\nAmber OR fast track: Kranthis warned {both.mean():.2f} ({both.sum()}/{len(T)}) vs amber alone {T.amb.notna().mean():.2f}; "
      f"total Ajay cost about {eps(A, 'road3', tr) / days['Ajay'] + ft(A, J).sum() / days['Ajay']:.2f} per day")
T.to_csv("c14g_kranthi.csv")
