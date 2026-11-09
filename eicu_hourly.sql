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
dv AS (SELECT patientunitstayid, CAST(FLOOR(o / 60) AS INT64) AS h, ARRAY_AGG(d ORDER BY o DESC LIMIT 1)[OFFSET(0)] AS device FROM (
         SELECT patientunitstayid, nursingchartoffset AS o, LOWER(TRIM(nursingchartvalue)) AS d FROM `physionet-data.eicu_crd.nursecharting`
         WHERE nursingchartcelltypevalname = 'O2 Admin Device' AND patientunitstayid IN (SELECT * FROM s) AND nursingchartoffset BETWEEN -720 AND 5759
         UNION ALL
         SELECT patientunitstayid, respchartoffset, LOWER(TRIM(respchartvalue)) FROM `physionet-data.eicu_crd.respiratorycharting`
         WHERE respchartvaluelabel IN ('O2 Device', 'Oxygen Delivery Method') AND patientunitstayid IN (SELECT * FROM s) AND respchartoffset BETWEEN -720 AND 5759)
       GROUP BY 1, 2),
gc AS (SELECT patientunitstayid, CAST(FLOOR(nursingchartoffset / 60) AS INT64) AS h, MIN(SAFE_CAST(nursingchartvalue AS FLOAT64)) AS gcs
       FROM `physionet-data.eicu_crd.nursecharting`
       WHERE nursingchartcelltypevalname = 'GCS Total' AND patientunitstayid IN (SELECT * FROM s) AND nursingchartoffset BETWEEN -720 AND 5759 GROUP BY 1, 2),
k AS (SELECT patientunitstayid, h FROM vh UNION DISTINCT SELECT patientunitstayid, h FROM fi UNION DISTINCT SELECT patientunitstayid, h FROM fl
      UNION DISTINCT SELECT patientunitstayid, h FROM dv UNION DISTINCT SELECT patientunitstayid, h FROM gc)
SELECT k.patientunitstayid, k.h AS hour, vh.hr, vh.rr, vh.spo2, vh.temp, vh.sbp, vh.dbp, vh.mbp, fi.fio2, fl.flow, dv.device, gc.gcs
FROM k LEFT JOIN vh USING (patientunitstayid, h) LEFT JOIN fi USING (patientunitstayid, h) LEFT JOIN fl USING (patientunitstayid, h)
LEFT JOIN dv USING (patientunitstayid, h) LEFT JOIN gc USING (patientunitstayid, h)
