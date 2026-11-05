WITH cohort AS (
  SELECT s.stay_id, i.icu_intime
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
first_event AS (
  SELECT c.stay_id,
         DATETIME_DIFF(MIN(e.starttime), c.icu_intime, MINUTE) / 60.0 AS hrs
  FROM cohort c
  JOIN events e USING (stay_id)
  GROUP BY c.stay_id, c.icu_intime
),
excluded AS (
  SELECT * FROM first_event WHERE hrs <= 3
)
SELECT
  COUNT(*) AS n_excluded,
  COUNTIF(hrs < 0) AS negative_times,
  ROUND(APPROX_QUANTILES(hrs, 100)[OFFSET(10)], 2) AS p10,
  ROUND(APPROX_QUANTILES(hrs, 100)[OFFSET(25)], 2) AS p25,
  ROUND(APPROX_QUANTILES(hrs, 100)[OFFSET(50)], 2) AS p50,
  ROUND(APPROX_QUANTILES(hrs, 100)[OFFSET(75)], 2) AS p75,
  ROUND(APPROX_QUANTILES(hrs, 100)[OFFSET(90)], 2) AS p90,
  COUNTIF(hrs >= 1) AS ge_1h,
  COUNTIF(hrs >= 2) AS ge_2h,
  COUNTIF(hrs >= 2.5) AS ge_2p5h
FROM excluded
