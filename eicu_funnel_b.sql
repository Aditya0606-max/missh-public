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
