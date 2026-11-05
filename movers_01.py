# movers_01.py — D_PRE_NEWS_MOVERS breakdown: slow / medium / big at the anchor.
import numpy as np
import pandas as pd

k0 = pd.read_csv("../missh_data/measures_p1_k0.csv", low_memory=False)
p1 = pd.read_csv("../missh_data/measures_p1.csv", low_memory=False)
p2 = pd.read_csv("../missh_data/measures_p2.csv", low_memory=False)
p3 = pd.read_csv("../missh_data/measures_p3.csv", low_memory=False)
S = pd.read_csv("../missh_data/series_dw.csv")

st1 = p1[p1.cohort == "stable"]
l95 = st1.groupby("hour").D_main.quantile(0.95); l99 = st1.groupby("hour").D_main.quantile(0.99)
d0 = k0[k0.cohort == "det"].copy()
d0["l95"], d0["l99"] = d0.hour.map(l95), d0.hour.map(l99)
d0["group"] = np.where(d0.D_main > d0.l99, "big", np.where(d0.D_main > d0.l95, "medium", "slow"))
G = d0.set_index("stay_id").group

def matched_auc(det, st, col):
    det = det.dropna(subset=[col]); out = []
    for _, r in det.iterrows():
        ref = st[(st.tier == r.tier) & st.hour.between(r.hour - 2, r.hour + 2)][col].dropna().values
        if len(ref) >= 30:
            out.append((ref < r[col]).mean() + 0.5 * (ref == r[col]).mean())
    return (np.mean(out), len(out)) if out else (np.nan, 0)

ST = S[S.cohort == "stable"]
def early_rate(sids, q, p):
    line = ST.groupby("hour").dw.quantile(q); hits = 0; n = 0
    for sid in sids:
        g = S[S.stay_id == sid].sort_values("hour"); c = 0; ft = np.nan
        if g.empty: continue
        n += 1
        for _, r in g.iterrows():
            if np.isnan(r.dw) or np.isnan(line.get(r.hour, np.nan)): continue
            c = c + 1 if r.dw > line[r.hour] else max(0, c - 1)
            if c >= p: ft = r.hour + 1; break
        if not np.isnan(ft) and g.anchor.iloc[0] - ft >= 1: hits += 1
    return hits / n if n else np.nan, n

L = ["MOVERS — deteriorating split by distance at the anchor (calibration)",
     f"group sizes: {G.value_counts().to_dict()}", ""]
for grp in ("slow", "medium", "big"):
    sids = set(G[G == grp].index)
    L.append(f"[{grp}] patients {len(sids)}")
    for name, df, col in (("Dw_main", p1, "Dw_main"), ("consist", p2, "consist"), ("share_defend", p3, "share_defend")):
        det = df[(df.cohort == "det") & (df.k == 2) & df.stay_id.isin(sids)]
        a, n = matched_auc(det, df[df.cohort == "stable"], col)
        L.append(f"   2h before, {name:12s} matched AUC {a:.3f} (n={n})")
    for q, p in ((0.90, 1), (0.95, 4)):
        r, n = early_rate(sids, q, p)
        L.append(f"   alarm q={q} p={p}: flagged >=1h early {r:.3f} (n={n})")
    L.append("")
text = "\n".join(L); print(text); open("MOVERS.txt", "w").write(text + "\n")
