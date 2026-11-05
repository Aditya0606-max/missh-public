# Miss H x VEVFM Track A — Amendments to Pre-Registration v1.0
Reconstructed after loss of WSL environment. v1.1 file did not survive;
this restates the retractions from memory and from the Part 0 packet.
Status: RECONSTRUCTION — verify against chat history before signature.

## A1. Omega gate — coupling-sign condition REMOVED
v1.0 location: Part III.3; Part 0 packet Section 3 (III.3 row) and Section 4 (closing para).
v1.0 text conditioned Gate 3 on coupling sign (septic loosens / cardiogenic tightens),
as control (a) for threat VII.1.
Reason for removal: label leak. The gate is the detection stage; the coupling sign is
the arm discriminator. Conditioning the gate on it makes detection depend on arm
identity, destroying informational independence between gate and six-vector prediction.
Replacement: the Omega gate is sign-blind.
OPEN: does the compensation template survive independently, or is it arm-specific
and therefore the same leak? Decide before B2 closes.

## A2. Onset-rank ordering — WITHDRAWN
No universal per-patient force ordering is predicted.
Primary claim rests on F4 sign inversion at COHORT level.
Basis: synthetic testbed; detrended F4 six-vector dissociates arms at AUC 0.786.

## A3. F2 — MOVED TO TRACK B
Non-estimable at routine charted resolution. Track A runs F1/F3/F4 only.

## A4. Detrending — MANDATORY for F4
Undetrended F4 does not dissociate.

## Consequences for the Part 0 packet
- Section 3, III.3 row: strike coupling-sign condition; resolve template question.
- Section 4, closing para: strike the Omega coupling-sign exemption.
- Section 1, B2: Part III.3 field count and the 41-field total may change.

## A1a. Compensation template — RESOLVED (decided 2026-08-11, not recovered)
The OPEN question in A1 is closed by decision, not by recovery of v1.1 text.
DECISION: no arm-specific compensation template exists in Part III.3.
What remains is an arm-agnostic admissibility criterion: Omega = 1[D(t) > tau],
where D is departure magnitude from the baseline-allowed region and tau is
pre-specified. It asks whether a departure is large enough to be real, not
whether it matches a septic or cardiogenic pattern.
Compensatory SHAPE is evaluated downstream by the six-vector, not at the gate.
Rationale: any template requiring the arm label to fit is the same leak as the
sign condition in different form, and is void under Part 0's no-arm-conditional-
values rule regardless.
Terminology: "compensation template" is retired as misleading. Call it the
admissibility criterion.
Consequence: Part III.3 retains a threshold field (tau) but loses the sign
condition. Confirm the III.3 field count against the B2 table.

