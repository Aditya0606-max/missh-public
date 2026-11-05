# D_PRE_NEWS_BRANCHES.md — what each answer will mean, committed before measuring
# Uses REFERENCE_RULE.md (1d5e272) and SD_POP.txt (56dbe50). Calibration split only.
# No displacement, coupling change or escalation-linked measure viewed yet.

## Choices (decided before any outcome is viewed)
- Score: reduced vitals-only NEWS (HR, SBP, RR, SpO2, temperature), as in the
  Oct 10 target group definition
- NEWS crossing (T_NEWS): first hour after the ruler closes with score >= 5
- Primary lookback: 2 h before the anchor; also reported at 4 h and 6 h
- Bar: a route holds if >= 20% of target patients exceed the stable 95th
  percentile at the primary lookback

## Who
- Target: calibration patients in the Oct 10 target group (no vasopressor or
  ventilator, reduced score 0-6 at hour 3) who escalate after the ruler closes
- Ruler tiers A and B only; tier C reported separately (direction track)
- Anchor: T_NEWS if NEWS crosses before escalation; otherwise escalation time,
  reported as its own group (the compensating patients)
- Patients whose anchor falls before ruler close + lookback: counted and
  reported, not measured at that lookback
- Patients already at NEWS >= 5 when the ruler closes: reported separately

## What is measured
- D: distance from his own ruler, D = sqrt( (4/m) x sum of z^2 )
- Coupling change: |delta rho| over the 4 h window ending at the lookback,
  against his ruler-period rho (rho_base); rho_base reported alongside
- Stable comparison: stable calibration patients, same ruler procedure,
  sampled at matched clock times; their 95th percentile is the bar line

## The four branches (primary lookback, each group separately)
1. Displacement route real: D bar met, coupling bar not met
2. Coupling route real: coupling bar met, D bar not met
3. Both: both bars met
4. Neither: neither bar met. Interpreted as: four vital signs at hourly
   charting do not carry enough early information for this route design;
   next work points to lactate, capillary refill or denser monitoring

## Known tilts, stated in advance
- D: a short ruler can understate wobble; the stable comparison uses the
  same ruler procedure, so the bias applies to both sides
- Coupling: deterioration inside the ruler window lowers rho_base and so
  lowers |delta rho|; rho_base is reported so this can be seen

## Directed distance (added before measurement, 2026-11-02)
- Alongside D, report D_w = D x cos(net travel, w): how far his arrow from his
  own ruler centre reaches along w = (HR up, MAP down, RR up, SpO2 down).
  Negative D_w = moved toward improvement.
- Bar for D_w: tightened-stable 95th percentile at matched clock times; the
  20% rule on D_w reported beside the D branch result. The four branches
  remain as committed on D.
