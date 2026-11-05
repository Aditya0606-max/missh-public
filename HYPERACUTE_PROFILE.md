# HYPERACUTE_PROFILE.md — path profile for no-ruler patients
# Addendum to HYPERACUTE_RULE.md (d820e29). Committed before any
# outcome-linked measure is viewed. DESCRIPTIVE ONLY, never a gate.

## Who
- escalated_hyperacute (escalation 3-5 h, outcome_01.sql d1c617e)
- Patient tier C, all hours

## Starting point
- First clean hour (not treatment-blocked, m >= 2 channels) = origin
- All changes in device-floor units (OMEGA_SCALE_RULE: HR 1 bpm,
  MAP 1 mmHg, RR 1 /min, SpO2 1 %)

## Path measures, from origin to each hour up to escalation
- Net travel: distance from origin
- Speed: net travel / hours since origin; also median hourly step length
- Straightness: net travel / path length (1 = straight)
- Net-travel cosine with w = (HR up, MAP down, RR up, SpO2 down)
- Consistency: share of hourly steps with positive cosine to w
- Blocked hours paused (8e41802); partial hours use channels present

## Comparison
- Tightened stable group (1,437, A10), first 5 hours, same origin rule:
  median, 95th and 99th percentile lines for every measure

## Reported
- Per measure: median and IQR, at each hour before escalation
- Share of hyperacute patients beyond the stable 95th line, and the hour
  that first happens relative to escalation
- With and without DNI (A11)
- No lead-time claim beyond what these numbers show

## Actionability (added before measurement, 2026-10-31)
- Lead over first clinician action: hours between the first time a patient
  passes the stable 95th line (cosine and speed together) and his first
  treatment block (bolus or BP/rate drug, PHI_TREATMENT_ADDENDUM.md);
  reported alongside lead over escalation
- Which path carries the travel: share of net travel (squared z, device-floor
  units) from MAP+HR (pressure-led) versus RR+SpO2 (breathing-led), reported
  per patient as pressure-led, breathing-led or mixed (neither share > 2/3)
- Precision: among patients passing the line (fast group + stable first 5 h),
  share who are fast-group, stated with the group sizes it depends on
