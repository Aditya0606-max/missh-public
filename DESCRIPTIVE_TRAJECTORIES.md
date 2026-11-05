
## Individual patients (added before the 80% run, 2026-11-03)
1. Per-patient alarm outcome, for every target deteriorating patient: alarm
   (FLAG_FROZEN and FLAG_SENS_FROZEN) fired before NEWS crossing, at the same
   hour, after, or never; hours of lead; reported as a distribution (counts
   and shares), overall and by time-to-deterioration group and tier.
2. Treatment context: for each deteriorating patient, whether the 4 h before
   the anchor contained a blocked hour (bolus, IV BP/rate drug, sedative
   infusion) or a flagged hour (oral BP, single sedative dose). All primary
   and secondary results also reported separately for patients with and
   without treatment in that window.
3. Case atlas: 20 deteriorating and 20 stable target patients drawn at random
   (numpy seed 2026, drawn after the run from the eligible lists, never
   replaced). Each shown as an hourly timeline: HR, MAP, RR, SpO2, reduced
   NEWS, cosine and Dw_main, share_defend, alarm state, and every bolus, IV
   drug and sedative interval. Anonymised (no dates, no identifiers).
Descriptive only; no claim rests on it.

## Stable baseline for the gradual-climb pattern (added before the 80% run, 2026-11-03)
For tightened-stable target patients: share of patients, and of 3-hour windows,
with cosine (Dw_main / D_main) >= 0.3 in at least 2 of 3 consecutive hours
(the gradual-climb criterion), over hours from watching open to 71; and the
share of those windows followed by the sensitivity alarm within the window.
Reported beside the gradual-climb group, so the alarm's early catches in that
group can be weighed against how often stable patients show the same pattern.
