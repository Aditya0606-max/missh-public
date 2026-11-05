-- bolus_01.sql — fluid boluses (A14 definition) for calibration stays, hours from ICU in.
CREATE TABLE `project-688c444c-3632-4faa-a13.missh.bolus_test` AS
WITH s AS (SELECT DISTINCT stay_id FROM `project-688c444c-3632-4faa-a13.missh.vitals_hourly_test`),
i AS (SELECT stay_id, icu_intime FROM `physionet-data.mimiciv_3_1_derived.icustay_detail`)
SELECT ie.stay_id,
  DATETIME_DIFF(ie.starttime, i.icu_intime, MINUTE) / 60.0 AS start_h,
  DATETIME_DIFF(ie.endtime, i.icu_intime, MINUTE) / 60.0 AS end_h,
  ie.amount
FROM `physionet-data.mimiciv_3_1_icu.inputevents` ie
JOIN s USING (stay_id) JOIN i USING (stay_id)
WHERE ie.itemid IN (225158, 225828, 220864, 220862)
  AND LOWER(ie.amountuom) = 'ml' AND ie.amount >= 500
  AND DATETIME_DIFF(ie.endtime, ie.starttime, MINUTE) <= 60
  AND ie.starttime >= i.icu_intime
  AND ie.starttime < DATETIME_ADD(i.icu_intime, INTERVAL 72 HOUR)
