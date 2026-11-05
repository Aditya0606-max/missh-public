-- early_ruler_01.sql — how many calibration patients have clean HR and MAP
-- readings in their first hours (ruler feasibility). Uses charting and the
-- treatment blocks of PHI_TREATMENT_ADDENDUM.md only; no outcome measure.

WITH cohort AS (
  SELECT s.stay_id, i.subject_id, i.hadm_id, i.icu_intime, i.icu_outtime
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
         MIN(IF(e.starttime <= DATETIME_ADD(c.icu_intime, INTERVAL 3 HOUR),
                e.starttime, NULL)) AS t_early
  FROM cohort c
  LEFT JOIN events e USING (stay_id)
  GROUP BY c.stay_id, c.subject_id, c.hadm_id, c.icu_intime, c.icu_outtime
),
pts AS (
  SELECT f.*
  FROM flags f
  JOIN `project-688c444c-3632-4faa-a13.missh.split_reg1` sp USING (subject_id)
  WHERE f.t_early IS NULL AND sp.split = 'calibration'
  QUALIFY ROW_NUMBER() OVER (PARTITION BY f.subject_id ORDER BY f.icu_intime) = 1
),
hours AS (
  SELECT p.stay_id, p.icu_intime, hour_idx
  FROM pts p,
  UNNEST(GENERATE_ARRAY(0, LEAST(5,
    DIV(DATETIME_DIFF(p.icu_outtime, p.icu_intime, MINUTE), 60) - 1))) AS hour_idx
),
vitals AS (
  SELECT v.stay_id,
         DIV(DATETIME_DIFF(v.charttime, p.icu_intime, MINUTE), 60) AS hour_idx,
         AVG(v.heart_rate) AS hr, AVG(v.mbp) AS map
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
),
grid AS (
  SELECT g.stay_id, g.hour_idx,
         (bh.stay_id IS NOT NULL) AS blocked,
         (v.hr  IS NOT NULL AND bh.stay_id IS NULL) AS hr_clean,
         (v.map IS NOT NULL AND bh.stay_id IS NULL) AS map_clean
  FROM hours g
  LEFT JOIN vitals v ON v.stay_id = g.stay_id AND v.hour_idx = g.hour_idx
  LEFT JOIN blocked_hours bh ON bh.stay_id = g.stay_id AND bh.hour_idx = g.hour_idx
),
per_pt AS (
  SELECT stay_id,
    COUNTIF(hour_idx < 2 AND hr_clean)  AS hr2,  COUNTIF(hour_idx < 2 AND map_clean) AS map2,
    COUNTIF(hour_idx < 3 AND hr_clean)  AS hr3,  COUNTIF(hour_idx < 3 AND map_clean) AS map3,
    COUNTIF(hour_idx < 5 AND hr_clean)  AS hr5,  COUNTIF(hour_idx < 5 AND map_clean) AS map5,
    COUNTIF(hr_clean) AS hr6, COUNTIF(map_clean) AS map6,
    COUNTIF(hour_idx < 2 AND blocked) AS blk2,
    COUNTIF(hour_idx < 3 AND blocked) AS blk3
  FROM grid
  GROUP BY stay_id
)
SELECT
  COUNT(*)                                  AS patients,
  COUNTIF(blk2 >= 1)                        AS any_block_first_2h,
  COUNTIF(blk3 >= 1)                        AS any_block_first_3h,
  COUNTIF(hr2 >= 2 AND map2 >= 2)           AS clean_2of2_by_h2,
  COUNTIF(hr3 >= 2 AND map3 >= 2)           AS clean_2plus_by_h3,
  COUNTIF(hr3 >= 3 AND map3 >= 3)           AS clean_3of3_by_h3,
  COUNTIF(hr5 >= 4 AND map5 >= 4)           AS clean_4plus_by_h5,
  COUNTIF(hr6 >= 5 AND map6 >= 5)           AS clean_5plus_by_h6
FROM per_pt
