# Pre-Commitment Worksheet — B1 Arm B Anchor Lookup
Per Part 0 Signature Packet, Section 4. Sections A and B written BEFORE the run.

## A. Before the run — permission
Test name: B1 Arm B anchor itemid resolution (d_items)
Field(s) permitted to set: Arm B anchor itemids ONLY — the integer identifiers
corresponding to concepts already committed in docs/B1_arm_b_anchor.md.
It may not set, revise, or expand the concept list itself.

Provenance: Class R. The clinical definition was reasoned and committed before
any dictionary contact (commit for B1_arm_b_anchor.md precedes this run).
d_items is a dictionary lookup: no patient rows, no subject_id, no outcomes.
The lookup implements an already-decided field; it does not make the decision.

Data touched:
[x] d_items (dictionary, no patient rows)
[ ] Synthetic only
[ ] Demo set
[ ] MIMIC patient records

## B. Before the run — criteria
Concepts to resolve (from committed anchor definition):
CORE   — dobutamine, milrinone, IABP, Impella, VA-ECMO
CONTEXT— norepinephrine, epinephrine, vasopressin, dopamine, phenylephrine
         (covariates, not anchors; resolved for later use)

PASS CONDITION (written now, before any output):
1. Each concept resolves to >=1 itemid in inputevents or procedureevents,
   OR is explicitly reported UNRESOLVED.
2. All matching
2. All matching itemids for a concept are retained. Concepts resolving across
   both tables retain entries from both.
3. VA-ECMO qualifies only if VA configuration is distinguishable from VV from
   the dictionary/procedure definition. A generic ECMO label does NOT qualify.
   If VA/VV cannot be distinguished, VA-ECMO is recorded UNRESOLVED.
4. UNRESOLVED is a legitimate terminal result. It is not cured by broadening
   the concept, substituting a near-match, or relaxing specificity.

FAILURE RESPONSE: an unresolved concept is documented as a gap in anchor
coverage and reported in limitations. It does not trigger redefinition.

STOP CHECK: does the failure response change a Part III or Part V value? NO.

## C. After the run — record
Date and time run:
Result (pass/fail, observed):
Itemids written into the pre-registration:
Unresolved concepts:
Commit SHA of code and worksheet at time of run:

## C. After the run — record  [FILLED 2026-08-17]
Date and time run: 2026-08-17
Query: scripts/b1_anchor_lookup.py + supplementary IABP query.
Source: physionet-data.mimiciv_3_1_icu.d_items (4095 rows). Dictionary only.
No patient rows, no subject_id, no outcomes touched.

RESULT: PASS with one documented gap.

CORE ANCHOR ITEMIDS
  Dobutamine   221653  inputevents      Medications
  Milrinone    221986  inputevents      Medications
  IABP         224272  procedureevents  Access Lines - Invasive
  Impella      228169  procedureevents  Access Lines - Invasive
  VA-ECMO      UNRESOLVED (see below)

CONTEXTUAL (covariates, never anchor alone)
  Norepinephrine 221906 | Epinephrine 221289, 229617 | Vasopressin 222315
  Dopamine 221662 | Phenylephrine 221749, 229630, 229632
  (229631 Phenylephrine _OLD_1 deprecated — EXCLUDED)

VA-ECMO UNRESOLVED — condition 3 fired as written. d_items contains only
229529 ECMO Inflow Line and 229530 ECMO Outflow Line, neither carrying VA/VV
configuration. Generic ECMO does not qualify. Not cured by broadening.
Consequence: Arm B MCS tier rests on IABP and Impella. Stated as a limitation.

IMPELLA — 229781 Bivalirudin (Impella) and 229597 Heparin Sodium (Impella)
EXCLUDED. These are anticoagulants administered to patients on Impella, not
the device. Different concept; retain-all applies within a concept, not across.

IABP — first pass returned UNRESOLVED on search pattern "balloon pump".
Re-queried on "balloon"/"iabp"; 224272 found. This corrected an under-specified
query string, not the concept. 30 further IABP entries exist in chartevents and
datetimeevents (settings, dressing changes, waveforms); all excluded by the
committed inputevents/procedureevents restriction.

Value written into pre-registration: the four resolved core itemids above,
with tables of origin. VA-ECMO recorded as unresolved.
Commit SHA at time of run: (this commit)
