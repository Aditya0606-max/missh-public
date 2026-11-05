
## E1. Arrival levels, fast vs stable (2026-11-01, AFTER HYPER_RESULTS)
Exploratory, post-result. Motivated by the fast-group null (hyper_01, 0555cae).
Question: do fast patients differ from stable patients in LEVEL (where they
are) in hours 0-2, rather than in movement? Also: were the 78 readable fast
patients less sick than the 423 unreadable ones?
No rule, threshold or registered analysis is changed by this check.

## E3. Pooled HR-MAP answer, fast vs stable (2026-11-01, AFTER E1)
Exploratory, post-result. Hourly coupling cannot be estimated within one
fast patient (<=3 pairs), so hour-to-hour steps are pooled per group.
Measures: answer rate (MAP fall >=5 mmHg with HR rise >=2 bpm), step
correlation dHR vs dMAP, slope bpm per mmHg, patient-bootstrap 95% CI.
Planned control (E3b): stable patients on beta-blockers should answer less.
No rule, threshold or registered analysis is changed.

## E3a. Sedation check for the E3 HR-MAP lock (2026-11-01, AFTER E3)
Exploratory, post-result. Sedatives/opioids lower HR and MAP together and
could produce the tighter fast-group coupling in E3. Sedated hours: IV
propofol, midazolam, lorazepam, fentanyl, hydromorphone, morphine,
dexmedetomidine, ketamine or etomidate (inputevents: start to end + 1 h;
emar administrations: +2 h). E3 measures recomputed excluding steps that
touch a sedated hour. No rule or registered analysis is changed.

## E3b. Quadrant count of HR-MAP steps (2026-11-01, AFTER E3a)
Exploratory, post-result, last look at the calibration split before the
fast-group hypotheses are written. Steps (not blocked, not sedated) sorted
into: defending (HR up, MAP down), recovering (HR down, MAP up), both down,
both up; |change| < 1 in either channel = flat. Fast steps also split by
hours before escalation (last 2 h vs earlier).

## E4. Bend with rate and time left to MAP 65 (2026-11-02, BEFORE fast-group predictions)
Exploratory on the calibration split, to decide which dots enter the
fast-group predictions tested once on the 80%. Channels scaled by SD_pop
(SD_POP_TIGHT.txt). Clean hours = not treatment-blocked, not sedated.
Bend with rate: three consecutive clean hours; (cos(arrow2,w) - cos(arrow1,w))
x |arrow2|. Time left: MAP above 65 divided by MAP fall per hour (1 arrow:
last step; 2 arrows: mean of last two steps); MAP <= 65 counts as 0; flat or
rising MAP = none. Fast: hours before escalation; stable: hours 0-4.

## E5. P4 and P5 rehearsal on calibration (2026-11-03)
Code and first look for FAST_GROUP_PREDICTIONS P4 and P5 on the 20%.
Recipes unchanged after viewing unless a bug is found (any change recorded).
Reference percentiles = calibration stable steps hours 0-4 (on the 80% the
same calibration reference is used, so the test there is independent).

## E6. Combined architecture vs NEWS, calibration build (2026-11-03)
Question: do the architecture's measures TOGETHER add to NEWS, though none
separates alone (CALIBRATION_FINDINGS)? Model A = NEWS + hour + tier;
Model B = A + 15 measures from parts 1-3 (D_main, Dw_main, D_o, Dw_o,
consistency, straightness, speed, bend, counter, since_ret, block_hrmap,
share_defend, share_recover, share_bothdown, lead_block). Coupling change
excluded (available in ~21% of rows). Missing measures imputed with the
stable median (no missingness indicators, so charting gaps cannot act as a
signal). L2 logistic regression, balanced classes, C = 0.5. 5-fold
cross-validation grouped by patient; AUC of out-of-fold predictions; patient
bootstrap for the B - A difference. Lookbacks 0 (control), 1, 2, 4 h.
If B clearly beats A, its recipe is frozen by amendment before the 80%.

