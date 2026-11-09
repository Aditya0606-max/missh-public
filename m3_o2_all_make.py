# Build O2 extraction for ALL c13 stays (fixes C8-only gap). Same columns as m3_o2_events.csv.
import pandas as pd
ids = ",".join(map(str, pd.read_csv("c13_groups.csv").icustay_id.astype(int)))
sql = f"""
SELECT c.icustay_id,
  DATETIME_DIFF(CAST(c.charttime AS DATETIME), CAST(i.intime AS DATETIME), MINUTE) / 60 AS h,
  CASE WHEN c.itemid IN (467, 226732) THEN 'device'
       WHEN c.itemid IN (470, 471, 223834, 227287) THEN 'flow' ELSE 'fio2' END AS kind,
  IF(c.itemid IN (467, 226732), c.value, NULL) AS value,
  CASE WHEN c.itemid IN (467, 226732) THEN NULL
       WHEN c.itemid IN (190, 3420, 3422, 223835) AND c.valuenum > 1 THEN c.valuenum / 100
       ELSE c.valuenum END AS num
FROM `physionet-data.mimiciii_clinical.chartevents` c
JOIN `physionet-data.mimiciii_clinical.icustays` i USING (icustay_id)
WHERE c.itemid IN (467, 226732, 470, 471, 223834, 227287, 190, 3420, 3422, 223835)
  AND (c.error IS NULL OR c.error != 1)
  AND c.icustay_id IN ({ids})
  AND DATETIME_DIFF(CAST(c.charttime AS DATETIME), CAST(i.intime AS DATETIME), MINUTE) <= 96 * 60
"""
open("m3_o2_all.sql", "w").write(sql)
print("ids:", ids.count(",") + 1)
