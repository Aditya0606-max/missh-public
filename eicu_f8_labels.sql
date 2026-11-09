SELECT 'respiratorycharting' AS tbl, respchartvaluelabel AS label, COUNT(*) AS n FROM `physionet-data.eicu_crd.respiratorycharting`
WHERE REGEXP_CONTAINS(LOWER(respchartvaluelabel), r'fio2|fi o2|o2 device|delivery device|oxygen') GROUP BY 1, 2
UNION ALL
SELECT 'nursecharting', nursingchartcelltypevalname, COUNT(*) FROM `physionet-data.eicu_crd.nursecharting`
WHERE REGEXP_CONTAINS(LOWER(nursingchartcelltypevalname), r'fio2|o2 l/%|o2 admin device|gcs total|glasgow') GROUP BY 1, 2
ORDER BY n DESC LIMIT 40
