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
st AS (SELECT patientunitstayid, MIN(respchartoffset) / 60 AS h FROM `physionet-data.eicu_crd.respiratorycharting`
       WHERE REGEXP_CONTAINS(LOWER(respchartvaluelabel), r'tidal volume|peep|vent rate|ventilator mode|^mode$|set fraction of inspired oxygen')
         AND patientunitstayid IN (SELECT patientunitstayid FROM s) GROUP BY 1),
et AS (SELECT patientunitstayid, MIN(o) / 60 AS h FROM (
         SELECT patientunitstayid, nursingchartoffset AS o FROM `physionet-data.eicu_crd.nursecharting`
         WHERE nursingchartcelltypevalname = 'O2 Admin Device' AND REGEXP_CONTAINS(LOWER(nursingchartvalue), r'\bett\b|endotrach|ventilator|\bvent\b')
         UNION ALL SELECT patientunitstayid, respchartoffset FROM `physionet-data.eicu_crd.respiratorycharting`
         WHERE REGEXP_CONTAINS(LOWER(respchartvaluelabel), r'^o2 device$|oxygen delivery method')
           AND REGEXP_CONTAINS(LOWER(respchartvalue), r'\bett\b|endotrach|ventilator|\bvent\b'))
       WHERE patientunitstayid IN (SELECT patientunitstayid FROM s) GROUP BY 1),
x AS (SELECT s.*, v.vaso_h, rc.h AS rc_h, tx.h AS tx_h, st.h AS st_h, et.h AS et_h,
        LEAST(IFNULL(rc.h, 1e9), IFNULL(tx.h, 1e9)) AS vent_off,
        LEAST(IFNULL(rc.h, 1e9), IFNULL(tx.h, 1e9), IFNULL(st.h, 1e9), IFNULL(et.h, 1e9)) AS vent_e,
        LEAST(IFNULL(st.h, 1e9), IFNULL(et.h, 1e9)) AS sign_h,
        REGEXP_CONTAINS(LOWER(IFNULL(s.unitadmitsource, '')), r'operating|recovery|pacu') AS planned
      FROM s LEFT JOIN v USING (patientunitstayid) LEFT JOIN rc USING (patientunitstayid) LEFT JOIN tx USING (patientunitstayid)
      LEFT JOIN st USING (patientunitstayid) LEFT JOIN et USING (patientunitstayid)),
y AS (SELECT *, LEAST(IFNULL(vaso_h, 1e9), vent_off) AS t1, LEAST(IFNULL(vaso_h, 1e9), vent_e) AS t2 FROM x),
z AS (SELECT *,
  CASE WHEN t1 >= 1e9 AND hospitaldischargestatus = 'Alive' THEN 'Ajay'
       WHEN t1 >= 1e9 OR t1 <= 0 OR (t1 <= 3 AND planned) THEN 'excluded'
       WHEN t1 <= 3 THEN 'Naveen' WHEN t1 < 5 THEN 'excluded'
       WHEN vaso_h IS NOT NULL AND vent_off < 1e9 AND ABS(vaso_h - vent_off) <= 1 THEN 'mixed'
       WHEN vaso_h IS NOT NULL AND vaso_h < vent_off THEN 'Kranthi' ELSE 'Sundar' END AS who_off,
  CASE WHEN t2 >= 1e9 AND hospitaldischargestatus = 'Alive' THEN 'Ajay'
       WHEN t2 >= 1e9 OR t2 <= 0 OR (t2 <= 3 AND planned) THEN 'excluded'
       WHEN t2 <= 3 THEN 'Naveen' WHEN t2 < 5 THEN 'excluded'
       WHEN vaso_h IS NOT NULL AND vent_e < 1e9 AND ABS(vaso_h - vent_e) <= 1 THEN 'mixed'
       WHEN vaso_h IS NOT NULL AND vaso_h < vent_e THEN 'Kranthi' ELSE 'Sundar' END AS who_new
  FROM y)
SELECT who_off, who_new, COUNT(*) AS n,
  COUNTIF(et_h IS NOT NULL) AS with_tube_sign, COUNTIF(et_h IS NULL AND st_h IS NOT NULL) AS settings_only
FROM z WHERE who_off != who_new GROUP BY 1, 2 ORDER BY n DESC