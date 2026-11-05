# RESULTS_80 — Registration 1, test split (run once after reg1-signed)

## Primary A — four branches, 2 h before anchor (SUMMARY_P1, SUMMARY_P3)
Distance: D_main beyond 0.039 (0.026-0.055), Dw_main 0.033 (0.021-0.046), n=769.
Coupling: drho beyond 0.045 (0.026-0.068), n=310 of 1090.
All below the 0.20 bar. Result: Branch 4, neither.
Noted: D_main AUC 0.463 (0.439-0.485), entirely below 0.5.

## Primary B — ranking (RANK_REHEARSAL)
NEWS + main alarm gain: 2 h -0.005 (-0.006 to -0.003); 4 h -0.004 (-0.005 to -0.002).
Entirely below 0: the alarm slightly worsens the ranking.
Main alarm active: deteriorating 0.005 vs stable 0.020 of hours.

## Primary sentence (as registered in PROTOCOL_FINAL.md)
"At hourly charting, reading septic ICU patients' vital signs as movement in
state space did not add to NEWS before deterioration; the slide was held behind
compensation and treatment until about the final hour."
The first clause is the tested result; the second is the interpretation
carried from calibration, consistent with but not tested by the 80%.

## Secondary — combined model, A16 (D2_COMBINED.txt, D2)
Reproduced AUC A 0.863, AUC B 0.858 at k = 2 h (confirms test data; N2 label only).
Gain B - A, patient-bootstrap 95% CI (300 resamples):
k=1 -0.003 (-0.006 to +0.000); k=2 -0.004 (-0.007 to -0.001) [primary];
k=4 -0.008 (-0.012 to -0.004). A16: SUPPORT=no. Adding the 15 architecture
measures slightly worsened ranking, most at 4 h.

## Descriptive — agreement (CONJUNCTION.txt, COS_LONG.txt)
ALL conditions: deteriorating 0.0015 / 0.0000 / 0.0013 at 1/2/4 h vs stable 0.0010 per hour.
Pairs C1&C2, C1&C3, C1&C4 about equal to stable. C2&C3 higher in deteriorating
(0.019 / 0.029 / 0.027 vs 0.015); C3 alone 0.093 at 2 h vs 0.059. Unmatched to
tier and hour (P6, matched, was 0.497); no intervals; hypothesis for registration 2 only.
Cosine, real arrows: matched AUC 0.48-0.53 at 2/4/6 h, ruler and origin. The
calibration lean away from shock (E10, AUC 0.44) did not replicate.

## Check — P4 oddity (FAST_80_RESULTS, P45_RESULTS, fast_80.py)
NEWS AUC ~0.23 reproduces calibration (0.227/0.238 vs 0.233/0.234); not a
pipeline error. Labels are standard (y=1 fast, fast_80.py line 132): at t=2-3,
fast patients not yet escalated had lower NEWS than stable patients. Possible
explanations, untested: selection on ordinary NEWS at hour 3; treatment lowering
NEWS. P4 verdict unchanged (difference ~0). About 90% of fast patients had no
measurable step in both splits; per A14 this reflects treatment-blocked hours
(most treated patients, ~1.1 clean of 12 h), not short stays or missing charting.
