import pandas as pd, numpy as np
src = open("c16e_wardpace.py").read(); exec(src.split('\nA = L[L.who == "Ajay"]; W')[0])
L = L.sort_values(["icustay_id", "hour"]).copy(); L["MAP"] = -L.negmap; L["SI"] = L.si; L["SF"] = -L.negsf
NK = pd.read_csv("naveen_kind.csv"); NK = NK[(NK.kind == "medical emergency") & NK.esc_h.between(1, 3)]
N = pd.read_csv("naveen_hourly.csv").merge(NK[["icustay_id", "esc_h"]], on="icustay_id").rename(columns={"esc_h": "tip"})
N = N[N.hour < np.ceil(N.tip)].copy(); N["MAP"] = N.mbp; N["SI"] = np.where(N.hr.between(20, 250) & N.sbp.between(40, 260), N.hr / N.sbp, np.nan)
N["SF"] = np.nan; N["who"] = "Naveen"
cols = ["icustay_id", "who", "tip", "hour", "MAP", "SI", "SF"]
D = pd.concat([L[cols], N[cols]], ignore_index=True).sort_values(["icustay_id", "hour"])
g = D.groupby("icustay_id")
for c in ["MAP", "SI", "SF"]: D[c + "3"] = g[c].transform(lambda s: s.rolling(3, min_periods=1).mean())
D = D[(D.who == "Ajay") | (D.hour < np.ceil(D.tip))]
low = {"MAP3": True, "SI3": False, "SF3": True}
worst = D.groupby(["icustay_id", "who"]).agg(**{c: (c, "min" if lw else "max") for c, lw in low.items()}).reset_index()
Aj = worst[worst.who == "Ajay"]
G = {c: (Aj[c].quantile(0.01) if lw else Aj[c].quantile(0.99)) for c, lw in low.items()}
print("Guardian lines (only 1% of Ajays ever hold a 3-h average beyond these):",
      {"MAP <=": round(G["MAP3"], 1), "SI >=": round(G["SI3"], 2), "S/F <=": round(G["SF3"], 0)}, "\n")
cross = lambda c: (D[c] <= G[c]) if low[c] else (D[c] >= G[c])
for w in ["Ajay", "Kranthi", "Sundar", "mixed", "Naveen"]:
    S = D[D.who == w]; tip = S.groupby("icustay_id").tip.first(); out = [f"  {w:8s} n {len(tip):5d}"]
    anyh = None
    for c, lab in [("MAP3", "MAP"), ("SI3", "SI"), ("SF3", "S/F")]:
        h = S[cross(c).loc[S.index]].groupby("icustay_id").hour.min().reindex(tip.index)
        anyh = h if anyh is None else np.fmin(anyh, h)
        if w == "Ajay": out.append(f"{lab} {h.notna().mean():.2f}")
        else:
            ok = h.notna() & (h < tip); out.append(f"{lab} {ok.mean():.2f} ({(tip - h)[ok].median():.1f} h)")
    if w == "Ajay": out.append(f"ANY {anyh.notna().mean():.2f}")
    else:
        ok = anyh.notna() & (anyh < tip); out.append(f"ANY {ok.mean():.2f} ({(tip - anyh)[ok].median():.1f} h before tip)")
    print(" | ".join(out))
