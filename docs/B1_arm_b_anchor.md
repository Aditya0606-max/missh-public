# B1 — Arm B Anchor Definition (Class R)
Decided before any d_items lookup. Dictionary results may resolve these
concepts to itemids; they may not add, remove, or redefine them.

## Rule
Arm B is anchored on predefined evidence of cardiogenic cardiovascular support,
not on nonspecific shock treatment.

CORE ANCHORS (any one suffices):
- Inotropic support: dobutamine, milrinone
- Mechanical circulatory support: IABP, Impella, VA-ECMO

CONTEXTUAL (never anchor alone; retained as treatment covariates):
- norepinephrine, epinephrine, vasopressin, dopamine, phenylephrine

Rationale: vasopressors are used across shock states including septic shock
(Arm A). Anchoring on them creates treatment overlap by design and weakens the
F4 sign-inversion claim. Inotropes and MCS are specific to cardiogenic physiology.

## Thresholds
No dose threshold. No duration threshold. Presence of a core anchor establishes
the anchor. Dose and duration are analyzed downstream as variables, never used
to constitute the cohort.

## VA-ECMO specificity
VA-ECMO anchors Arm B. VV-ECMO does not — it is respiratory support and appears
in septic ARDS (Arm A). Only itemids resolvable specifically to VA configuration
qualify. A generic ECMO label does not qualify. If VA/VV cannot be distinguished,
VA-ECMO is reported UNRESOLVED. An unresolved concept is not cured by broadening.

## Resolution rule
For each concept, all matching itemids are retained. Concepts may resolve across
inputevents and procedureevents; both are kept. Absence of a resolvable itemid is
reported as unresolved, never fixed by substitution or expansion.

## OPEN — must close before signature
- Overlap window: how far apart may Arm A and Arm B anchors fall and still be one
  illness episode? No value committed. Free parameter under B2.
- Overlap disposition: intent is exclude-from-primary, retain-for-secondary.
  Primary claim then applies only to physiologically separated arms — this
  limitation to be stated explicitly, not left implicit.
- Reconcile with II.2 tie-break: earliest-qualifying-event still sets t=0 within
  an arm; it does not decide arm assignment. Both rules coexist.

## Overlap window — CLOSED (Class R, decided 2026-08-13)
PRIMARY: 72 hours. Arm A and Arm B anchors falling within 72h of each other are
one illness episode; the patient is classified OVERLAP.

Basis: septic cardiomyopathy characteristically develops within 2-3 days of sepsis
onset (Parker 1984; consistent across subsequent reviews) and resolves in 7-10 days.
A 48h window would admit day-3 septic cardiomyopathy into Arm B as apparently clean
cardiogenic physiology — the contamination the anchor tiers exist to prevent — and
would also lose those patients as identifiable mixed cases. 72h keeps them together.

Cost asymmetry: a wider window over-excludes some genuinely cardiogenic patients,
costing n. A narrower one imports septic physiology into Arm B, corrupting the
comparison. Lost n is recoverable; contaminated arms are not.

SENSITIVITY (pre-declared, reported regardless of result): 48h and 7d.
The 7d bound is the resolution edge of septic cardiomyopathy; anchors further
apart are plausibly sequential illnesses rather than one evolving episode.

DISPOSITION: OVERLAP excluded from the primary A-vs-B F4 comparison; retained for
secondary analysis. The primary claim therefore applies to physiologically
separated arms only. This limitation is stated explicitly in the results, not
left implicit.

SECONDARY ANALYSIS SCOPE: descriptive and cohort-level. Permitted question — does
the OVERLAP cohort's six-vector distribution sit between the arms or cluster with
one? Not permitted — per-patient trajectory or evolution narratives; that is Track B
under per-patient attribution, and Track A's cohort-level narrowing is a constraint
on what the data support, not a presentational choice.

NOTE: VA configuration does not by itself establish cardiogenic etiology — V-VA
ECMO is documented in septic cardiomyopathy. Supports exclusion over assignment
for dual-anchor patients.

CLASSIFIER INVARIANT: arm assignment uses anchor identity and timestamps only.
It may not inspect F4, outcomes, or any downstream trajectory measurement.
