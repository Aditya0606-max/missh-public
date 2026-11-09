WITH s AS (SELECT patientunitstayid, unitadmitsource, hospitaldischargestatus FROM `physionet-data.eicu_crd.patient`
           WHERE LOWER(apacheadmissiondx) LIKE '%sepsis%' AND unitvisitnumber = 1
             AND (SAFE_CAST(REGEXP_REPLACE(age, r'[^0-9]', '') AS INT64) >= 18 OR age LIKE '%>%')),
v AS (SELECT patientunitstayid, MIN(infusionoffset) / 60 AS vaso_h FROM `physionet-data.eicu_crd.infusiondrug`
      WHERE patientunitstayid IN (SELECT patientunitstayid FROM s)
        AND REGEXP_CONTAINS(LOWER(drugname), r'norepinephrine|levophed|vasopressin|epinephrine|phenylephrine|neo-synephrine|neosynephrine|dopamine')
        AND SAFE_CAST(drugrate AS FLOAT64) > 0 GROUP BY 1),
rc AS (SELECT patientunitstayid, MIN(ventstartoffset) / 60 AS h FROM `physionet-data.eicu_crd.respiratorycare`
       WHERE ventstartoffset IS NOT NULL AND ventstartoffset != 0 AND patientunitstayid IN (SELECT patientunitstayid FROM s) GROUP BY 1),
tx AS (SELECT patientunitstayid, MIN(treatmentoffset) / 60 AS h FROM `physionet-data.eicu_crd.treatment`
       WHERE LOWER(treatmentstring) LIKE '%mechanical ventilation%' AND patientunitstayid IN (SELECT patientunitstayid FROM s) GROUP BY 1),
et AS (SELECT patientunitstayid, MIN(o) / 60 AS h FROM (
         SELECT patientunitstayid, nursingchartoffset AS o FROM `physionet-data.eicu_crd.nursecharting`
         WHERE nursingchartcelltypevalname = 'O2 Admin Device' AND REGEXP_CONTAINS(LOWER(nursingchartvalue), r'\bett\b|endotrach|ventilator|\bvent\b')
         UNION ALL SELECT patientunitstayid, respchartoffset FROM `physionet-data.eicu_crd.respiratorycharting`
         WHERE REGEXP_CONTAINS(LOWER(respchartvaluelabel), r'^o2 device$|oxygen delivery method')
           AND REGEXP_CONTAINS(LOWER(respchartvalue), r'\bett\b|endotrach|ventilator|\bvent\b'))
       WHERE patientunitstayid IN (SELECT patientunitstayid FROM s) GROUP BY 1),
x AS (SELECT s.*, v.vaso_h, LEAST(IFNULL(rc.h, 1e9), IFNULL(tx.h, 1e9), IFNULL(et.h, 1e9)) AS vent_h,
        REGEXP_CONTAINS(LOWER(IFNULL(s.unitadmitsource, '')), r'operating|recovery|pacu') AS planned
      FROM s LEFT JOIN v USING (patientunitstayid) LEFT JOIN rc USING (patientunitstayid)
      LEFT JOIN tx USING (patientunitstayid) LEFT JOIN et USING (patientunitstayid)),
y AS (SELECT *, LEAST(IFNULL(vaso_h, 1e9), vent_h) AS tip FROM x),
z AS (SELECT *, CASE
  WHEN tip >= 1e9 AND hospitaldischargestatus = 'Alive' THEN 'Ajay'
  WHEN tip >= 1e9 AND hospitaldischargestatus = 'Expired' THEN 'died without escalation'
  WHEN tip >= 1e9 THEN 'no tip, discharge status missing'
  WHEN tip <= 0 THEN 'arrived on support'
  WHEN tip <= 3 AND planned THEN 'planned early escalation'
  WHEN tip <= 3 THEN 'Naveen'
  WHEN tip < 5 THEN 'grey zone (3-5 h)'
  WHEN vaso_h IS NOT NULL AND vent_h < 1e9 AND ABS(vaso_h - vent_h) <= 1 THEN 'mixed'
  WHEN vaso_h IS NOT NULL AND vaso_h < vent_h THEN 'Kranthi' ELSE 'Sundar' END AS row_ FROM y)
SELECT row_, COUNT(*) AS stays FROM z GROUP BY 1
UNION ALL SELECT 'TOTAL', COUNT(*) FROM z
ORDER BY stays DESC
