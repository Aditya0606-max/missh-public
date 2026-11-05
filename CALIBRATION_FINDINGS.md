
Flag calibration (CALIBRATION.txt, FLAG_FROZEN.json): rule CALIBRATION_RULE.md
chose q = 0.95, p = 4 (stable ever-alarmed 7.2%; deteriorating flagged >= 1 h
before anchor 0.2%). Per hour, deteriorating patients cross the line ~3-4x as
often as stable, but stable patients are watched ~70 h vs ~4-5 h, so any
setting with few false alarms gives almost no early flags. No practical lead
time at hourly charting on calibration. Settings frozen for the 80%.

E10 (COS_LONG.txt, 88bf274): restricting to real arrows (D > 1 or > 3
wobbles) did not reveal early direction toward shock. Matched AUC of cosine
0.44-0.49 at 2, 4, 6 h (ruler and origin); with D > 3 at 2 h, deteriorating
median cosine -0.23 vs stable -0.06. Long arrows of deteriorating patients
lean slightly away from shock before the anchor, consistent with treatment
and compensation pushing numbers back. Descriptive; supports counting
support as part of state in registration 2.

E12 (BOLUS_RESPONSE.txt): first bolus, stable n=406 vs deteriorating n=75.
MAP lift (~5-6 mmHg) and wear-off (~2 h; 77% vs 73%) similar; anchor after
wear-off 53% (coin toss). Hint: HR eased ~2 bpm within 1 h in stable but not
in deteriorating for 2-3 h. Descriptive; carried to registration 2 as an
effort question (does the heart relax when support is given?).
