-- split_01.sql — 20/80 calibration/test split by patient, fixed salt
-- Committed before execution. Salt: 'missh-reg1'. Never changed after commit.
-- Analysable cohort rebuilt with the same rules as funnel_01.sql (f3145f1).

CREATE TABLE `project-688c444c-3632-4faa-a13.missh.split_reg1` AS
WITH cohort AS (
  SELECT s.stay_id, i.subject_id, i.icu_intime
  FROM `physionet-data.mimiciv_3_1_derived.sepsis3` s
  JOIN `physionet-data.mimiciv_3_1_derived.icustay_detail` i
    USING (stay_id)
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
  SELECT
    c.stay_id, c.subject_id,
    MIN(IF(e.starttime <= DATETIME_ADD(c.icu_intime, INTERVAL 3 HOUR),
           e.starttime, NULL)) AS t_early
  FROM cohort c
  LEFT JOIN events e USING (stay_id)
  GROUP BY c.stay_id, c.subject_id
),
analysable_subjects AS (
  SELECT DISTINCT subject_id
  FROM flags
  WHERE t_early IS NULL
)
SELECT
  subject_id,
  IF(MOD(ABS(FARM_FINGERPRINT(CONCAT('missh-reg1-', CAST(subject_id AS STRING)))), 10) < 2,
     'calibration', 'test') AS split
FROM analysable_subjects
