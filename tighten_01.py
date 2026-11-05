# tighten_01.py — remove rescued stays from the phi_hourly_cal export (A9)
import pandas as pd
src = "../missh_data/phi_hourly_cal.csv"
res = pd.read_csv("../missh_data/rescued_stays.csv")
df = pd.read_csv(src)
out = df[~df["stay_id"].isin(res["stay_id"])]
out.to_csv("../missh_data/phi_hourly_cal_tight.csv", index=False)
print(f"stays before: {df['stay_id'].nunique()}  rescued removed: "
      f"{df['stay_id'].isin(res['stay_id']).groupby(df['stay_id']).any().sum()}  "
      f"stays after: {out['stay_id'].nunique()}")
