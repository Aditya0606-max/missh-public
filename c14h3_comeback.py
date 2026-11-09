import pandas as pd, numpy as np
src = open("c14h_naveen.py").read(); exec(src.split('print(f"Naveens')[0])
R = pd.read_csv("naveen_kind.csv")[["icustay_id", "route"]].set_index("icustay_id")
W = W[(W.who != "Naveen") | (W.hour < np.ceil(W.tip))]
F = W[(W.hour <= 2) & (W.road >= 0.6)].sort_values("hour").groupby("icustay_id").first()[["who", "hour", "road", "tip"]]
nxt = W[["icustay_id", "hour", "road"]].rename(columns={"road": "next_road"}); nxt["hour"] -= 1
F = F.reset_index().merge(nxt, on=["icustay_id", "hour"], how="left").set_index("icustay_id")
F["has_next"] = F.next_road.notna(); F["back"] = F.has_next & (F.next_road <= F.road - 0.1)
F["grp"] = F.who; F.loc[F.who == "Naveen", "grp"] = "Naveen " + R.route.reindex(F.index[F.who == "Naveen"]).values
print("Flagged at arrival (road >= 0.6 in hours 0-2): who came back at the next reading")
print(F.groupby("grp").agg(flagged=("who", "size"), has_next=("has_next", "mean"),
      came_back=("back", lambda s: s[F.loc[s.index, "has_next"]].mean())).round(2).to_string(), "\n")
F["red2"] = F.has_next & ~F.back
nN = N.icustay_id.nunique(); Nf2 = F[F.who == "Naveen"]
ok = Nf2.red2 & (Nf2.hour + 1 < Nf2.tip)
print(f"Two-reading red (flagged, not back at next reading):")
print(f"  Naveens caught before tip {ok.sum() / nN:.2f} ({ok.sum()}/{nN}), median lead {(Nf2.tip - Nf2.hour - 1)[ok].median():.1f} h")
print(f"  Flagged Naveens who tipped before a next reading: {(~Nf2.has_next).sum()} | by route caught: " +
      ", ".join(f"{r} {(ok & (R.route.reindex(Nf2.index) == r)).sum() / (R.route.reindex(N.icustay_id.unique()) == r).sum():.2f}" for r in ["pressor first", "both", "vent first"]))
nA = A.icustay_id.nunique(); Af = F[F.who == "Ajay"]
print(f"  Arriving Ajays flagged at arrival {len(Af) / nA:.2f}; given two-reading red {Af.red2.sum() / nA:.2f}")
back = Af[Af.back].index
print(f"  Ajays who came back after an arrival flag: {len(back)} (all survived without escalation, by definition of Ajay)")
