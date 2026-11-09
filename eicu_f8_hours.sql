WITH s AS (SELECT patientunitstayid, unitadmitsource, hospitaldischargestatus, unitdischargeoffset
           FROM `physionet-data.eicu_crd.patient`
           WHERE LOWER(apacheadmissiondx) LIKE '%sepsis%' AND unitvisitnumber = 1
             AND (SAFE_CAST(REGEXP_REPLACE(age, r'[^0-9]', '') AS INT64) >= 18 OR age LIKE '%>%')),
v AS (SELECT patientunitstayid, MIN(infusionoffset) / 60 AS vaso_h FROM `physionet-data.eicu_crd.infusiondrug`
      WHERE patientunitstayid IN (SELECT patientunitstayid FROM s)
        AND REGEXP_CONTAINS(LOWER(drugname), r'norepinephrine|levophed|vasopressin|epinephrine|phenylephrine|neo-synephrine|neosynephrine|dopamine')
        AND SAFE_CAST(drugrate AS FLOAT64) > 0 GROUP BY 1),
m AS (SELECT patientunitstayid, MIN(t) / 60 AS vent_h FROM (
        SELECT patientunitstayid, ventstartoffset AS t FROM `physionet-data.eicu_crd.respiratorycare` WHERE ventstartoffset IS NOT NULL AND ventstartoffset != 0
        UNION ALL SELECT patientunitstayid, treatmentoffset FROM `physionet-data.eicu_crd.treatment` WHERE LOWER(treatmentstring) LIKE '%mechanical ventilation%')
      WHERE patientunitstayid IN (SELECT patientunitstayid FROM s) GROUP BY 1),
x AS (SELECT s.*, v.vaso_h, m.vent_h, LEAST(IFNULL(v.vaso_h, 1e9), IFNULL(m.vent_h, 1e9)) AS tip,
        REGEXP_CONTAINS(LOWER(IFNULL(s.unitadmitsource, '')), r'operating|recovery|pacu') AS planned
      FROM s LEFT JOIN v USING (patientunitstayid) LEFT JOIN m USING (patientunitstayid)),
y AS (SELECT *, CASE
  WHEN tip >= 1e9 AND hospitaldischargestatus = 'Alive' THEN 'Ajay'
  WHEN tip >= 1e9 OR tip <= 0 OR (tip <= 3 AND planned) THEN NULL
  WHEN tip <= 3 THEN 'Naveen'
  WHEN tip < 5 THEN NULL
  WHEN vaso_h IS NOT NULL AND vent_h IS NOT NULL AND ABS(vaso_h - vent_h) <= 1 THEN 'mixed'
  WHEN vaso_h IS NOT NULL AND (vent_h IS NULL OR vaso_h < vent_h) THEN 'Kranthi' ELSE 'Sundar' END AS who,
  IF(tip >= 1e9, unitdischargeoffset / 60, tip) AS window_h FROM x),
w AS (SELECT patientunitstayid, who, window_h FROM y WHERE who IS NOT NULL AND window_h > 0)
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
