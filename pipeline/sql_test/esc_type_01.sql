-- esc_type_01.sql — first escalation type after hour 3 (calibration), for P7.
CREATE TABLE `project-688c444c-3632-4faa-a13.missh.esc_type_test` AS
WITH pts AS (
  SELECT o.stay_id, i.icu_intime
  FROM `project-688c444c-3632-4faa-a13.missh.outcome_test` o
  JOIN `physionet-data.mimiciv_3_1_derived.icustay_detail` i USING (stay_id)
  WHERE o.label IN ('escalated', 'escalated_hyperacute')
),
pr AS (
  SELECT p.stay_id, MIN(v.starttime) AS t
  FROM `physionet-data.mimiciv_3_1_derived.vasoactive_agent` v JOIN pts p USING (stay_id)
  WHERE COALESCE(v.dopamine, v.epinephrine, v.norepinephrine, v.phenylephrine, v.vasopressin) IS NOT NULL
    AND v.starttime > DATETIME_ADD(p.icu_intime, INTERVAL 3 HOUR)
  GROUP BY p.stay_id
),
ve AS (
  SELECT p.stay_id, MIN(x.starttime) AS t
  FROM `physionet-data.mimiciv_3_1_derived.ventilation` x JOIN pts p USING (stay_id)
  WHERE x.ventilation_status IN ('InvasiveVent', 'Tracheostomy')
    AND x.starttime > DATETIME_ADD(p.icu_intime, INTERVAL 3 HOUR)
  GROUP BY p.stay_id
)
SELECT p.stay_id,
  CASE WHEN pr.t IS NOT NULL AND (ve.t IS NULL OR pr.t < ve.t) THEN 'pressor'
       WHEN ve.t IS NOT NULL AND (pr.t IS NULL OR ve.t < pr.t) THEN 'vent'
       WHEN pr.t IS NOT NULL AND pr.t = ve.t THEN 'both'
  END AS first_type
FROM pts p LEFT JOIN pr USING (stay_id) LEFT JOIN ve USING (stay_id)
