-- news_01.sql — hourly reduced NEWS (HR, SBP, RR, SpO2, temperature)
-- Calibration first analysable stays, hours 0-71 (ENDPOINT_RULE 72 h window).
-- Worst item score within each hour; carry-forward up to 2 h (HR, SBP, RR,
-- SpO2) and 4 h (temperature); hours with missing items flagged incomplete.
-- Committed before execution. Computes no architecture measure.

CREATE TABLE `project-688c444c-3632-4faa-a13.missh.news_hourly_prac` AS
WITH cohort AS (
  SELECT s.stay_id, i.subject_id, i.icu_intime, i.icu_outtime
  FROM `physionet-data.mimiciv_3_1_derived.sepsis3` s
  JOIN `physionet-data.mimiciv_3_1_derived.icustay_detail` i USING (stay_id)
  WHERE s.sepsis3 = TRUE
),
pressor AS (
  SELECT stay_id, starttime
  FROM `physionet-data.mimiciv_3_1_derived.vasoactive_agent`
  WHERE COALESCE(dopamine, epinephrine, norepinephrine,
                 phenylephrine, vasopressin) IS NOT NULL
),
vent AS (
  SELECT stay_id, starttime
  FROM `physionet-data.mimiciv_3_1_derived.ventilation`
  WHERE ventilation_status IN ('InvasiveVent','Tracheostomy')
),
events AS (
  SELECT stay_id, starttime FROM pressor
  UNION ALL
  SELECT stay_id, starttime FROM vent
),
flags AS (
  SELECT c.stay_id, c.subject_id, c.icu_intime, c.icu_outtime,
         MIN(IF(e.starttime <= DATETIME_ADD(c.icu_intime, INTERVAL 3 HOUR),
                e.starttime, NULL)) AS t_early
  FROM cohort c
  LEFT JOIN events e USING (stay_id)
  GROUP BY c.stay_id, c.subject_id, c.icu_intime, c.icu_outtime
),
pts AS (
  SELECT f.*
  FROM flags f
  JOIN `project-688c444c-3632-4faa-a13.missh.split_reg1` sp USING (subject_id)
  WHERE f.t_early IS NULL AND sp.split = 'calibration'
  QUALIFY ROW_NUMBER() OVER (PARTITION BY f.subject_id ORDER BY f.icu_intime) = 1
),
readings AS (
  SELECT v.stay_id,
    DIV(DATETIME_DIFF(v.charttime, p.icu_intime, MINUTE), 60) AS hour_idx,
    CASE WHEN v.heart_rate IS NULL THEN NULL
         WHEN v.heart_rate <= 40 THEN 3 WHEN v.heart_rate <= 50 THEN 1
         WHEN v.heart_rate <= 90 THEN 0 WHEN v.heart_rate <= 110 THEN 1
         WHEN v.heart_rate <= 130 THEN 2 ELSE 3 END AS s_hr,
    CASE WHEN v.sbp IS NULL THEN NULL
         WHEN v.sbp <= 90 THEN 3 WHEN v.sbp <= 100 THEN 2
         WHEN v.sbp <= 110 THEN 1 WHEN v.sbp < 220 THEN 0 ELSE 3 END AS s_sbp,
    CASE WHEN v.resp_rate IS NULL THEN NULL
         WHEN v.resp_rate <= 8 THEN 3 WHEN v.resp_rate <= 11 THEN 1
         WHEN v.resp_rate <= 20 THEN 0 WHEN v.resp_rate <= 24 THEN 2
         ELSE 3 END AS s_rr,
    CASE WHEN v.spo2 IS NULL THEN NULL
         WHEN v.spo2 <= 91 THEN 3 WHEN v.spo2 <= 93 THEN 2
         WHEN v.spo2 <= 95 THEN 1 ELSE 0 END AS s_spo2,
    CASE WHEN v.temperature IS NULL THEN NULL
         WHEN v.temperature <= 35.0 THEN 3 WHEN v.temperature <= 36.0 THEN 1
         WHEN v.temperature <= 38.0 THEN 0 WHEN v.temperature <= 39.0 THEN 1
         ELSE 2 END AS s_temp
  FROM `physionet-data.mimiciv_3_1_derived.vitalsign` v
  JOIN pts p USING (stay_id)
  WHERE v.charttime >= p.icu_intime
    AND v.charttime <  LEAST(p.icu_outtime, DATETIME_ADD(p.icu_intime, INTERVAL 72 HOUR))
),
per_hour AS (
  SELECT stay_id, hour_idx,
         MAX(s_hr) AS s_hr, MAX(s_sbp) AS s_sbp, MAX(s_rr) AS s_rr,
         MAX(s_spo2) AS s_spo2, MAX(s_temp) AS s_temp
  FROM readings
  GROUP BY stay_id, hour_idx
),
grid AS (
  SELECT p.stay_id, hour_idx
  FROM pts p,
  UNNEST(GENERATE_ARRAY(0, LEAST(71,
    DIV(DATETIME_DIFF(p.icu_outtime, p.icu_intime, MINUTE), 60) - 1))) AS hour_idx
),
filled AS (
  SELECT g.stay_id, g.hour_idx,
    LAST_VALUE(h.s_hr IGNORE NULLS) OVER w2   AS s_hr,
    LAST_VALUE(h.s_sbp IGNORE NULLS) OVER w2  AS s_sbp,
    LAST_VALUE(h.s_rr IGNORE NULLS) OVER w2   AS s_rr,
    LAST_VALUE(h.s_spo2 IGNORE NULLS) OVER w2 AS s_spo2,
    LAST_VALUE(h.s_temp IGNORE NULLS) OVER w4 AS s_temp
  FROM grid g
  LEFT JOIN per_hour h USING (stay_id, hour_idx)
  WINDOW
    w2 AS (PARTITION BY g.stay_id ORDER BY g.hour_idx
           ROWS BETWEEN 2 PRECEDING AND CURRENT ROW),
    w4 AS (PARTITION BY g.stay_id ORDER BY g.hour_idx
           ROWS BETWEEN 4 PRECEDING AND CURRENT ROW)
)
SELECT stay_id, hour_idx, s_hr, s_sbp, s_rr, s_spo2, s_temp,
  COALESCE(s_hr,0) + COALESCE(s_sbp,0) + COALESCE(s_rr,0)
    + COALESCE(s_spo2,0) + COALESCE(s_temp,0) AS news,
  (IF(s_hr IS NULL,0,1) + IF(s_sbp IS NULL,0,1) + IF(s_rr IS NULL,0,1)
    + IF(s_spo2 IS NULL,0,1) + IF(s_temp IS NULL,0,1)) AS n_items,
  (s_hr IS NULL OR s_sbp IS NULL OR s_rr IS NULL
    OR s_spo2 IS NULL OR s_temp IS NULL) AS incomplete
FROM filled
