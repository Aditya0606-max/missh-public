# REFERENCE_RULE.md — Kranthi's ruler (admission reference) for MIMIC-IV hourly data
# Written AFTER phi (6e8b3fb) and early-hour feasibility (f3286d6) were measured,
# outcome-blind, on the calibration split only. No displacement, D_pre-NEWS,
# coupling change or escalation-linked performance measure has been viewed.

## Choices (decided before any outcome is viewed)
- phi used for planning: 0.35 for all channels (HR, the stickiest, ~0.33 at 16h+)
- Target independent looks: 2
- Main ruler: blended, opens at hour 3, frozen at hour 5
- Sensitivity arms (pre-committed, all reported): blended frozen at hour 2;
  own-data frozen at hour 8
- Gap tolerance: at least 4 of 5 reference hours clean per channel
- Rulers are built per channel, independently

## Effective looks
n_eff = n_clean x (1 - phi) / (1 + phi), phi = 0.35

## Center (where his normal sits)
- His own mean over clean reference hours, per channel. Never borrowed.

## Width (his normal wobble), per channel
- SD_own: SD of his clean reference hours after removing a linear trend
- SD_pop: median within-patient detrended SD of stable calibration patients,
  computed by a committed script on missh.phi_hourly_cal before any outcome
  is viewed
- Blend: SD^2 = (n_eff x SD_own^2 + 2 x SD_pop^2) / (n_eff + 2)
  (stable patients count as 2 looks; his own data dominates as hours add)
- SD_used = max(SD blend, device floor)  [OMEGA_SCALE_RULE]
- Frozen when the ruler closes; never recomputed

## Tiers (assigned by rule, per patient)
- Channel tier A: all reference hours clean
- Channel tier B: at least the gap tolerance clean
- Channel tier C: fewer -> no ruler for that channel
- Patient tier A: all four channels A
- Patient tier B: HR and MAP both have a ruler (A or B)
- Patient tier C: otherwise -> direction track only (HYPERACUTE_RULE)

## After the ruler closes
- Missing hours: unified pause rule (8e41802); persistence counter neither
  advances nor resets
- Missing channel at an hour: distance over the m channels present,
  D = sqrt( (4/m) x sum of z^2 ), m >= 2, hour flagged partial
- Treatment hours: as PHI_TREATMENT_ADDENDUM.md

## Reporting
- Every result reported by patient tier with counts
- No patient excluded for missing data
