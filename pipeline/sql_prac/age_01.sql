-- age_01.sql — age at ICU admission for the split's first stays (descriptive strata).
CREATE TABLE `project-688c444c-3632-4faa-a13.missh.age_prac` AS
SELECT DISTINCT v.stay_id, i.admission_age
FROM `project-688c444c-3632-4faa-a13.missh.vitals_hourly_prac` v
JOIN `physionet-data.mimiciv_3_1_derived.icustay_detail` i USING (stay_id)
