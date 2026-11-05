# FAST_GROUP_PREDICTIONS.md — secondary, descriptive predictions for the
# fast (hyper-acute) group, tested ONCE on the 80% test split after signing.
# Derived from calibration exploration E1, E3, E3a, E3b, E4 (docs/EXPLORATORY.md).
# Not part of the registered architecture; no gate; HYPERACUTE_RULE unchanged.

## Populations (test split, first analysable stay, outcome labels per outcome_01)
- Fast: label escalated_hyperacute; hours up to floor(esc_h - 1)
- Stable: label stable; hours 0-4
- Clean hour: not treatment-blocked and not sedated (A13 definitions)
- Channels scaled by calibration SD_pop (SD_POP_TIGHT.txt): HR 3.743,
  MAP 5.941, RR 2.600, SpO2 1.211 (frozen)
- Every result reported with and without DNI before escalation (A11)

## P1. The lock (parts moving as one block)
Pooled consecutive clean hour pairs with HR and MAP present: correlation of
dHR with dMAP; slope reported alongside.
Support: fast r minus stable r > 0, patient-bootstrap 95% CI lower bound > 0.
Calibration hint: 0.39 vs 0.16.

## P2. Fewer recoveries (does not get back into his stance) — WEAK
Recovering step: HR down and MAP up, each |change| >= 1.
Support: fast share minus stable share < 0, CI upper bound < 0.
Calibration hint: 12.5% vs 18%, small numbers.

## P3. Bend with rate (sharp, fast turn toward worsening)
Three consecutive clean hours: (cos(arrow2, w) - cos(arrow1, w)) x |arrow2|,
w = (HR up, MAP down, RR up, SpO2 down), |.| with (4/m) scaling.
Line: calibration stable 95th percentile = 5.434 (frozen, E4_RESULTS).
Per patient: last available triple.
Support: share of fast patients >= line minus share of stable patients >= line
> 0, CI lower bound > 0. Calibration hint: 13.5% vs 5%.

## P4. Combined score adds to NEWS for ranking
At evaluation time t (data through hour index t-1):
- block = z(dHR) x z(dMAP) for the latest clean step
- bend = latest bend with rate (needs 3 consecutive clean hours)
- each converted to its percentile among calibration stable steps/triples;
  missing = 0.5 (neutral); S = mean of the two percentiles (0 to 1)
Ranking at t = 2 and t = 3: fast patients not yet escalated at t, and stable
patients. Compare AUC of reduced NEWS at hour t-1 alone vs NEWS + 3 x S.
Support: AUC difference > 0, CI lower bound > 0. Counts reported: patients
with no measurable step at t.

## Dropped before testing (with reason)
- Time left to MAP 65 (E4): no separation, unstable between 1 and 2 arrows;
  stable patients often sit near 65 at hourly charting
- Proximity to 65 alone: weak (about 30% vs 25%); not included
- Direction-only flag: pre-registered null (HYPER_RESULTS)

## Multiplicity
Four predictions, all reported regardless of outcome; no correction applied;
stated as secondary and descriptive.

## P5. Precision beyond the score at hour 2 (added 2026-11-03, before testing)
Population: target patients (deteriorating, stable, fast), test split.
Early-shape score at hour 2 = mean of stable percentiles of latest arrow
cosine to w, bend with rate (if available, else 0.5) and block (z(dHR)
x z(dMAP)), SD_pop scaling, clean readings from hour 0.
Within reduced-NEWS bands at hour 2 (0-2, 3-4, 5-6):
(a) AUC of the early-shape score for deteriorating within 72 h vs not;
    support: pooled within-band AUC > 0.5, CI lower bound > 0.5
(b) among deteriorating patients, concordance of the score with earlier
    event; support: C > 0.5, CI lower bound > 0.5
(c) repeated excluding patients with MAP <= 66 at hour 2
Secondary and descriptive; reported regardless of outcome.
