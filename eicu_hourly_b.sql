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
