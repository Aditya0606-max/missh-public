# Builds cuff_check.sql: charted BP in the 6 h before each stay's tip.
import pandas as pd
G = pd.read_csv("c13_groups.csv"); G = G[G.tip >= 6]
w = ",".join(f"({int(i)},{t:.4f})" for i, t in zip(G.icustay_id, G.tip))
sql = f"""
WITH w AS (SELECT * FROM UNNEST(ARRAY<STRUCT<icustay_id INT64, tip FLOAT64>>[{w}])),
e AS (
  SELECT DISTINCT c.icustay_id, CAST(c.charttime AS DATETIME) AS t, w.tip,
    IF(c.itemid IN (455, 8441, 456, 220179, 220180, 220181), 'cuff', 'art') AS src,
    DATETIME_DIFF(CAST(c.charttime AS DATETIME), CAST(i.intime AS DATETIME), MINUTE) / 60 AS h
  FROM `physionet-data.mimiciii_clinical.chartevents` c
  JOIN `physionet-data.mimiciii_clinical.icustays` i USING (icustay_id)
  JOIN w USING (icustay_id)
  WHERE c.itemid IN (455, 8441, 456, 220179, 220180, 220181, 51, 8368, 52, 220050, 220051, 220052)
    AND (c.error IS NULL OR c.error != 1) AND c.valuenum > 0
)
SELECT icustay_id, h, tip, src FROM e WHERE h >= tip - 6 AND h < tip
"""
open("cuff_check.sql", "w").write(sql); print("stays:", len(G))
