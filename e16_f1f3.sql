-- e16_f1f3.sql — E16: hourly urine output, lactate, base excess for cohort stays (descriptive)
-- hour_idx as in vitals_01.sql: DIV(DATETIME_DIFF(charttime, icu_intime, MINUTE), 60)
WITH st AS (
  SELECT DISTINCT v.stay_id, ie.hadm_id, ie.intime AS icu_intime, ie.outtime AS icu_outtime
  FROM `project-688c444c-3632-4faa-a13.missh.vitals_hourly___SPLIT__` v
  JOIN `physionet-data.mimiciv_3_1_icu.icustays` ie USING (stay_id)
),
uo AS (
  SELECT s.stay_id, DIV(DATETIME_DIFF(u.charttime, s.icu_intime, MINUTE), 60) AS hour_idx,
         SUM(u.urineoutput) AS uo_ml
  FROM st s JOIN `physionet-data.mimiciv_3_1_derived.urine_output` u USING (stay_id)
  WHERE u.charttime >= s.icu_intime AND u.charttime < s.icu_outtime
  GROUP BY 1, 2
),
lab AS (
  SELECT s.stay_id, DIV(DATETIME_DIFF(b.charttime, s.icu_intime, MINUTE), 60) AS hour_idx,
         MAX(b.lactate) AS lactate, MIN(b.baseexcess) AS base_excess,
         COUNTIF(b.lactate IS NOT NULL) AS lac_n
  FROM st s JOIN `physionet-data.mimiciv_3_1_derived.bg` b ON b.hadm_id = s.hadm_id
  WHERE (b.lactate IS NOT NULL OR b.baseexcess IS NOT NULL)
    AND b.charttime >= DATETIME_SUB(s.icu_intime, INTERVAL 6 HOUR)
    AND b.charttime < s.icu_outtime
  GROUP BY 1, 2
)
SELECT COALESCE(uo.stay_id, lab.stay_id) AS stay_id,
       COALESCE(uo.hour_idx, lab.hour_idx) AS hour_idx,
       uo.uo_ml, lab.lactate, lab.base_excess, lab.lac_n
FROM uo FULL OUTER JOIN lab ON uo.stay_id = lab.stay_id AND uo.hour_idx = lab.hour_idx
WHERE COALESCE(uo.hour_idx, lab.hour_idx) BETWEEN -6 AND 96
