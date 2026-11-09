WITH cv AS (
  SELECT c.icustay_id, CAST(c.charttime AS DATETIME) AS t, c.amount AS ml,
    IF(REGEXP_CONTAINS(LOWER(d.label), r"albumin|hespan|hetastarch|dextran"), "colloid", "crystalloid") AS kind
  FROM `physionet-data.mimiciii_clinical.inputevents_cv` c
  JOIN `physionet-data.mimiciii_clinical.d_items` d USING (itemid)
  WHERE c.amount >= 250 AND LOWER(c.amountuom) = "ml"
    AND (c.itemid IN (30018, 30021)
         OR REGEXP_CONTAINS(LOWER(d.label), r"bolus|albumin|hespan|hetastarch"))
    AND NOT REGEXP_CONTAINS(LOWER(d.label), r"water|h2o|h20|feed|blood")
),
mv AS (
  SELECT m.icustay_id, CAST(m.starttime AS DATETIME) AS t,
    IF(LOWER(m.amountuom) = "l", m.amount * 1000, m.amount) AS ml,
    IF(REGEXP_CONTAINS(LOWER(d.label), r"albumin|hetastarch|hespan|dextran"), "colloid", "crystalloid") AS kind
  FROM `physionet-data.mimiciii_clinical.inputevents_mv` m
  JOIN `physionet-data.mimiciii_clinical.d_items` d USING (itemid)
  WHERE m.statusdescription != "Rewritten"
    AND (m.itemid IN (225158, 225828, 225159, 225823, 225825, 225827, 225941)
         OR REGEXP_CONTAINS(LOWER(d.label), r"albumin|hetastarch|hespan"))
    AND ((m.rate IS NOT NULL AND m.rateuom = "mL/hour" AND m.rate > 248)
      OR (m.rate IS NULL AND LOWER(m.amountuom) = "ml" AND m.amount > 248)
      OR (m.rate IS NULL AND LOWER(m.amountuom) = "l" AND m.amount > 0.248))
)
SELECT b.icustay_id, DATETIME_DIFF(b.t, CAST(i.intime AS DATETIME), MINUTE) / 60 AS h, b.ml, b.kind
FROM (SELECT * FROM cv UNION ALL SELECT * FROM mv) b
JOIN `physionet-data.mimiciii_clinical.icustays` i USING (icustay_id)
