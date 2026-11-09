WITH s AS (SELECT patientunitstayid FROM `physionet-data.eicu_crd.patient`
           WHERE LOWER(apacheadmissiondx) LIKE '%sepsis%' AND unitvisitnumber = 1
             AND (SAFE_CAST(REGEXP_REPLACE(age, r'[^0-9]', '') AS INT64) >= 18 OR age LIKE '%>%')),
dev AS (
  SELECT 'nurse: O2 Admin Device' AS src, LOWER(TRIM(nursingchartvalue)) AS val FROM `physionet-data.eicu_crd.nursecharting`
  WHERE nursingchartcelltypevalname = 'O2 Admin Device' AND patientunitstayid IN (SELECT * FROM s)
  UNION ALL SELECT CONCAT('resp: ', respchartvaluelabel), LOWER(TRIM(respchartvalue)) FROM `physionet-data.eicu_crd.respiratorycharting`
  WHERE respchartvaluelabel IN ('O2 Device', 'Oxygen Delivery Method') AND patientunitstayid IN (SELECT * FROM s)),
num AS (
  SELECT 'nurse: O2 L/%' AS src, SAFE_CAST(nursingchartvalue AS FLOAT64) AS x FROM `physionet-data.eicu_crd.nursecharting`
  WHERE nursingchartcelltypevalname = 'O2 L/%' AND patientunitstayid IN (SELECT * FROM s)
  UNION ALL SELECT CONCAT('resp: ', respchartvaluelabel), SAFE_CAST(REGEXP_REPLACE(respchartvalue, r'[^0-9.]', '') AS FLOAT64)
  FROM `physionet-data.eicu_crd.respiratorycharting`
  WHERE respchartvaluelabel IN ('FiO2', 'FIO2 (%)') AND patientunitstayid IN (SELECT * FROM s))
SELECT 'A device text' AS part, src, val AS value, COUNT(*) AS n FROM dev GROUP BY 1, 2, 3 HAVING n >= 200
UNION ALL
SELECT 'B numbers', src, CASE WHEN x IS NULL THEN 'not a number' WHEN x <= 1 THEN '0-1 (fraction)' WHEN x <= 15 THEN '1-15 (litres?)'
  WHEN x < 21 THEN '15-21' WHEN x <= 100 THEN '21-100 (percent)' ELSE '>100' END, COUNT(*) FROM num GROUP BY 1, 2, 3
ORDER BY part, src, n DESC
