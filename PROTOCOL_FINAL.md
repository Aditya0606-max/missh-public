# Miss H x VEVFM — Registration 1: final protocol (signed before the 80% run)

## Question
In septic ICU patients who look ordinary on NEWS at hour 3, does reading their
hourly vital signs as movement in state space (distance and direction from their
own normal, path, relationships) add to NEWS before deterioration?

## Data and split
MIMIC-IV v3.1 (BigQuery). Sepsis-3 first ICU stays, analysable at hour 3
(funnel_01.sql). Patient-level split, salt missh-reg1 (split_01.sql):
calibration 20% (3,111 patients; all design, tuning and exploration) and
test 80% (11,934; untouched until this signature).

## Definitions (committed rule files)
REFERENCE_RULE.md + amendments A1-A17 (docs/AMENDMENTS.md); ENDPOINT_RULE.md;
D_PRE_NEWS_BRANCHES.md; D_PRE_NEWS_MOVERS.md; D_PRE_NEWS_PROFILE.md;
HYPERACUTE_RULE.md; OMEGA_SCALE_RULE.md; PRIMARY_COMPARISON.md;
CALIBRATION_RULE.md.

## Primary analyses
1. Four branches (D_PRE_NEWS_BRANCHES): distance and coupling change vs the
   tightened-stable 95th line at 2 h before the anchor, 20% bar; tier- and
   clock-matched (PRIMARY_COMPARISON). Scripts: summarize_p1, summarize_p3.
2. Ranking: NEWS alone vs NEWS + frozen alarm (FLAG_FROZEN.json, q 0.95, p 4)
   for deterioration within 2 h and 4 h; AUC and top-10% share with patient
   bootstrap (rank_01).

## Secondary analyses (reported regardless of outcome; no claim rests on them)
P1-P5 fast group (FAST_GROUP_PREDICTIONS.md; fast_80 with FAST_REFS.json);
P6 defending steps and P7 readout kind vs first escalation
(SECONDARY_PREDICTIONS.md; summarize_p3, p7_01); combined model
(A16, COMBINED_FROZEN.json; rank_01); sensitivity-first alarm (A17,
FLAG_SENS_FROZEN.json; rank_01, describe_80).

## Descriptive layer (no tests)
DESCRIPTIVE_TRAJECTORIES.md, all sections: hour-by-hour trajectories by age,
time to deterioration, mover group and direction pattern; per-patient alarm
outcomes; treatment context; state-space path; alarm by hour; bolus-aligned
picture; stable baseline for the gradual-climb pattern; random case atlas
(local only). Script: describe_80.

## What calibration already showed (disclosed, not 80% results)
CALIBRATION_FINDINGS.md and docs/EXPLORATORY.md (E1-E13): no early separation
by distance, path, coupling or combined measures at hourly charting; ~94% of
deteriorating patients compensating; swing toward shock within the final hour;
the one consistent early trace is defending steps (AUC ~0.56-0.57); the
'gradual climb' pattern occurs in 30% of stable 3-h windows; an
asymmetric-sampling artifact was found and fixed (RET_CHECK). Expected 80%
result: main tests null; P6 small positive or null.

## Execution
pipeline/make_sql.sh test test; pipeline/run_sql.sh test; pipeline/export.sh test;
pipeline/run_py.sh test. Same code, verified on calibration (practice suffix
'prac'). Frozen settings are never re-chosen; calibrate_01 and other
setting-choosing scripts are not run on the test split.

## Reproducibility criterion
The practice run reproduced every calibration result, except bootstrap interval
bounds (which depend on the row order of unsorted exports) and one last-digit
rounding (MOVERS 0.510 vs 0.509). Exports are now sorted by patient, so the
test-split run is deterministic. Signing requires identical point estimates
(compare_points.py: numbers within 0.0015, intervals ignored).

## Commitments
- The 80% is run once. Every pre-specified result is reported, null or not.
- Any deviation (a crash, a bug, a missing file) is fixed only if the fix
  changes no definition, is recorded in DEVIATIONS.md with its reason, and the
  original failing output is kept.
- Primary results are stated first and exactly as registered; secondary and
  descriptive results are labelled as such.
- Patient-level outputs (case atlas) stay local unless PhysioNet rules allow.

## Claim sentences, written before the run
If both primary analyses are null: "At hourly charting, reading septic ICU
patients' vital signs as movement in state space did not add to NEWS before
deterioration; the slide was held behind compensation and treatment until about
the final hour."
If a primary analysis succeeds: "Reading hourly vital signs as movement in state
space added to NEWS before deterioration in [branch / ranking], by [effect, CI]."
