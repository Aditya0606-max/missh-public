-- sedation_01.sql — EXPLORATORY E3a (post-result): sedated hours 0-5,
-- escalated_hyperacute and stable calibration patients.
CREATE TABLE `project-688c444c-3632-4faa-a13.missh.sed_hours_cal` AS
WITH pts AS (
  SELECT o.stay_id, i.hadm_id, i.icu_intime
  FROM `project-688c444c-3632-4faa-a13.missh.outcome_cal` o
  JOIN `physionet-data.mimiciv_3_1_derived.icustay_detail` i USING (stay_id)
  WHERE o.label IN ('escalated_hyperacute', 'stable')
),
hours AS (
  SELECT p.stay_id, p.icu_intime, hour_idx
  FROM pts p, UNNEST(GENERATE_ARRAY(0, 5)) AS hour_idx
),
sed_items AS (
  SELECT itemid FROM `physionet-data.mimiciv_3_1_icu.d_items`
  WHERE linksto = 'inputevents'
    AND REGEXP_CONTAINS(LOWER(label),
      r'propofol|midazolam|lorazepam|fentanyl|hydromorphone|morphine|dexmedetomidine|ketamine|etomidate')
),
sed AS (
  SELECT ie.stay_id, ie.starttime AS s,
         DATETIME_ADD(ie.endtime, INTERVAL 1 HOUR) AS e
  FROM `physionet-data.mimiciv_3_1_icu.inputevents` ie
  JOIN pts p USING (stay_id)
  WHERE ie.itemid IN (SELECT itemid FROM sed_items)
  UNION ALL
  SELECT p.stay_id, em.charttime AS s,
         DATETIME_ADD(em.charttime, INTERVAL 2 HOUR) AS e
  FROM `physionet-data.mimiciv_3_1_hosp.emar` em
  JOIN pts p ON em.hadm_id = p.hadm_id
  WHERE em.event_txt LIKE 'Administered%'
    AND REGEXP_CONTAINS(LOWER(em.medication),
      r'propofol|midazolam|lorazepam|fentanyl|hydromorphone|morphine|dexmedetomidine|ketamine|etomidate')
    AND em.charttime >= DATETIME_SUB(p.icu_intime, INTERVAL 2 HOUR)
    AND em.charttime <  DATETIME_ADD(p.icu_intime, INTERVAL 6 HOUR)
)
SELECT g.stay_id, g.hour_idx,
  LOGICAL_OR(s.stay_id IS NOT NULL) AS sedated
FROM hours g
LEFT JOIN sed s
  ON s.stay_id = g.stay_id
 AND s.s < DATETIME_ADD(g.icu_intime, INTERVAL (g.hour_idx + 1) HOUR)
 AND s.e > DATETIME_ADD(g.icu_intime, INTERVAL g.hour_idx HOUR)
GROUP BY g.stay_id, g.hour_idx