## E7. All-conditions pattern (conjunction), calibration (2026-11-03)
Defined before running. Per patient-hour: C1 Dw_main > stable 95th at that
ICU hour (all tiers pooled); C2 consistency >= 0.75; C3 share_defend >= 0.5;
C4 since_ret >= 3. Full pattern = C1 AND C2 AND C3 AND C4. Reported for
stable (per hour, per patient) and det at 1, 2, 4 h before anchor, overall
and with NEWS < 5. The candidate combined-agreement flag of
PRIMARY_COMPARISON in practical form.

## E8. Effort before the slide: pulse pressure and HR-while-MAP-holds (2026-11-03)
Exploratory, after COSINE_TRAJECTORY showed a jump at the anchor (compensation
hypothesis). Hourly SBP/DBP (vitalsign), pulse pressure = SBP - DBP; arterial
share recorded. Clean = not blocked (A14). Det lookbacks k = 0,1,2,4; stable
all hours (symmetric). Measures: pp_rel, |pp_rel|, dpp4, dhr4, dmap4,
effort = z(dHR_4h) - |z(dMAP_4h)|. Tier- and clock-matched, as parts 1-3.
For registration 2 only; registration 1 unchanged.

## E10. Cosine with real arrows only (2026-11-03, descriptive)
Question: was early direction hidden by short arrows? Cosine = Dw / D, from
the main ruler (D_main, Dw_main) and from origin (D_o, Dw_o), at 2, 4 and 6 h
before the anchor (measures_p1.csv). Only rows whose arrow D > 1 wobble
(primary) or D > 3 wobbles (secondary), in both cohorts. Deteriorating vs
stable of the same tier within +-2 ICU hours (>= 30 stable rows); matched
AUC of cosine, medians, share with cosine > 0.5. Descriptive; no rule changes.

## E11. Ranking rehearsal (2026-11-03)
Dress rehearsal of the headline test on the 20% with frozen pieces only.
Ward = target deteriorating (hours from open to anchor) + target stable
(open to 71). Positive = deteriorating hour with anchor within 2 h (also 4 h);
stable hours negative; other deteriorating hours excluded for that version.
Lists: NEWS; NEWS + 3 x main alarm active (FLAG_FROZEN q=0.95 p=4);
NEWS + 3 x sensitivity alarm active (FLAG_SENS_FROZEN q=0.90 p=1). Alarm
active = decaying counter >= p at that hour (lines frozen per ICU hour).
Metrics: AUC, share of positives in top 10% of patient-hours, gain vs NEWS
with patient bootstrap. Combined model (COMBINED_FROZEN.json) applied
unchanged at k = 1, 2, 4 per A16; in-sample on the 20%, so optimistic.
No settings change after viewing.

## E12. Bolus response and wear-off (2026-11-03, descriptive)
For target deteriorating (bolus before anchor) and target stable patients:
first fluid bolus after ICU admission (>= 500 mL in <= 60 min, items as A14).
MAP before = mean of hours b-2, b-1 (b = bolus start hour). MAP after at the
bolus end hour + 0..6. Lift = max(MAP in end+0..end+2) - before. Wear-off =
first hour after the peak with MAP <= before (within 6 h). Deteriorating:
hours from bolus end to anchor; whether the anchor followed wear-off.
Uses raw hourly MAP and HR including blocked hours. Descriptive; for
registration 2 (support as part of state); no rule changes.

## E12. Bolus response and wear-off (2026-11-03, descriptive)
For target deteriorating (bolus before anchor) and target stable patients:
first fluid bolus after ICU admission (>= 500 mL in <= 60 min, items as A14).
MAP before = mean of hours b-2, b-1 (b = bolus start hour). MAP after at the
bolus end hour + 0..6. Lift = max(MAP in end+0..end+2) - before. Wear-off =
first hour after the peak with MAP <= before (within 6 h). Deteriorating:
hours from bolus end to anchor; whether the anchor followed wear-off.
Uses raw hourly MAP and HR including blocked hours. Descriptive; for
registration 2 (support as part of state); no rule changes.

