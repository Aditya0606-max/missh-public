# cos_long_01.py — E10: cosine toward shock, only where the arrow is long.
import numpy as np
import pandas as pd

M = pd.read_csv("../missh_data/measures_p1.csv", low_memory=False)
L = ["COS_LONG — cosine with real arrows only (calibration, E10)", ""]
for arm, D, Dw in (("ruler", "D_main", "Dw_main"), ("origin", "D_o", "Dw_o")):
    M[f"cos_{arm}"] = np.where(M[D] > 0, M[Dw] / M[D], np.nan)
    for thr in (1, 3):
        st = M[(M.cohort == "stable") & (M[D] > thr)]
        L.append(f"=== {arm}, arrow > {thr} wobble(s) ===")
        L.append(f"   stable rows kept {len(st)} of {int((M.cohort=='stable').sum())}  "
                 f"median cos {st[f'cos_{arm}'].median():.3f}  share >0.5 {(st[f'cos_{arm}'] > 0.5).mean():.3f}")
        for k in (2, 4, 6):
            dk = M[(M.cohort == "det") & (M.k == k)]
            d = dk[dk[D] > thr]
            pw = []
            for _, r in d.iterrows():
                ref = st[(st.tier == r.tier) & st.hour.between(r.hour - 2, r.hour + 2)][f"cos_{arm}"].dropna().values
                if len(ref) >= 30 and np.isfinite(r[f"cos_{arm}"]):
                    x = r[f"cos_{arm}"]
                    pw.append((ref < x).mean() + 0.5 * (ref == x).mean())
            auc = np.mean(pw) if pw else np.nan
            L.append(f"   {k}h before: det kept {len(d)} of {len(dk)}  median cos {d[f'cos_{arm}'].median():.3f}  "
                     f"share >0.5 {(d[f'cos_{arm}'] > 0.5).mean():.3f}  matched AUC {auc:.3f} (n={len(pw)})")
        L.append("")
text = "\n".join(L); print(text); open("COS_LONG.txt", "w").write(text + "\n")
