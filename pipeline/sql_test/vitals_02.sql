-- vitals_02.sql — A14 flags on the existing hourly grid (vitals_hourly_test).
-- block_bolus, block_iv, sed_infusion = BLOCK; flag_oral_bp, flag_sed_dose = FLAG.
-- No outcome labels. Committed before execution.
CREATE TABLE `project-688c444c-3632-4faa-a13.missh.vitals_hourly_test_v2` AS
WITH base AS (
  SELECT v.stay_id, v.hour_idx, v.hr, v.map, v.rr, v.spo2, i.icu_intime, i.hadm_id
  FROM `project-688c444c-3632-4faa-a13.missh.vitals_hourly_test` v
  JOIN `physionet-data.mimiciv_3_1_derived.icustay_detail` i USING (stay_id)
),
pts AS (SELECT DISTINCT stay_id, hadm_id, icu_intime FROM base),
iv_items AS (
  SELECT itemid FROM `physionet-data.mimiciv_3_1_icu.d_items`
  WHERE linksto = 'inputevents' AND REGEXP_CONTAINS(LOWER(label),
    r'esmolol|labetalol|metoprolol|diltiazem|amiodarone|nicardipine|clevidipine|hydralazine|nitroglycerin|nitroprusside|enalaprilat|verapamil|digoxin|dobutamine|milrinone')
),
sed_items AS (
  SELECT itemid FROM `physionet-data.mimiciv_3_1_icu.d_items`
  WHERE linksto = 'inputevents' AND REGEXP_CONTAINS(LOWER(label),
    r'propofol|midazolam|lorazepam|fentanyl|hydromorphone|morphine|dexmedetomidine|ketamine|etomidate')
),
events AS (
  SELECT ie.stay_id, ie.starttime AS s_t, DATETIME_ADD(ie.endtime, INTERVAL 2 HOUR) AS e_t, 'bolus' AS t
  FROM `physionet-data.mimiciv_3_1_icu.inputevents` ie JOIN pts p USING (stay_id)
  WHERE ie.itemid IN (225158, 225828, 220864, 220862) AND LOWER(ie.amountuom) = 'ml'
    AND ie.amount >= 500 AND DATETIME_DIFF(ie.endtime, ie.starttime, MINUTE) <= 60
  UNION ALL
  SELECT ie.stay_id, ie.starttime, DATETIME_ADD(ie.endtime, INTERVAL 4 HOUR), 'iv'
  FROM `physionet-data.mimiciv_3_1_icu.inputevents` ie JOIN pts p USING (stay_id)
  WHERE ie.itemid IN (SELECT itemid FROM iv_items)
  UNION ALL
  SELECT ie.stay_id, ie.starttime, DATETIME_ADD(ie.endtime, INTERVAL 1 HOUR), 'sedinf'
  FROM `physionet-data.mimiciv_3_1_icu.inputevents` ie JOIN pts p USING (stay_id)
  WHERE ie.itemid IN (SELECT itemid FROM sed_items)
    AND DATETIME_DIFF(ie.endtime, ie.starttime, MINUTE) >= 60
  UNION ALL
  SELECT ie.stay_id, ie.starttime, DATETIME_ADD(ie.endtime, INTERVAL 2 HOUR), 'seddose'
  FROM `physionet-data.mimiciv_3_1_icu.inputevents` ie JOIN pts p USING (stay_id)
  WHERE ie.itemid IN (SELECT itemid FROM sed_items)
    AND DATETIME_DIFF(ie.endtime, ie.starttime, MINUTE) < 60
  UNION ALL
  SELECT p.stay_id, e.charttime, DATETIME_ADD(e.charttime, INTERVAL 2 HOUR), 'seddose'
  FROM `physionet-data.mimiciv_3_1_hosp.emar` e JOIN pts p ON e.hadm_id = p.hadm_id
  WHERE e.event_txt LIKE 'Administered%'
    AND REGEXP_CONTAINS(LOWER(e.medication),
      r'propofol|midazolam|lorazepam|fentanyl|hydromorphone|morphine|dexmedetomidine|ketamine|etomidate')
    AND e.charttime >= DATETIME_SUB(p.icu_intime, INTERVAL 2 HOUR)
    AND e.charttime <  DATETIME_ADD(p.icu_intime, INTERVAL 72 HOUR)
  UNION ALL
  SELECT p.stay_id, e.charttime, DATETIME_ADD(e.charttime, INTERVAL 4 HOUR), 'oral'
  FROM `physionet-data.mimiciv_3_1_hosp.emar` e JOIN pts p ON e.hadm_id = p.hadm_id
  WHERE e.event_txt LIKE 'Administered%'
    AND REGEXP_CONTAINS(LOWER(e.medication),
      r'metoprolol|atenolol|carvedilol|labetalol|propranolol|esmolol|bisoprolol|nadolol|diltiazem|verapamil|amlodipine|nifedipine|hydralazine|lisinopril|captopril|enalapril|losartan|valsartan|clonidine|isosorbide|nitroglycerin|amiodarone|digoxin')
    AND e.charttime >= DATETIME_SUB(p.icu_intime, INTERVAL 4 HOUR)
    AND e.charttime <  DATETIME_ADD(p.icu_intime, INTERVAL 72 HOUR)
),
ev_hours AS (
  SELECT b.stay_id, b.hour_idx,
    LOGICAL_OR(x.t = 'bolus') AS bolus, LOGICAL_OR(x.t = 'iv') AS iv,
    LOGICAL_OR(x.t = 'sedinf') AS sedinf, LOGICAL_OR(x.t = 'seddose') AS seddose,
    LOGICAL_OR(x.t = 'oral') AS oral
  FROM base b JOIN events x ON x.stay_id = b.stay_id
   AND x.s_t < DATETIME_ADD(b.icu_intime, INTERVAL (b.hour_idx + 1) HOUR)
   AND x.e_t > DATETIME_ADD(b.icu_intime, INTERVAL b.hour_idx HOUR)
  GROUP BY b.stay_id, b.hour_idx
)
SELECT b.stay_id, b.hour_idx, b.hr, b.map, b.rr, b.spo2,
  COALESCE(f.bolus, FALSE)   AS block_bolus,
  COALESCE(f.iv, FALSE)      AS block_iv,
  COALESCE(f.sedinf, FALSE)  AS sed_infusion,
  COALESCE(f.oral, FALSE)    AS flag_oral_bp,
  COALESCE(f.seddose, FALSE) AS flag_sed_dose
FROM base b LEFT JOIN ev_hours f USING (stay_id, hour_idx)