## A5. AUC 0.786 reclassified — estimator recovery, NOT physiological evidence
Discovered 2026-08-19 by reading scripts/forcelab2.py make_patient().
The synthetic generator INJECTS the hypothesis: sepsis arm sets decouple=ramp,
tighten=0; cardiogenic arm sets decouple=0, tighten=ramp applied to HR and MAP
via w = w + 0.30*tighten. The predicted coupling directions are therefore
assumptions of the data generator, not findings.
CONSEQUENCE: AUC 0.786 is a Class S result — the estimator recovers an injected
coupling change. It is NOT evidence for the sepsis/cardiogenic direction and
must never be cited as such. The twelve F4 signs cannot be derived from this
testbed without circularity (v1.0 IV.3 already states this: "a simulation
cannot supply them without making the claim circular").
The twelve signs remain Class R, unwritten, and must come from mechanism alone.

## A6. Cadence scope of ADMISSIBILITY_RULE and CADENCE_RULE (decided 2026-10-30)
Both rules (5a73869, 357980c) were written for monitored charting
(oximeter q15, NIBP q30). Measured MIMIC-IV v3.1 cadence (cadence_01.sql,
cadence_02.sql, f3145f1) is one hourly observation set across HR/MAP/RR/SpO2.
At hourly cadence the reference floor (>=12 obs AND >=3 h) is internally
inconsistent: 12 obs requires 12 h.
CONSEQUENCE: both rules are retained unchanged for monitored cadence
(target ward deployment). For the MIMIC-IV confirmatory analysis the
reference is governed by REFERENCE_RULE.md. The >=4 obs per window floor is
retained; F4 windows are therefore 4 h, and F4 is reported as exploratory.
Disclosure: escalation timing (escal_timing.sql) was viewed before this
amendment, as a sample-size consideration only. No measure of architecture
performance was viewed.

## A7. Simulation phi superseded by measured phi (decided 2026-10-30)
All Class S simulations assumed phi = 0.93 per 15-min step (~0.75 per hour).
Measured hourly phi on stable calibration patients (PHI_RESULTS.txt, 6e8b3fb),
16h+ stretch medians: HR ~0.33, SpO2 ~0.15, MAP ~0.11, RR ~0.06.
CONSEQUENCE: simulation numbers (thresholds incl. 6.88, catch rates, lead
times, the 0.69 reference-SD bias) do not transfer to the real data. All
thresholds are set on the calibration split; simulations inform design
direction only.

## A8. Omega — noise floor, old Omega withdrawn, route-specific, floors filled (decided 2026-10-31)
The original Omega (severity veto, third gate of an AND cascade) is
WITHDRAWN. Decided 2026-09-02: Omega is a NOISE FLOOR ("did anything real
happen"), because the AND cascade vetoed the compensating patient whose
coordination worsens while displacement stays small.
Route-specific (decided 2026-10-31): displacement route uses a device floor
built from per-channel charted resolution; coupling route uses the 95th
percentile of the stable |delta rho| null, since estimator sampling variance
dwarfs device noise for correlations.
Per-channel floors: HR 1 bpm, MAP 1 mmHg, RR 1 /min, SpO2 1 % (charted
resolution; lower bound; repeat error unmeasured). Device bias cancels within
patient. Sensitivity grid: 1x, 2x, 3x on all four channels.
Frozen-SD source: blended per REFERENCE_RULE.md (1d5e272) with SD_pop (56dbe50).

## A9. Endpoint tightened; culture-draw anchor dropped (decided 2026-10-31)
Death without escalation counts only for in-hospital, timed deaths within
72 h of ICU admission without prior comfort-measures-only status. Patients
rescued by NIV, high-flow oxygen or RRT form their own group and are
removed from the stable definition. phi and SD_pop are re-run on the
tightened stable group as a check before any outcome-linked measure.
Culture draw (chosen 2026-09-01 as lead-time anchor) is dropped: in a
sepsis-3 cohort it precedes ICU admission by definition. Anchors are now
T_NEWS (primary) and escalation time (secondary). See ENDPOINT_RULE.md (dfb9ed9).

## A10. Stable re-check result (decided 2026-10-31)
Per A9, phi and SD_pop were re-run on the tightened stable group (1,437;
165 rescued by NIV/HFNC/RRT removed), f23fddf. No material change:
phi 16h+ HR 0.329 -> 0.317, MAP 0.106 -> 0.103, RR 0.060 -> 0.059,
SpO2 0.150 -> 0.152; SD_pop within ~1% on all channels.
CONSEQUENCE: REFERENCE_RULE inputs unchanged (1d5e272, 56dbe50).
All stable comparison lines from here on (D_pre-NEWS bar, mover groups,
hyper-acute calibration, coupling null) use the tightened stable group.

## A11. DNI recorded; results reported with and without DNI (decided 2026-10-31)
Code Status (itemids 223758, 228687) charts DNI ("DNR / DNI", "DNI (do not
intubate)", "DNAR ... / DNI"). A DNI patient cannot receive invasive
ventilation, so "no escalation" may reflect a care limit, not physiology.
Outcome labels are unchanged (ENDPOINT_RULE.md). The first DNI time is
recorded per patient (outcome_01.sql, d1c617e), and every outcome-linked
result is reported both for all patients and excluding patients with DNI
charted before their anchor. DNR alone (no CPR) is not used: it does not
block vasopressors or ventilation. Comfort care: value "Comfort measures only".

## A13. Sedation in ruler and pause rule; delayed ruler for tier C (decided 2026-11-02)
Sedation definition as sedation_01.sql (IV propofol, midazolam, lorazepam,
fentanyl, hydromorphone, morphine, dexmedetomidine, ketamine, etomidate;
inputevents start to end + 1 h; emar +2 h); flag per hour in
vitals_01.sql (3ad8009).
1. Ruler: a sedated hour is not clean for building his ruler (centre or
   wobble), the same as a treatment-blocked hour. Reason: a drug-lowered
   HR/MAP would set his normal too low.
2. Watching: sedated hours join the unified pause rule (8e41802). The
   persistence counter holds its value during sedation and resumes from it
   when sedation ends; watching restarts immediately.
3. Delayed ruler: if a channel has fewer clean hours in hours 0-4 than the
   gap tolerance, its ruler is built from the first 5 clean hours by hour 12
   and frozen at the end of the fifth; reported as tier C-delayed. Only if
   that fails is the channel without a ruler. Patient tier C-direction =
   HR or MAP without a ruler after this step.
4. Reported: every result by tier (A, B, C-delayed, C-direction) with counts;
   ruler close hour reported for C-delayed. Assigned from charting,
   treatment and sedation only; no outcome used.
Reason for 3: the direction-only reading was a pre-registered null on the
fast group (HYPER_RESULTS), so it should not be the main reading for
patients who simply lack early clean hours.

## A12. Fast-group secondary predictions recorded (decided 2026-11-02; entered after A13)
FAST_GROUP_PREDICTIONS.md fixes four secondary, descriptive predictions for
the escalated_hyperacute group, derived from calibration exploration
(E1, E3, E3a, E3b, E4) and tested once on the 80% test split: P1 HR-MAP
lock, P2 fewer recovering steps (weak), P3 bend with rate, P4 combined
score added to NEWS for ranking. Time left to MAP 65 and proximity alone
were examined and dropped. The registered architecture, HYPERACUTE_RULE.md
and its pre-registered null are unchanged. Entered after A13 in file order;
committed before any ruler or main-group measurement.

## A14. Treatment split, starting-point rulers, one rule for all (decided 2026-11-02)
Reason: RULER_DIAG (13308a1): 1,338 calibration patients (43%) had no HR/MAP
ruler. Not short stays (1%) nor missing charting (MAP present ~9 of 12 h):
they are the most treated patients (mean 1.1 clean hours of 12). Leaving them
out, or to the direction-only reading (pre-registered null, HYPER_RESULTS),
would test the architecture on the less treated half.
1. Treatment that BLOCKS (not clean for ruler; pauses the counter):
   fluid bolus (unchanged, +2 h); any IV BP/rate drug in inputevents
   (unchanged, +4 h); continuous sedative/opioid infusion (inputevents rows
   >= 60 min: propofol, midazolam, lorazepam, fentanyl, hydromorphone,
   morphine, dexmedetomidine, ketamine), start to end + 1 h.
2. Treatment that is FLAGGED only (counts as clean; reported): oral/hospital
   BP and rate medicines recorded in emar (+4 h); single sedative/opioid doses
   (inputevents rows < 60 min, or emar administrations, +2 h). Assumption
   stated: ICU IV pushes of BP/rate drugs are charted in inputevents.
3. Ruler tiers: A, B, C-delayed as before, using the clean definition above.
   C-origin: no C-delayed ruler, but a clean hour by hour 11; centre = his
   first clean hour (mean of first two if consecutive); width = SD_pop
   (56dbe50), floored; read by distance, path, bend and counter.
   C-sparse: no clean hour by hour 11; origin = his first reading of any kind,
   flagged as treated/sedated; width = SD_pop; reported as net arrow to each
   lookback (length and direction) plus share of unclean or missing hours.
4. Direction-only (HYPERACUTE_RULE) still runs for C-sparse as registered;
   reported as expected null, no claim.
5. Primary analysis: every target patient is watched from his own ruler or
   starting point by one fixed rule, without knowledge of outcome. The first
   table compares the deteriorating and stable cohorts at matched clock hours
   (PRIMARY_COMPARISON.md). Groups by escalation speed, mover size and tier
   are descriptive only. Stable patients use the same tier rules.
6. Disclosure: phi (6e8b3fb) and SD_pop (56dbe50) were estimated under the
   stricter A13 clean definition; retained (a stricter baseline is cleaner).
   Flag shares are reported per tier.

## A14. Treatment split, starting-point rulers, one rule for all (decided 2026-11-02)
Reason: RULER_DIAG (13308a1): 1,338 calibration patients (43%) had no HR/MAP
ruler. Not short stays (1%) nor missing charting (MAP present ~9 of 12 h):
they are the most treated patients (mean 1.1 clean hours of 12). Leaving them
out, or to the direction-only reading (pre-registered null, HYPER_RESULTS),
would test the architecture on the less treated half.
1. Treatment that BLOCKS (not clean for ruler; pauses the counter):
   fluid bolus (unchanged, +2 h); any IV BP/rate drug in inputevents
   (unchanged, +4 h); continuous sedative/opioid infusion (inputevents rows
   >= 60 min: propofol, midazolam, lorazepam, fentanyl, hydromorphone,
   morphine, dexmedetomidine, ketamine), start to end + 1 h.
2. Treatment that is FLAGGED only (counts as clean; reported): oral/hospital
   BP and rate medicines recorded in emar (+4 h); single sedative/opioid doses
   (inputevents rows < 60 min, or emar administrations, +2 h). Assumption
   stated: ICU IV pushes of BP/rate drugs are charted in inputevents.
3. Ruler tiers: A, B, C-delayed as before, using the clean definition above.
   C-origin: no C-delayed ruler, but a clean hour by hour 11; centre = his
   first clean hour (mean of first two if consecutive); width = SD_pop
   (56dbe50), floored; read by distance, path, bend and counter.
   C-sparse: no clean hour by hour 11; origin = his first reading of any kind,
   flagged as treated/sedated; width = SD_pop; reported as net arrow to each
   lookback (length and direction) plus share of unclean or missing hours.
4. Direction-only (HYPERACUTE_RULE) still runs for C-sparse as registered;
   reported as expected null, no claim.
5. Primary analysis: every target patient is watched from his own ruler or
   starting point by one fixed rule, without knowledge of outcome. The first
   table compares the deteriorating and stable cohorts at matched clock hours
   (PRIMARY_COMPARISON.md). Groups by escalation speed, mover size and tier
   are descriptive only. Stable patients use the same tier rules.
6. Disclosure: phi (6e8b3fb) and SD_pop (56dbe50) were estimated under the
   stricter A13 clean definition; retained (a stricter baseline is cleaner).
   Flag shares are reported per tier.

## A16. Combined model frozen as a secondary 80% test; P6 added (decided 2026-11-03)
COMBINED_FROZEN.json (sha256 ffaf8567b819aebbb9869610941da752f17af9052eb2c779ddef1dbcd97f3e83), from freeze_combined.py: models
A (NEWS + hour + tier) and B (A + 15 architecture measures), L2 logistic,
C = 0.5, balanced, fitted on the full 20% at k = 1, 2, 4 h. Preprocessing
frozen with them (stable medians, means, SDs; NEWS median).
On the 80%: apply both unchanged (no refitting); primary k = 2 h; support =
AUC(B) - AUC(A) > 0 with patient-bootstrap 95% CI lower bound > 0.
Disclosure: on calibration B added nothing (E6, COMBINED_RESULTS e6d094a:
gains 0.000, -0.003, -0.004). Tested because the architecture is meant to
run as a whole; a null is expected and will be reported as such.
P6 (SECONDARY_PREDICTIONS.md): heart defending more often before
deterioration; calibration AUC 0.561 at 2 h.
Registered architecture, branches and P1-P5 unchanged.

## A17. Sensitivity-first flag setting as a secondary 80% test (decided 2026-11-03, after CALIBRATION.txt)
Primary flag unchanged (CALIBRATION_RULE: q = 0.95, p = 4). Added after
viewing the calibration grid, as secondary: sensitivity-first setting
q = 0.90, p = 1 (calibration: deteriorating flagged >= 1 h before anchor 13%,
>= 2 h 10%; stable ever-alarmed 55%, 0.19 alarms per patient-day).
Reported on the 80% with: early-flag share, stable alarms per patient-day,
and false alarms per true early flag. Lines L_0.90(h) taken from the same
calibration stable series (series_dw.csv) and frozen in FLAG_SENS_FROZEN.json.
Labelled as chosen after viewing; no claim rests on it.
