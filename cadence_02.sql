WITH cohort AS (
  SELECT s.stay_id, i.icu_intime
  FROM `physionet-data.mimiciv_3_1_derived.sepsis3` s
  JOIN `physionet-data.mimiciv_3_1_derived.icustay_detail` i USING (stay_id)
  WHERE s.sepsis3 = TRUE
),
pressor AS (
  SELECT stay_id, starttime FROM `physionet-data.mimiciv_3_1_derived.vasoactive_agent`
  WHERE COALESCE(dopamine, epinephrine, norepinephrine,
                 phenylephrine, vasopressin) IS NOT NULL
),
vent AS (
  SELECT stay_id, starttime FROM `physionet-data.mimiciv_3_1_derived.ventilation`
  WHERE ventilation_status IN ('InvasiveVent','Tracheostomy')
),
events AS (
  SELECT stay_id, starttime FROM pressor
  UNION ALL SELECT stay_id, starttime FROM vent
),
analysable AS (
  SELECT c.stay_id, c.icu_intime
  FROM cohort c
  LEFT JOIN events e
    ON e.stay_id = c.stay_id
   AND e.starttime <= DATETIME_ADD(c.icu_intime, INTERVAL 3 HOUR)
  GROUP BY c.stay_id, c.icu_intime
  HAVING COUNTIF(e.starttime IS NOT NULL) = 0
),
vs AS (
  SELECT a.stay_id, v.heart_rate, v.mbp
  FROM analysable a
  JOIN `physionet-data.mimiciv_3_1_derived.vitalsign` v
    ON v.stay_id = a.stay_id
   AND v.charttime BETWEEN a.icu_intime
                       AND DATETIME_ADD(a.icu_intime, INTERVAL 12 HOUR)
),
per_stay AS (
  SELECT stay_id,
    COUNTIF(heart_rate IS NOT NULL) AS n_hr,
    COUNTIF(mbp        IS NOT NULL) AS n_map
  FROM vs GROUP BY stay_id
)
SELECT
  COUNT(*) AS n_stays,
  APPROX_QUANTILES(n_hr, 100)[OFFSET(50)] AS hr_p50,
  APPROX_QUANTILES(n_hr, 100)[OFFSET(75)] AS hr_p75,
  APPROX_QUANTILES(n_hr, 100)[OFFSET(90)] AS hr_p90,
  APPROX_QUANTILES(n_hr, 100)[OFFSET(99)] AS hr_p99,
  MAX(n_hr) AS hr_max,
  COUNTIF(n_hr >= 24) AS stays_ge_24,
  COUNTIF(n_hr >= 36) AS stays_ge_36,
  COUNTIF(n_hr >= 48) AS stays_ge_48
FROM per_stay
