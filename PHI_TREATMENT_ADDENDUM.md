# PHI_TREATMENT_ADDENDUM.md — defines "treatment" for PHI_PROTOCOL.md (9ea7371)
# Committed before phi_01.sql is written or run.

## Breaks a stretch
- IV fluid bolus: crystalloid or colloid >= 500 mL given within <= 60 min
  (source: mimiciv_icu.inputevents)
  Blocked from bolus start until 2 h after it ends.
- Any IV vasoactive, antiarrhythmic or antihypertensive infusion or push
  (source: mimiciv_icu.inputevents)
  Blocked from start until 4 h after it ends.
- Beta-blockers and other blood-pressure-lowering drugs given by mouth or IV
  (source: mimiciv_hosp.emar, administered only)
  Blocked from administration until 4 h after.

## Does not break a stretch
- Antibiotics (near-universal in this cohort; no direct hour-to-hour effect on vitals)
- Maintenance IV fluids below the bolus definition
- Supplemental oxygen

## Rule for the stretch
- A stretch is a run of >= 8 consecutive hourly readings per channel
  with no blocked hour inside it.
- A blocked hour ends a stretch; a new stretch can start after the block.

## Not decided here
- Exact itemid lists are fixed in phi_01.sql and committed with it,
  before it is run.
