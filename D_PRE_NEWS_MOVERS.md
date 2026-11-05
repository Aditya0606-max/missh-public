# D_PRE_NEWS_MOVERS.md — addendum to D_PRE_NEWS_BRANCHES.md (49e83e5)
# Lead time and precision by kind of mover. Committed before any
# displacement, coupling or escalation-linked measure is viewed.
# DESCRIPTIVE ONLY: no inferential weight, never a gate.

## Mover groups (target patients, ruler tiers A and B)
D_anchor = distance from his own ruler at the anchor (T_NEWS, or escalation
time for patients whose NEWS never crosses).
Lines come from stable calibration patients, same ruler procedure, matched
clock times:
- Slow (compensating): D_anchor <= stable 95th percentile
- Medium:              stable 95th < D_anchor <= stable 99th percentile
- Big:                 D_anchor > stable 99th percentile
Counts reported per group, separately for NEWS-anchored and
escalation-anchored patients.
Secondary: the same tables by tertiles of D_anchor.
Groups use D at the anchor, i.e. later information, so they describe
patients after the fact and can never be used to route or gate.

## Direction agreement
Net-travel cosine: cosine between his net travel (current state minus ruler
centre, per channel in his own wobbles) and the worsening direction
w = (HR up, MAP down, RR up, SpO2 down). Reported per group at each lookback.

## Flag used for lead time
The displacement-route flag as frozen by calibration (threshold, direction
agreement, persistence in hours). This addendum fixes the grouping and the
quantities; calibration fixes the flag.

## Lead time, per group
- Lead = T_anchor - T_flag, in hours (resolution: 1 h)
- Reported: median and IQR; share with lead >= 1 h, >= 2 h, >= 4 h
- Patients not flagged before the anchor: counted, lead recorded as none

## Precision, per group
- Among all flags fired in the calibration split (deteriorating and stable
  patients over matched clock time), the share belonging to deteriorating
  patients, by the D level at which the flag fired
- Stable flag rate per patient-day reported alongside, and the share of
  deteriorating patients in the population stated, since precision
  depends on it

## Claims this addendum allows, if the data supports them
- Big movers: a high-precision flag, at or slightly ahead of NEWS, with the
  direction of travel reported to the clinician
- Medium movers: hours of lead, delivered as ranking
- Slow movers: measured honestly; a weak result points to registration 2
No claim is made for any group before measurement.
