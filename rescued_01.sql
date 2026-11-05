-- rescued_01.sql — stays in phi_hourly_cal rescued by NIV, HFNC or RRT
-- (ENDPOINT_RULE.md dfb9ed9, A9). Treatment only; no outcome measure.
WITH s AS (
  SELECT DISTINCT stay_id
  FROM `project-688c444c-3632-4faa-a13.missh.phi_hourly_cal`
)
SELECT DISTINCT v.stay_id
FROM `physionet-data.mimiciv_3_1_derived.ventilation` v
JOIN s USING (stay_id)
WHERE v.ventilation_status IN ('NonInvasiveVent', 'HFNC')
UNION DISTINCT
SELECT DISTINCT r.stay_id
FROM `physionet-data.mimiciv_3_1_derived.rrt` r
JOIN s USING (stay_id)
WHERE r.dialysis_active = 1
