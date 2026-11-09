SELECT w.patientunitstayid, w.who, w.window_h, MIN(vp.observationoffset) AS first_vital_min
FROM w LEFT JOIN `physionet-data.eicu_crd.vitalperiodic` vp
  ON vp.patientunitstayid = w.patientunitstayid AND vp.observationoffset >= 0
 AND (vp.heartrate IS NOT NULL OR vp.respiration IS NOT NULL OR vp.sao2 IS NOT NULL)
GROUP BY 1, 2, 3
