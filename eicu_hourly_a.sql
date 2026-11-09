WITH s AS (SELECT patientunitstayid FROM `physionet-data.eicu_crd.patient`
           WHERE LOWER(apacheadmissiondx) LIKE '%sepsis%' AND unitvisitnumber = 1
             AND (SAFE_CAST(REGEXP_REPLACE(age, r'[^0-9]', '') AS INT64) >= 18 OR age LIKE '%>%')),
v AS (
  SELECT patientunitstayid, CAST(FLOOR(observationoffset / 60) AS INT64) AS h, heartrate AS hr, respiration AS rr, sao2 AS spo2,
         temperature AS temp, systemicsystolic AS sbp, systemicdiastolic AS dbp, systemicmean AS mbp
  FROM `physionet-data.eicu_crd.vitalperiodic` WHERE patientunitstayid IN (SELECT * FROM s) AND observationoffset BETWEEN -720 AND 5759
  UNION ALL
  SELECT patientunitstayid, CAST(FLOOR(observationoffset / 60) AS INT64), NULL, NULL, NULL, NULL, noninvasivesystolic, noninvasivediastolic, noninvasivemean
  FROM `physionet-data.eicu_crd.vitalaperiodic` WHERE patientunitstayid IN (SELECT * FROM s) AND observationoffset BETWEEN -720 AND 5759),
vh AS (SELECT patientunitstayid, h, AVG(hr) AS hr, AVG(rr) AS rr, AVG(spo2) AS spo2, AVG(temp) AS temp, AVG(sbp) AS sbp, AVG(dbp) AS dbp, AVG(mbp) AS mbp
       FROM v GROUP BY 1, 2),
ox AS (
  SELECT patientunitstayid, respchartoffset AS o, 'r' AS src, SAFE_CAST(REGEXP_REPLACE(respchartvalue, r'[^0-9.]', '') AS FLOAT64) AS x
  FROM `physionet-data.eicu_crd.respiratorycharting`
  WHERE respchartvaluelabel IN ('FiO2', 'FIO2 (%)') AND patientunitstayid IN (SELECT * FROM s) AND respchartoffset BETWEEN -720 AND 5759
  UNION ALL
  SELECT patientunitstayid, nursingchartoffset, 'n', SAFE_CAST(nursingchartvalue AS FLOAT64) FROM `physionet-data.eicu_crd.nursecharting`
  WHERE nursingchartcelltypevalname = 'O2 L/%' AND patientunitstayid IN (SELECT * FROM s) AND nursingchartoffset BETWEEN -720 AND 5759),
fi AS (SELECT patientunitstayid, CAST(FLOOR(o / 60) AS INT64) AS h, ARRAY_AGG(IF(x >= 21, x / 100, x) ORDER BY o DESC LIMIT 1)[OFFSET(0)] AS fio2
       FROM ox WHERE (x BETWEEN 21 AND 100) OR (x > 0 AND x <= 1) GROUP BY 1, 2),
fl AS (SELECT patientunitstayid, CAST(FLOOR(o / 60) AS INT64) AS h, ARRAY_AGG(x ORDER BY o DESC LIMIT 1)[OFFSET(0)] AS flow
       FROM ox WHERE src = 'n' AND x > 1 AND x <= 15 GROUP BY 1, 2),
