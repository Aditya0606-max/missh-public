-- outcome_01.sql — one outcome label per calibration patient (ENDPOINT_RULE.md
-- dfb9ed9, A9, A10, A11). Committed before execution.
-- Comfort care: Code Status itemids 223758, 228687, value containing "comfort".
-- DNI: same itemids, value containing "dni" or "do not intubate" (recorded,
-- not used for labelling; results reported with and without DNI, A11).

CREATE TABLE `project-688c444c-3632-4faa-a13.missh.outcome_cal` AS
WITH cohort AS (
  SELECT s.stay_id, i.subject_id, i.hadm_id, i.icu_intime, i.icu_outtime,
         i.hospital_expire_flag
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
  SELECT c.stay_id, c.subject_id, c.hadm_id, c.icu_intime, c.icu_outtime,
         c.hospital_expire_flag,
         MIN(IF(e.starttime <= DATETIME_ADD(c.icu_intime, INTERVAL 3 HOUR),
                e.starttime, NULL)) AS t_early,
         MIN(IF(e.starttime >  DATETIME_ADD(c.icu_intime, INTERVAL 3 HOUR),
                e.starttime, NULL)) AS t_esc
  FROM cohort c
  LEFT JOIN events e USING (stay_id)
  GROUP BY c.stay_id, c.subject_id, c.hadm_id, c.icu_intime, c.icu_outtime,
           c.hospital_expire_flag
),
pts AS (
  SELECT f.*
  FROM flags f
  JOIN `project-688c444c-3632-4faa-a13.missh.split_reg1` sp USING (subject_id)
  WHERE f.t_early IS NULL AND sp.split = 'calibration'
  QUALIFY ROW_NUMBER() OVER (PARTITION BY f.subject_id ORDER BY f.icu_intime) = 1
),
rescue_events AS (
  SELECT v.stay_id, v.starttime AS t
  FROM `physionet-data.mimiciv_3_1_derived.ventilation` v
  JOIN pts p USING (stay_id)
  WHERE v.ventilation_status IN ('NonInvasiveVent', 'HFNC')
  UNION ALL
  SELECT r.stay_id, r.charttime AS t
  FROM `physionet-data.mimiciv_3_1_derived.rrt` r
  JOIN pts p USING (stay_id)
  WHERE r.dialysis_active = 1
),
rescue AS (
  SELECT stay_id, MIN(t) AS t_res FROM rescue_events GROUP BY stay_id
),
code_status AS (
  SELECT ce.stay_id, ce.charttime, LOWER(ce.value) AS v
  FROM `physionet-data.mimiciv_3_1_icu.chartevents` ce
  JOIN pts p USING (stay_id)
  WHERE ce.itemid IN (223758, 228687)
),
comfort AS (
  SELECT stay_id, MIN(charttime) AS t_cmo
  FROM code_status WHERE REGEXP_CONTAINS(v, r'comfort')
  GROUP BY stay_id
),
dni AS (
  SELECT stay_id, MIN(charttime) AS t_dni
  FROM code_status WHERE REGEXP_CONTAINS(v, r'dni|do not intubate')
  GROUP BY stay_id
),
death AS (
  SELECT p.stay_id, a.deathtime
  FROM pts p
  JOIN `physionet-data.mimiciv_3_1_hosp.admissions` a ON a.hadm_id = p.hadm_id
  WHERE a.deathtime IS NOT NULL
),
joined AS (
  SELECT p.stay_id, p.icu_intime, p.hospital_expire_flag, p.t_esc,
         r.t_res, c.t_cmo, n.t_dni, d.deathtime,
         DATETIME_ADD(p.icu_intime, INTERVAL 5 HOUR)  AS t5,
         DATETIME_ADD(p.icu_intime, INTERVAL 72 HOUR) AS t72
  FROM pts p
  LEFT JOIN rescue r  USING (stay_id)
  LEFT JOIN comfort c USING (stay_id)
  LEFT JOIN dni n     USING (stay_id)
  LEFT JOIN death d   USING (stay_id)
)
SELECT stay_id,
  CASE
    WHEN t_esc IS NOT NULL AND t_esc <= t5  THEN 'escalated_hyperacute'
    WHEN t_esc IS NOT NULL AND t_esc <= t72 THEN 'escalated'
    WHEN deathtime IS NOT NULL AND deathtime <= t72
         AND (t_cmo IS NULL OR t_cmo > deathtime) THEN 'death_counts'
    WHEN deathtime IS NOT NULL AND deathtime <= t72 THEN 'death_comfort'
    WHEN t_res IS NOT NULL AND t_res <= t72 THEN 'rescued'
    WHEN t_esc IS NOT NULL THEN 'escalated_after_72h'
    WHEN t_res IS NULL AND hospital_expire_flag = 0 THEN 'stable'
    ELSE 'other'
  END AS label,
  ROUND(DATETIME_DIFF(t_esc,     icu_intime, MINUTE) / 60.0, 2) AS esc_h,
  ROUND(DATETIME_DIFF(deathtime, icu_intime, MINUTE) / 60.0, 2) AS death_h,
  ROUND(DATETIME_DIFF(t_res,     icu_intime, MINUTE) / 60.0, 2) AS rescue_h,
  ROUND(DATETIME_DIFF(t_cmo,     icu_intime, MINUTE) / 60.0, 2) AS cmo_h,
  ROUND(DATETIME_DIFF(t_dni,     icu_intime, MINUTE) / 60.0, 2) AS dni_h
FROM joined
