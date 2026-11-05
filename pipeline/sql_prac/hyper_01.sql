-- hyper_01.sql — hourly vitals + treatment-blocked flag, hours 0-5,
-- escalated_hyperacute patients (outcome_01.sql d1c617e).
-- Implements HYPERACUTE_PROFILE.md (cf1cc97). Committed before execution.

CREATE TABLE `project-688c444c-3632-4faa-a13.missh.hyper_hourly_prac` AS
WITH pts AS (
  SELECT o.stay_id, o.esc_h, o.dni_h, i.hadm_id, i.icu_intime
  FROM `project-688c444c-3632-4faa-a13.missh.outcome_prac` o
  JOIN `physionet-data.mimiciv_3_1_derived.icustay_detail` i USING (stay_id)
  WHERE o.label = 'escalated_hyperacute'
),
hours AS (
  SELECT p.stay_id, p.icu_intime, hour_idx
  FROM pts p, UNNEST(GENERATE_ARRAY(0, 5)) AS hour_idx
),
vitals AS (
  SELECT v.stay_id,
         DIV(DATETIME_DIFF(v.charttime, p.icu_intime, MINUTE), 60) AS hour_idx,
         AVG(v.heart_rate) AS hr, AVG(v.mbp) AS map,
         AVG(v.resp_rate) AS rr, AVG(v.spo2) AS spo2
  FROM `physionet-data.mimiciv_3_1_derived.vitalsign` v
  JOIN pts p USING (stay_id)
  WHERE v.charttime >= p.icu_intime
    AND v.charttime <  DATETIME_ADD(p.icu_intime, INTERVAL 6 HOUR)
  GROUP BY v.stay_id, hour_idx
),
blocks_bolus AS (
  SELECT ie.stay_id, ie.starttime AS b_start,
         DATETIME_ADD(ie.endtime, INTERVAL 2 HOUR) AS b_end
  FROM `physionet-data.mimiciv_3_1_icu.inputevents` ie
  JOIN pts p USING (stay_id)
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
  JOIN pts p USING (stay_id)
  WHERE ie.itemid IN (SELECT itemid FROM iv_drug_items)
),
blocks_emar AS (
  SELECT p.stay_id, e.charttime AS b_start,
         DATETIME_ADD(e.charttime, INTERVAL 4 HOUR) AS b_end
  FROM `physionet-data.mimiciv_3_1_hosp.emar` e
  JOIN pts p ON e.hadm_id = p.hadm_id
  WHERE e.event_txt LIKE 'Administered%'
    AND REGEXP_CONTAINS(LOWER(e.medication),
      r'metoprolol|atenolol|carvedilol|labetalol|propranolol|esmolol|bisoprolol|nadolol|diltiazem|verapamil|amlodipine|nifedipine|hydralazine|lisinopril|captopril|enalapril|losartan|valsartan|clonidine|isosorbide|nitroglycerin|amiodarone|digoxin')
    AND e.charttime >= DATETIME_SUB(p.icu_intime, INTERVAL 4 HOUR)
    AND e.charttime <  DATETIME_ADD(p.icu_intime, INTERVAL 6 HOUR)
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
SELECT g.stay_id, g.hour_idx, v.hr, v.map, v.rr, v.spo2,
       (bh.stay_id IS NOT NULL) AS blocked, p.esc_h, p.dni_h
FROM hours g
JOIN pts p USING (stay_id)
LEFT JOIN vitals v ON v.stay_id = g.stay_id AND v.hour_idx = g.hour_idx
LEFT JOIN blocked_hours bh ON bh.stay_id = g.stay_id AND bh.hour_idx = g.hour_idx