## E12. Bolus response and wear-off (2026-11-03, descriptive)
For target deteriorating (bolus before anchor) and target stable patients:
first fluid bolus after ICU admission (>= 500 mL in <= 60 min, items as A14).
MAP before = mean of hours b-2, b-1 (b = bolus start hour). MAP after at the
bolus end hour + 0..6. Lift = max(MAP in end+0..end+2) - before. Wear-off =
first hour after the peak with MAP <= before (within 6 h). Deteriorating:
hours from bolus end to anchor; whether the anchor followed wear-off.
Uses raw hourly MAP and HR including blocked hours. Descriptive; for
registration 2 (support as part of state); no rule changes.

## E13. Compensation traces: freedom vs pinned (2026-11-03, descriptive, final panel)
Idea: a stable patient near equilibrium is free (independent hours and
channels); a compensating patient at the same distance is pinned (sticky,
fewer degrees of freedom, RR rising). Window: last 8 h ending at the hour,
>= 6 clean hours (A14). Measures: (1) lag-1 autocorrelation of detrended HR
and MAP, mean = stick; (2) participation ratio of HR, MAP, RR z-steps
(SD_pop), 1-3 = dof; (3) SD of HR and MAP steps; (4) RR slope /h; (5) cosine
of net (RR, MAP) z-travel to (+1, -1); (6) shock index HR/SBP at the hour and
its slope; (7) DBP slope; (8) pinned = D_main <= stable median at that hour
AND stick >= stable q75 AND dof <= stable q25 AND RR slope >= 0.5/h.
Det lookbacks k = 0 (control), 2, 4, 6; stable every hour; tier- and
hour-matched as summarize_p1. Many measures: only patterns consistent across
lookbacks and at the same NEWS are read. Any promising measure is written as
a prediction before signing; otherwise none. Last exploratory panel.

## E15. Settling, matched (2026-11-03, descriptive, after reg1-results)
describe_80.py (line 176) compared deteriorating rows with stable rows at any
ICU hour present at that k, effectively pooled; deteriorating patients mostly
tip early, so the "not settling" gap may reflect time since admission. E15
compares d_hr and d_map with stable rows at the same ICU hour (+-1) and tier
(>= 30 rows): matched stable median, median difference, matched AUC, k = 0-12,
calibration and test. Runs describe_80.py lines 1-170 unchanged in a scratch
copy. Descriptive; tests nothing.

## E16. F1/F3 underneath: urine output and lactate (2026-11-03, descriptive, after reg1-results)
Question: in deteriorating patients whose vitals matched stable patients, were
perfusion (urine output, F1) and energy (lactate, F3) already worse underneath?
Hourly urine output (mL in the hour, and 3 h sum); latest lactate in the past
6 h; lactate drawn this hour (suspicion, reported separately). Each
deteriorating patient-hour vs stable rows at the same ICU hour (+-1) and tier
(>= 30 rows), k = 0-12, all deteriorating and anchor < 8 h, calibration and
test. Matched median difference and matched AUC. Caveats: lactate is drawn on
clinical suspicion; low urine can prompt escalation. Descriptive; tests nothing.

## E18. Ruler at hour 0-1, first ICU hours (2026-11-03, descriptive, after reg1-results)
Origin = mean of each patient's hours 0-1 (HR, MAP, RR, SpO2). At ICU hours 2-6,
before the anchor: HR-MAP cosine and four-channel cosine toward the worsening
direction (HR up, MAP down, RR up, SpO2 down), distance scaled by stable
patients' hour-to-hour SD per channel, and cumulative share of HR-MAP steps
with HR up and MAP down. Deteriorating rows before anchor (k >= 1) vs stable
rows at the same ICU hour (+-1) and tier (>= 30 rows); all deteriorating and
anchor < 8 h; calibration and test; coverage reported. Treatment hours not
removed. Expectation stated in advance: origin arm and hyper-acute profile were
null, so a null is likely. Descriptive; tests nothing.
