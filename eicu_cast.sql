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
