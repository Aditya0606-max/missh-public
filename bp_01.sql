-- bp_01.sql — hourly SBP/DBP and arterial share, calibration stays, hours 0-71 (E8)
CREATE TABLE `project-688c444c-3632-4faa-a13.missh.bp_hourly_cal` AS
WITH s AS (SELECT DISTINCT stay_id FROM `project-688c444c-3632-4faa-a13.missh.vitals_hourly_cal`),
i AS (SELECT stay_id, icu_intime FROM `physionet-data.mimiciv_3_1_derived.icustay_detail`)
SELECT v.stay_id,
       DIV(DATETIME_DIFF(v.charttime, i.icu_intime, MINUTE), 60) AS hour_idx,
       AVG(v.sbp) AS sbp, AVG(v.dbp) AS dbp,
       AVG(IF(v.sbp_ni IS NULL, 1, 0)) AS art_share
FROM `physionet-data.mimiciv_3_1_derived.vitalsign` v
JOIN s USING (stay_id) JOIN i USING (stay_id)
WHERE v.charttime >= i.icu_intime
  AND v.charttime < DATETIME_ADD(i.icu_intime, INTERVAL 72 HOUR)
  AND v.sbp IS NOT NULL AND v.dbp IS NOT NULL
GROUP BY v.stay_id, hour_idx
