# HYPERACUTE_RULE.md — reading Kranthi with no ruler, by direction only
# Committed before any outcome is viewed. Separate estimand; never pooled
# with the ruler-based routes (REFERENCE_RULE.md, 1d5e272).

## Who
- Patients escalating after hour 3 but before the ruler closes (hour 5)
- Patient tier C (no ruler: too many missing reference hours), all hours
- Runs from hour 0 for every patient as a descriptive track (never dark)

## What is read
- Worsening direction w = (HR up, MAP down, RR up, SpO2 down), unit vector
- Each hour: step = change from the previous clean hour, per channel,
  divided by that channel's device floor (OMEGA_SCALE_RULE: HR 1 bpm,
  MAP 1 mmHg, RR 1 /min, SpO2 1 %)
- Direction score: cosine between the step and w, over channels present (m >= 2)
- Size gate: at least 2 channels moved by more than their device floor

## Flag
- Flag when the direction score >= c AND the size gate is met
  for k consecutive clean hours
- c and k are set on stable calibration patients' first 5 hours (same
  no-ruler condition, no outcome labels): the pair giving a stable flag
  rate <= 5%, with the smallest k preferred
- Missing hours follow the unified pause rule (8e41802)

## What it claims
- That the architecture is not silent on the fastest-escalating quarter
- Not a lead-time claim: these patients escalate at a median under 4.2 h,
  so the flag may come shortly before escalation
- Reported as its own group: share flagged before escalation, hours before

## What it does not do
- No coupling: delta rho needs a rho_base, which needs a ruler
- No population SD: magnitude uses device precision only
