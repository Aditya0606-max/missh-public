, pres AS (
  SELECT patientunitstayid, DIV(observationoffset, 60) AS h, 1 AS vit, 0 AS bp, 0 AS fi, 0 AS dev, 0 AS gcs FROM `physionet-data.eicu_crd.vitalperiodic`
    WHERE (heartrate IS NOT NULL OR respiration IS NOT NULL OR sao2 IS NOT NULL) AND patientunitstayid IN (SELECT patientunitstayid FROM w)
  UNION ALL SELECT patientunitstayid, DIV(observationoffset, 60), 0, 1, 0, 0, 0 FROM `physionet-data.eicu_crd.vitalaperiodic`
    WHERE noninvasivesystolic IS NOT NULL AND patientunitstayid IN (SELECT patientunitstayid FROM w)
  UNION ALL SELECT patientunitstayid, DIV(observationoffset, 60), 0, 1, 0, 0, 0 FROM `physionet-data.eicu_crd.vitalperiodic`
    WHERE systemicsystolic IS NOT NULL AND patientunitstayid IN (SELECT patientunitstayid FROM w)
  UNION ALL SELECT patientunitstayid, DIV(respchartoffset, 60), 0, 0, 1, 0, 0 FROM `physionet-data.eicu_crd.respiratorycharting`
    WHERE REGEXP_CONTAINS(LOWER(respchartvaluelabel), r'fio2|fi o2') AND patientunitstayid IN (SELECT patientunitstayid FROM w)
  UNION ALL SELECT patientunitstayid, DIV(respchartoffset, 60), 0, 0, 0, 1, 0 FROM `physionet-data.eicu_crd.respiratorycharting`
    WHERE REGEXP_CONTAINS(LOWER(respchartvaluelabel), r'^o2 device$|oxygen delivery method|oxygen flow rate') AND patientunitstayid IN (SELECT patientunitstayid FROM w)
  UNION ALL SELECT patientunitstayid, DIV(nursingchartoffset, 60), 0, 0,
      IF(REGEXP_CONTAINS(LOWER(nursingchartcelltypevalname), r'fio2|o2 l/%'), 1, 0),
      IF(REGEXP_CONTAINS(LOWER(nursingchartcelltypevalname), r'o2 admin device'), 1, 0),
      IF(REGEXP_CONTAINS(LOWER(nursingchartcelltypevalname), r'gcs total|glasgow'), 1, 0)
    FROM `physionet-data.eicu_crd.nursecharting`
    WHERE REGEXP_CONTAINS(LOWER(nursingchartcelltypevalname), r'fio2|o2 l/%|o2 admin device|gcs total|glasgow')
      AND patientunitstayid IN (SELECT patientunitstayid FROM w))
SELECT w.patientunitstayid, w.who, w.window_h, p.h, MAX(p.vit) vit, MAX(p.bp) bp, MAX(p.fi) fi, MAX(p.dev) dev, MAX(p.gcs) gcs
FROM w JOIN pres p USING (patientunitstayid)
WHERE p.h >= -12 AND p.h < LEAST(w.window_h, 72)
GROUP BY 1, 2, 3, 4
