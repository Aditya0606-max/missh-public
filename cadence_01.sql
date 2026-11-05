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
-- first 12 hours only; that is where the reference and early windows live
vs AS (
  SELECT a.stay_id, v.charttime,
         v.heart_rate, v.mbp, v.resp_rate, v.spo2, v.temperature
  FROM analysable a
  JOIN `physionet-data.mimiciv_3_1_derived.vitalsign` v
    ON v.stay_id = a.stay_id
   AND v.charttime BETWEEN a.icu_intime
                       AND DATETIME_ADD(a.icu_intime, INTERVAL 12 HOUR)
),
per_stay AS (
  SELECT stay_id,
    COUNTIF(heart_rate  IS NOT NULL) AS n_hr,
    COUNTIF(mbp         IS NOT NULL) AS n_map,
    COUNTIF(resp_rate   IS NOT NULL) AS n_rr,
    COUNTIF(spo2        IS NOT NULL) AS n_spo2,
    COUNTIF(temperature IS NOT NULL) AS n_temp
  FROM vs GROUP BY stay_id
)
SELECT
  COUNT(*) AS n_stays,
  ROUND(APPROX_QUANTILES(n_hr,   100)[OFFSET(50)], 1) AS hr_med_12h,
  ROUND(APPROX_QUANTILES(n_map,  100)[OFFSET(50)], 1) AS map_med_12h,
  ROUND(APPROX_QUANTILES(n_rr,   100)[OFFSET(50)], 1) AS rr_med_12h,
  ROUND(APPROX_QUANTILES(n_spo2, 100)[OFFSET(50)], 1) AS spo2_med_12h,
  ROUND(APPROX_QUANTILES(n_temp, 100)[OFFSET(50)], 1) AS temp_med_12h,
  ROUND(APPROX_QUANTILES(n_hr,   100)[OFFSET(25)], 1) AS hr_p25,
  ROUND(APPROX_QUANTILES(n_map,  100)[OFFSET(25)], 1) AS map_p25
FROM per_stay
