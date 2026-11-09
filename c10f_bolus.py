# C10f: does a bolus in hours 6-3 delay the slide / PP signal? Descriptive.
import pandas as pd, numpy as np
src = open("c10e2_lowfloor.py").read()
exec(src.split('nK, nA = (L.who')[0])                     # builds L and T exactly as C10e v2
B = pd.read_csv("m3_bolus.csv"); Gt = pd.read_csv("c13_groups.csv")[["icustay_id", "tip"]]
B = B.merge(Gt, on="icustay_id"); B["hb"] = np.ceil(B.tip) - 1 - np.floor(B.h)
got = set(B[B.hb.between(3, 6)].icustay_id)
T["bolus_6_3"] = T.icustay_id.isin(got)
print("Low-sitting patients with a bolus in hours 6-3:",
      T.drop_duplicates("icustay_id").groupby("who").bolus_6_3.agg(["sum", "size"]).to_dict("index"))
for split, lab in [(True, "BOLUS in hours 6-3"), (False, "NO bolus in hours 6-3")]:
    print(f"\n==== {lab} ====")
    for hb in (4, 2):
        S = T[(T.hb == hb) & (T.bolus_6_3 == split)]; k, a = S[S.who == "Kranthi"], S[S.who == "Ajay"]
        print(f"  {hb} h before (Kranthi {k.icustay_id.nunique()}, Ajay {a.icustay_id.nunique()}): " +
              "  ".join(f"{lab2} {auc(k[f], a[f]):.2f}" for f, lab2 in
                        [("slide", "slide"), ("z_pp", "PP narrowing"), ("z_si", "SI"), ("neg_map", "MAP level")]))
