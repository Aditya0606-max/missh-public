# CALIBRATION_RULE.md — how the registered flag's settings are chosen (2026-11-03)
# Written before any setting is evaluated. Calibration split only.

Flag: directed distance Dw_main (main ruler per A15; provisional before hour 3
for tiers A/B) above a line L_q(h) = q-th percentile of tightened-stable
Dw_main at the same ICU hour h. Decaying counter (unified pause rule 8e41802,
A13/A14): +1 when beyond, -1 when a clean hour is not beyond (floor 0); blocked
or missing hours pause. Fires when counter >= p; fire time = end of that hour.
Grid: q in {0.90, 0.95, 0.975, 0.99}; p in {1, 2, 3, 4}.
Stable false alarms: share of target stable patients firing at least once
between watching open and hour 71; also fires per patient-day.
Deteriorating: share firing at least 1 h before anchor; at least 2 h;
median lead (anchor - fire time) among those firing >= 1 h before.
Selection: among settings with stable patients ever firing <= 10%, choose the
one with the highest deteriorating share firing >= 1 h before anchor; ties go
to the larger p, then the larger q. If no setting meets the 10% limit, choose
the setting with the lowest stable share and record it.
The chosen (q, p) and its lines L_q(h) are frozen for the 80%.
