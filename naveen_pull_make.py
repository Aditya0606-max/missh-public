import pandas as pd
K = pd.read_csv("naveen_kind.csv")
print("naveen_kind columns:", K.columns.tolist()); print(K.head(3).to_string())
ids = ",".join(map(str, K.icustay_id.astype(int)))
sql = f"""
SELECT v.icustay_id,
  DIV(DATETIME_DIFF(CAST(v.charttime AS DATETIME), CAST(i.intime AS DATETIME), MINUTE), 60) AS hour,
  AVG(v.heartrate) AS hr, AVG(v.sysbp) AS sbp, AVG(v.diasbp) AS dbp, AVG(v.meanbp) AS mbp,
  AVG(v.resprate) AS rr, AVG(v.spo2) AS spo2, AVG(v.tempc) AS temp
FROM `physionet-data.mimiciii_derived.pivoted_vital` v
JOIN `physionet-data.mimiciii_clinical.icustays` i USING (icustay_id)
WHERE v.icustay_id IN ({ids})
  AND CAST(v.charttime AS DATETIME) >= CAST(i.intime AS DATETIME)
  AND DATETIME_DIFF(CAST(v.charttime AS DATETIME), CAST(i.intime AS DATETIME), MINUTE) < 6 * 60
GROUP BY 1, 2
"""
open("naveen_hourly.sql", "w").write(sql); print("ids:", K.shape[0])
