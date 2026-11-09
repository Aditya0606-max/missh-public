import pandas as pd, numpy as np
src = open("c14c_ward.py").read(); exec(src.split("Pt = {}")[0])
P = W[["icustay_id", "hour", "road"]].copy(); P["hour"] += 1
W = W.merge(P.rename(columns={"road": "p_road"}), on=["icustay_id", "hour"], how="left"); W["jump"] = W.road - W.p_road
A, N, Kr = W[W.who == "Ajay"], W[W.who == "Naveen"], W[W.who == "Kranthi"]
adays = A.groupby("icustay_id").tip.first().clip(upper=72).apply(np.ceil).sum() / 24
def ftm(D, J): return (np.nan_to_num(D.jump.values, nan=-np.inf) >= J) & (np.nan_to_num(D.road.values, nan=-np.inf) >= 0.5)
J = next(j for j in np.unique(np.nanquantile(A.jump.values, np.linspace(0.8, 0.9999, 300))) if ftm(A, j).sum() / adays <= 0.2)
Nf = N.sort_values("hour").groupby("icustay_id").agg(tip=("tip", "first"),
     first_road=("road", lambda s: s.dropna().iloc[0] if s.notna().any() else np.nan), max_jump=("jump", "max"))
print(f"Naveens {len(Nf)}: first-reading road median {Nf.first_road.median():.2f}; already >= 0.5 at first reading {(Nf.first_road >= 0.5).mean():.2f}; "
      f"max one-hour jump median {Nf.max_jump.median():.2f}")
G14 = pd.read_csv("c14g_kranthi.csv")
print("C14g Kranthis, max one-hour jump in last 3 h (median):", G14.groupby("slip").jump.median().rename(index={True: "sudden slippers", False: "caught early"}).round(2).to_dict())
nj = N[ftm(N, J)].groupby("icustay_id").hour.min(); okj = nj[nj < Nf.tip.reindex(nj.index)]
print(f"\nJump rule (J {J:.2f}, Ajay {ftm(A, J).sum() / adays:.2f} h/day): Naveens caught {len(okj) / len(Nf):.2f}, median lead {(Nf.tip[okj.index] - okj).median():.1f} h")
first3 = lambda D: D[D.hour <= 2].groupby("icustay_id").road.max()
La = first3(A).quantile(0.90)
na = N[(N.hour <= 2) & (N.road >= La)].groupby("icustay_id").hour.min(); oka = na[na < Nf.tip.reindex(na.index)]
print(f"Arrival rule (max road in first 3 h >= {La:.2f}; flags {(first3(A) >= La).mean():.2f} of arriving Ajays): "
      f"Naveens caught {len(oka) / len(Nf):.2f}, median lead {(Nf.tip[oka.index] - oka).median():.1f} h; Kranthis flagged at arrival {(first3(Kr) >= La).mean():.2f}")
print(f"Arrival OR jump: Naveens caught {len(set(okj.index) | set(oka.index)) / len(Nf):.2f}")
