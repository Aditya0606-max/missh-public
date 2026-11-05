# D_PRE_NEWS_PROFILE.md — path profile per mover group
# Addendum to D_PRE_NEWS_MOVERS.md (0703aaf). Committed before any
# displacement, coupling or escalation-linked measure is viewed.
# DESCRIPTIVE ONLY: never a gate; the frozen displacement-route flag decides.

## Window
From ruler close to each lookback (2, 4, 6 h before the anchor); also the
last 4 h before each lookback. Channels and z-scores per REFERENCE_RULE.md.

## Path measures (in his own wobbles, z units)
- Net travel: distance from ruler centre to his state at the lookback
- Path length: sum of hourly step lengths over the window
- Speed: net travel / hours in window; also median hourly step length
- Straightness: net travel / path length (1 = straight, near 0 = wandering)
- Net-travel cosine: cosine of net travel with w = (HR up, MAP down,
  RR up, SpO2 down)
- Consistency: share of hourly steps with positive cosine to w
Missing hours follow the unified pause rule (8e41802); partial hours
use channels present per REFERENCE_RULE.md.

## Reported per mover group (slow / medium / big), per anchor type
- Each path measure: median and IQR
- Alongside: distance D, coupling change (exploratory), reduced NEWS
- The same measures for the tightened stable group (1,437, A10) at
  matched clock times: median, 95th and 99th percentile lines

## Clinician readout (format only, filled after calibration)
Direction of travel, speed, straightness, which channels moved most,
distance from his own admission state.

## Bend with rate (added before measurement, 2026-11-02)
- Three consecutive clean hours: (cos(arrow2, w) - cos(arrow1, w)) x |arrow2|,
  arrows in his own wobbles (REFERENCE_RULE ruler)
- Reported per mover group (slow / medium / big) at each lookback, with the
  hour of the first bend above the tightened-stable 95th line relative to
  the anchor (T_NEWS or escalation)
- Big movers: reported alongside distance, cosine and consistency, as the
  precision profile; descriptive only, never a gate

## Relationship alongside the vector (added before measurement, 2026-11-02)
- Pooled step correlation and slope for HR-MAP and the lead pair (see
  PRIMARY_COMPARISON.md), 6 h before each anchor, per mover group and anchor
  type, vs tightened stable at matched clock hours
- Step kinds: defending, recovering, both down, both up, flat
- Descriptive only; patient-bootstrap 95% CIs; never a gate

## Early shape, from hour 0 (added before measurement, 2026-11-03)
- For every target patient (deteriorating and stable), arrow cosine to w,
  bend with rate, and moving-as-one-block, computed from his first clean
  readings onward (hour 0-5), scaled by SD_pop; no ruler needed
- Each value also given as its percentile among tightened-stable patients
  at the same ICU hour (precision: how unusual, not just how high)
- Reported per cohort and per mover group; descriptive only, never a gate
