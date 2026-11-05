# PRIMARY_COMPARISON.md — the first table of every report (pre-measurement)

## Cohorts
- Target group: reduced NEWS 0-6 at hour 3 (news_01), first analysable stay
- Deteriorating: label escalated (5-72 h) or death_counts (outcome_01, A9-A11)
- Stable: label stable (tightened, A10)
- Reported separately, not in either cohort: escalated_hyperacute
  (FAST_GROUP_PREDICTIONS), rescued, escalated_after_72h, death_comfort, other

## Matching
- Deteriorating: values at anchor - 2, 4, 6 h (anchor = T_NEWS or escalation)
- Stable: values at the same ICU clock hours

## Measures, both cohorts side by side
D, directed distance D_w, net-travel cosine, consistency, straightness,
speed, bend with rate, counter level and hours without return, coupling
change (exploratory), reduced NEWS; share beyond the stable 95th line for
D, D_w and bend

## Relationships
- Pooled step correlation and slope for all six pairs (HR-MAP, RR-SpO2,
  HR-SpO2, HR-RR, MAP-RR, MAP-SpO2), clean unsedated consecutive hours.
  HR-MAP is the only pair with a prior hint (E3); the other five are
  descriptive; SpO2 pairs limited by ceiling and oxygen therapy
- Lead pair: the pair with the largest share of his net travel (sum of the
  two channels' squared z over the total). Its pooled step correlation is
  reported per cohort; stable lead pairs found by the same rule. Shared drift
  can inflate step correlation; the same-rule stable comparison is the control

## Breakdowns (descriptive only)
By mover group, charting tier, anchor type, with and without DNI.
Groups never set or judge the rule.

## Origin-based lookbacks for everyone (added before measurement, 2026-11-03)
ANCHOR_COUNTS: only 321 of 699 target deteriorating patients have an anchor
>= 2 h after yardstick close. In parallel with the ruler-based reading, every
target patient is also read from his origin (first clean reading from hour 0;
first reading of any kind if none, flagged), width = SD_pop: distance and
directed distance from origin, arrow cosine, bend with rate, block, each as a
tightened-stable percentile at the same ICU hour, at anchor - 1 and - 2 h
(any lookback at or after his second reading). Stable comparators read the
same way at matched clock hours and tier. Reported for all target
deteriorating, and separately for those ineligible under the ruler.
Descriptive and secondary to the ruler-based primary.
