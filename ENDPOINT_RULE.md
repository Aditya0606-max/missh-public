# ENDPOINT_RULE.md — what counts as Kranthi's outcome
# Committed before any outcome-linked measure is viewed.

## Follow-up window
- 72 h from ICU admission. Events after 72 h reported separately, never
  scored as architecture hits or misses.

## Escalation (unchanged from Oct 4)
- First start of a vasopressor or invasive mechanical ventilation after the
  ruler closes, within the follow-up window

## Death without escalation (counts as an outcome only if all hold)
- In-hospital death with a recorded time (admissions.deathtime), within the
  follow-up window
- No comfort-measures-only code status recorded before death
- Otherwise: reported separately (comfort care / outside window / date-only)

## Rescued by other means (own group)
- Non-invasive ventilation, high-flow nasal oxygen, or renal replacement
  therapy within the follow-up window, without vasopressor or invasive
  ventilation
- Neither escalated nor stable; reported as its own group

## Stable (tightened)
- No vasopressor, no invasive ventilation, alive at discharge, AND none of
  the rescued-by-other-means treatments during the stay
- phi (6e8b3fb) and SD_pop (56dbe50) were measured on the earlier, looser
  stable definition; both are re-run on the tightened group as a check
  BEFORE any outcome-linked measure. If either moves materially, the ruler
  inputs are updated by amendment before measurement.

## Lead-time anchors
- Primary: T_NEWS (D_PRE_NEWS_BRANCHES.md, 49e83e5)
- Secondary: escalation time
- Culture draw dropped: in a sepsis-3 cohort suspected infection
cat >> ~/missh/docs/AMENDMENTS.md << 'EOF'

## A9. Endpoint tightened; culture-draw anchor dropped (decided 2026-10-31)
Death without escalation counts only for in-hospital, timed deaths within
72 h of ICU admission without prior comfort-measures-only status. Patients
rescued by NIV, high-flow oxygen or RRT form their own group and are
removed from the stable definition. phi and SD_pop are re-run on the
tightened stable group as a check before any outcome-linked measure.
Culture draw (chosen 2026-09-01 as lead-time anchor) is dropped: in a
sepsis-3 cohort it precedes ICU admission by definition. Anchors are now
T_NEWS (primary) and escalation time (secondary).
