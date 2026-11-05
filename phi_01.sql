-- phi_01.sql — hourly vitals + treatment-blocked flag, stable calibration patients
-- Implements PHI_PROTOCOL.md (9ea7371) and PHI_TREATMENT_ADDENDUM.md.
-- Committed before execution. Computes no phi and no outcome-linked measure.

CREATE TABLE `project-688c444c-3632-4faa-a13.missh.phi_hourly_cal` AS
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
         COUNT(e.starttime) AS n_events
  FROM cohort c
  LEFT JOIN events e USING (stay_id)
  GROUP BY c.stay_id, c.subject_id, c.hadm_id, c.icu_intime, c.icu_outtime,
           c.hospital_expire_flag
),
first_analysable AS (
  SELECT * FROM flags
  WHERE t_early IS NULL
  QUALIFY ROW_NUMBER() OVER (PARTITION BY subject_id ORDER BY icu_intime) = 1
),
stable AS (
  SELECT f.*
  FROM first_analysable f
  JOIN `project-688c444c-3632-4faa-a13.missh.split_reg1` sp USING (subject_id)
  WHERE sp.split = 'calibration'
    AND f.n_events = 0
    AND f.hospital_expire_flag = 0
),
hours AS (
  SELECT s.stay_id, s.icu_intime, hour_idx
  FROM stable s,
  UNNEST(GENERATE_ARRAY(0,
    DIV(DATETIME_DIFF(s.icu_outtime, s.icu_intime, MINUTE), 60) - 1)) AS hour_idx
),
vitals AS (
  SELECT v.stay_id,
         DIV(DATETIME_DIFF(v.charttime, s.icu_intime, MINUTE), 60) AS hour_idx,
         AVG(v.heart_rate) AS hr, AVG(v.mbp) AS map,
         AVG(v.resp_rate) AS rr, AVG(v.spo2) AS spo2
  FROM `physionet-data.mimiciv_3_1_derived.vitalsign` v
  JOIN stable s USING (stay_id)
  WHERE v.charttime >= s.icu_intime AND v.charttime < s.icu_outtime
  GROUP BY v.stay_id, hour_idx
),
blocks_bolus AS (
  SELECT ie.stay_id, ie.starttime AS b_start,
         DATETIME_ADD(ie.endtime, INTERVAL 2 HOUR) AS b_end
  FROM `physionet-data.mimiciv_3_1_icu.inputevents` ie
  JOIN stable s USING (stay_id)
  WHERE ie.itemid IN (225158, 225828, 220864, 220862)
    AND LOWER(ie.amountuom) = 'ml' AND ie.amount >= 500
    AND DATETIME_DIFF(ie.endtime, ie.starttime, MINUTE) <= 60
),
iv_drug_items AS (
  SELECT itemid
  FROM `physionet-data.mimiciv_3_1_icu.d_items`
  WHERE linksto = 'inputevents'
    AND REGEXP_CONTAINS(LOWER(label),
      r'esmolol|labetalol|metoprolol|diltiazem|amiodarone|nicardipine|clevidipine|hydralazine|nitroglycerin|nitroprusside|enalaprilat|verapamil|digoxin|dobutamine|milrinone')
),
blocks_iv AS (
  SELECT ie.stay_id, ie.starttime AS b_start,
         DATETIME_ADD(ie.endtime, INTERVAL 4 HOUR) AS b_end
  FROM `physionet-data.mimiciv_3_1_icu.inputevents` ie
  JOIN stable s USING (stay_id)
  WHERE ie.itemid IN (SELECT itemid FROM iv_drug_items)
),
blocks_emar AS (
  SELECT s.stay_id, e.charttime AS b_start,
         DATETIME_ADD(e.charttime, INTERVAL 4 HOUR) AS b_end
  FROM `physionet-data.mimiciv_3_1_hosp.emar` e
  JOIN stable s ON e.hadm_id = s.hadm_id
  WHERE e.event_txt LIKE 'Administered%'
    AND REGEXP_CONTAINS(LOWER(e.medication),
      r'metoprolol|atenolol|carvedilol|labetalol|propranolol|esmolol|bisoprolol|nadolol|diltiazem|verapamil|amlodipine|nifedipine|hydralazine|lisinopril|captopril|enalapril|losartan|valsartan|clonidine|isosorbide|nitroglycerin|amiodarone|digoxin')
    AND e.charttime >= DATETIME_SUB(s.icu_intime, INTERVAL 4 HOUR)
    AND e.charttime <  s.icu_outtime
),
all_blocks AS (
  SELECT * FROM blocks_bolus
  UNION ALL SELECT * FROM blocks_iv
  UNION ALL SELECT * FROM blocks_emar
),
blocked_hours AS (
  SELECT DISTINCT g.stay_id, g.hour_idx
  FROM hours g
  JOIN all_blocks b USING (stay_id)
  WHERE b.b_start < DATETIME_ADD(g.icu_intime, INTERVAL (g.hour_idx + 1) HOUR)
    AND b.b_end   > DATETIME_ADD(g.icu_intime, INTERVAL g.hour_idx HOUR)
)
SELECT g.stay_id, g.hour_idx,
       v.hr, v.map, v.rr, v.spo2,
       (bh.stay_id IS NOT NULL) AS blocked
FROM hours g
LEFT JOIN vitals v
  ON v.stay_id = g.stay_id AND v.hour_idx = g.hour_idx
LEFT JOIN blocked_hours bh
  ON bh.stay_id = g.stay_id AND bh.hour_idx = g.hour_idx
