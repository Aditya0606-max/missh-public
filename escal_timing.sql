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
per_stay AS (
  SELECT c.stay_id,
    MIN(IF(e.starttime <= DATETIME_ADD(c.icu_intime, INTERVAL 3 HOUR),
           e.starttime, NULL)) AS t_early,
    MIN(IF(e.starttime >  DATETIME_ADD(c.icu_intime, INTERVAL 3 HOUR),
           e.starttime, NULL)) AS t_esc,
    c.icu_intime
  FROM cohort c
  LEFT JOIN events e USING (stay_id)
  GROUP BY c.stay_id, c.icu_intime
),
esc AS (
  SELECT DATETIME_DIFF(t_esc, icu_intime, MINUTE) / 60.0 AS hrs
  FROM per_stay
  WHERE t_early IS NULL AND t_esc IS NOT NULL
)
SELECT
  COUNT(*) AS n,
  ROUND(APPROX_QUANTILES(hrs, 100)[OFFSET(10)], 1) AS p10,
  ROUND(APPROX_QUANTILES(hrs, 100)[OFFSET(25)], 1) AS p25,
  ROUND(APPROX_QUANTILES(hrs, 100)[OFFSET(50)], 1) AS p50,
  ROUND(APPROX_QUANTILES(hrs, 100)[OFFSET(75)], 1) AS p75,
  COUNTIF(hrs >= 8)  AS ge_8h,
  COUNTIF(hrs >= 12) AS ge_12h,
  COUNTIF(hrs >= 18) AS ge_18h,
  COUNTIF(hrs >= 24) AS ge_24h
FROM esc
