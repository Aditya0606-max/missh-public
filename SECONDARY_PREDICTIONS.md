# SECONDARY_PREDICTIONS.md — main-group secondary predictions (2026-11-03)
# Tested ONCE on the 80% test split after signing. Derived from calibration
# (SUMMARY_P3 4c10b20, CONJUNCTION 825eb5c). Not a gate; claim unchanged.

## P6. Heart defending more often before deterioration
Measure: share_defend as in measure_p3.py (2a16302): in the 6 h ending at the
lookback hour, among clean consecutive-hour steps with |dHR| >= 1 bpm and
|dMAP| >= 1 mmHg (at least 2 such steps), the share with HR up and MAP down.
Clean = not blocked (A14). Same symmetric sampling as part 3.
Populations: target deteriorating at 1, 2 and 4 h before anchor (anchors as
anchors_02.py); target stable at every hour from watching open.
Comparison: matched AUC against tightened-stable rows of the same tier
within +-1 h (widening to +-3 h, then all tiers, if < 30), as summarize_p1.py.
Primary: k = 2 h. Support: matched AUC > 0.5 with patient-bootstrap 95% CI
lower bound > 0.5. Also reported: k = 1 and 4 h, and the same-NEWS version
(>= 4 NEWS items, same NEWS band).
Calibration result: AUC 0.561 (0.517-0.599) at 2 h; same NEWS 0.573
(0.531-0.614).

## P7. The readout's kind of instability matches the first escalation (2026-11-03)
Population: target deteriorating with label 'escalated' (anchors_02, outcome_01).
Readout at the anchor (k = 0; also k = 2 h): z = (state - ruler centre) / ruler
width (main ruler per A15, state as measure_p1.py). Pressure share =
(z_HR^2 + z_MAP^2) / sum of z^2 over channels present; breathing share =
(z_RR^2 + z_SpO2^2) / same. Requires HR, MAP and at least one of RR, SpO2.
Pressure-led: pressure share > 2/3; breathing-led: breathing share > 2/3;
otherwise mixed.
First escalation type (esc_type_01.sql): vasopressor first, ventilator first,
or both in the same minute.
Support: share vasopressor-first among pressure-led minus among breathing-led
> 0, patient-bootstrap 95% CI lower bound > 0 (primary k = 0).
Rehearsed on the 20% (E9); recipe unchanged after viewing; tested once on the 80%.

## P7. The readout's kind of instability matches the first escalation (2026-11-03)
Population: target deteriorating with label 'escalated' (anchors_02, outcome_01).
Readout at the anchor (k = 0; also k = 2 h): z = (state - ruler centre) / ruler
width (main ruler per A15, state as measure_p1.py). Pressure share =
(z_HR^2 + z_MAP^2) / sum of z^2 over channels present; breathing share =
(z_RR^2 + z_SpO2^2) / same. Requires HR, MAP and at least one of RR, SpO2.
Pressure-led: pressure share > 2/3; breathing-led: breathing share > 2/3;
otherwise mixed.
First escalation type (esc_type_01.sql): vasopressor first, ventilator first,
or both in the same minute.
Support: share vasopressor-first among pressure-led minus among breathing-led
> 0, patient-bootstrap 95% CI lower bound > 0 (primary k = 0).
Rehearsed on the 20% (E9); recipe unchanged after viewing; tested once on the 80%.
