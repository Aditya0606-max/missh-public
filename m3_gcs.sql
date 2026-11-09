SELECT g.icustay_id, DIV(DATETIME_DIFF(CAST(g.charttime AS DATETIME), CAST(i.intime AS DATETIME), MINUTE), 60) AS hour, MIN(g.gcs) AS gcs
FROM `physionet-data.mimiciii_derived.pivoted_gcs` g JOIN `physionet-data.mimiciii_clinical.icustays` i USING (icustay_id)
WHERE g.gcs IS NOT NULL GROUP BY 1, 2
HAVING hour BETWEEN -12 AND 120
