WITH cohort AS (
  SELECT s.stay_id, i.subject_id, i.icu_intime, i.icu_outtime, i.dod,
         i.admission_age, i.first_icu_stay
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
    c.stay_id,
    c.dod,
    MIN(IF(e.starttime <= DATETIME_ADD(c.icu_intime, INTERVAL 3 HOUR),
           e.starttime, NULL)) AS t_early,
    MIN(IF(e.starttime >  DATETIME_ADD(c.icu_intime, INTERVAL 3 HOUR),
           e.starttime, NULL)) AS t_escalate
  FROM cohort c
  LEFT JOIN events e USING (stay_id)
  GROUP BY c.stay_id, c.dod
)
SELECT
  COUNT(*)                                            AS sepsis3_stays,
  COUNTIF(t_early IS NOT NULL)                        AS excluded_at_hour3,
  COUNTIF(t_early IS NULL)                            AS analysable,
  COUNTIF(t_early IS NULL AND t_escalate IS NOT NULL) AS escalated_after_h3,
  COUNTIF(t_early IS NULL AND t_escalate IS NULL
          AND dod IS NOT NULL)                        AS died_without_escalation,
  COUNTIF(t_early IS NULL AND t_escalate IS NULL
          AND dod IS NULL)                            AS stable_candidates
FROM flags
