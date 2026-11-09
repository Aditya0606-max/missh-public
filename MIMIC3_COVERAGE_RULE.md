# MIMIC3_COVERAGE_RULE — written before counting (2026-11-06)
Purpose: decide whether the MIMIC-III Waveform Database Matched Subset can test the
Registration 2 hypotheses (straining pump, silent heart, cost not coming back, breathing route).
Stage A (outcome-blind availability): from file headers only, per numerics record:
subject_id, start time, length (h), sampling interval, and which signals exist
(HR, SpO2, RESP, ABP mean/sys/dia = arterial line, NBP = cuff). Same for waveform layout
headers (ABP, PLETH, RESP, ECG at 125 Hz).
Stage B (link): Sepsis-3 ICU stays in MIMIC-III clinical; escalation (first vasopressor or
invasive ventilation) and stable labels defined as in Registration 1; usable = recording
with arterial pressure covering the 6 h before escalation (>= 80% present), or the same
clock hours for stable patients.
Overlap: MIMIC-III and MIMIC-IV years overlap (2008-2012); any analysis treated as a new
test set must state how overlapping patients are handled. Counting only at this stage.

## Stage B definitions (written before running, 2026-11-06)
Cohort: first ICU stay, age >= 18; suspected infection (mimiciii_derived.suspicion_of_infection,
earliest suspected_infection_time) within -24 h to +24 h of ICU intime; first-day SOFA >= 2
(mimiciii_derived.sofa). Close to, not identical with, Registration 1's MIMIC-IV sepsis3 table.
Tip: esc_h = earliest of first vasopressor start (vasopressordurations) and first ventilation
start (ventdurations), hours from intime. Route: pressor / vent / both (within 1 h).
Labels: esc_h < 0 or <= 3 h -> excluded (already on support); 3 < esc_h <= 72 -> escalated;
> 72 -> escalated_after_72h; no escalation and survived -> stable; else other.
Coverage window: escalated with esc_h >= 6: the 6 h before esc_h. Stable: same-length window
before a pseudo-tip drawn (seed 7) from escalated esc_h values within the stay.
Usable = numerics records flagged with ABP spanning >= 80% of the window (record span only;
gaps inside records checked later on a sample). Counting only.

## Deviation M1 (after first coverage run, 2026-11-06)
Record start times mixed formats (with and without fractional seconds); the default parser
silently dropped unreadable starts, undercounting coverage. Fixed by parsing with
format="ISO8601". First-run counts kept on record: escalated usable 43 (any 100, >=80% 66);
stable usable 70 (any 305, >=80% 271).

## Check C8 (written before running, 2026-11-06; descriptive)
Oxygen staircase from ICU admission to tip (Sundar = vent-first, tip >= 6 h) or pseudo-tip (Ajay).
Hourly support level from charted O2 delivery device, O2 flow, and FiO2 (pivoted_fio2),
carried forward until the next entry, max 12 h: 0 room air/none; 1 nasal cannula < 4 L;
2 nasal cannula >= 4 L; 3 face mask / Venti / face tent / trach mask / aerosol, or FiO2 >= 0.40;
4 non-rebreather / high-flow, or FiO2 >= 0.50; 5 BiPAP / CPAP.
Per patient: start level (max of hours 0-2), max level before tip - 1 h, level at tip - 2 h,
climbed (max > start), climb size, hours before tip of first climb.
Groups: Sundar vs Ajay (all) and Ajay on oxygen (any level >= 1). Descriptive: it shows what
happened, not whether a warning could have come earlier (charting follows staff concern).
Next stage: in Sundars with waveform data, whether the HR/RR/SpO2 vector moved while the level climbed.

## Check C8b (written before running, 2026-11-06; descriptive)
Did the HR/RR/SpO2 vector move while the oxygen ladder climbed?
Patients: oxygen Sundars (C8 climbed, max level >= 3, climb >= 4 h after ICU admission) vs
Ajays on oxygen who climbed (aligned on their first climb; random sample up to 200, seed 7).
Numerics from MIMIC-III matched subset, read directly for the needed hours; 15-min block means;
HR 20-250, RR 3-60, SpO2 50-100. Hour 0 = first oxygen step. Ruler = blocks -4 to -2 h
(>= 6 of 8 complete), SD floor 1. Worsening direction (+HR, +RR, -SpO2)/sqrt3.
Read: Dw in hour -1, +1, +3, and (Sundar) 2 h before intubation; heading (slope cosine)
over -2 to 0 and 0 to +2; per-channel z at +3.
Vector-blind prediction, fixed now: Sundar Dw at +3 h and at 2 h before intubation stays
within +/-1 wobble and is not clearly larger than in Ajays who climbed. If Sundar Dw grows
toward worsening more than Ajays, the vector was seeing the slide.

## Check C8c (written before running, 2026-11-06)
Same patients and alignment as C8b (oxygen Sundars who climbed; Ajays on oxygen who climbed,
sample up to 200, seed 7). Two vectors per patient, same ruler (-4 to -2 h before first step):
V1 = HR, RR, SpO2 (worsening +,+,-; SD floor 1,1,1); V2 = HR, RR, S/F (worsening +,+,-;
SD floor 1,1,10). S/F = monitor SpO2 / FiO2 in force: charted FiO2 (carried <= 12 h) else
device estimate (room air 0.21; nasal cannula 0.21 + 0.04 x L/min, 2 L if missing, max 0.45;
mask/Venti/face tent/aerosol/trach 0.40; non-rebreather/high-flow 0.60; BiPAP/CPAP 0.50).
Read: Dw at -1, +1, +3, +5 h and (Sundar) 2 h before intubation; recovery slope of Dw from
+1 to +5 h; AUC (Sundar vs Ajay) of Dw at +3 and +5 h for V1 and V2.
Prediction fixed now: V2 AUC > V1 AUC at +3 and +5 h; Ajay recovery slope <= 0, Sundar's >= 0.
Caution: FiO2 is set by staff; a falling S/F partly reflects their decisions. Descriptive.

## Check C8c (written before running, 2026-11-06)
Same patients and alignment as C8b (oxygen Sundars who climbed; Ajays on oxygen who climbed,
sample up to 200, seed 7). Two vectors per patient, same ruler (-4 to -2 h before first step):
V1 = HR, RR, SpO2 (worsening +,+,-; SD floor 1,1,1); V2 = HR, RR, S/F (worsening +,+,-;
SD floor 1,1,10). S/F = monitor SpO2 / FiO2 in force: charted FiO2 (carried <= 12 h) else
device estimate (room air 0.21; nasal cannula 0.21 + 0.04 x L/min, 2 L if missing, max 0.45;
mask/Venti/face tent/aerosol/trach 0.40; non-rebreather/high-flow 0.60; BiPAP/CPAP 0.50).
Read: Dw at -1, +1, +3, +5 h and (Sundar) 2 h before intubation; recovery slope of Dw from
+1 to +5 h; AUC (Sundar vs Ajay) of Dw at +3 and +5 h for V1 and V2.
Prediction fixed now: V2 AUC > V1 AUC at +3 and +5 h; Ajay recovery slope <= 0, Sundar's >= 0.
Caution: FiO2 is set by staff; a falling S/F partly reflects their decisions. Descriptive.

## Check C8d (written before running, 2026-11-06)
Cost of holding SpO2 flat. Same candidates and alignment as C8b/C8c (first oxygen step = 0 h;
ruler -4 to -2 h). Kept only if SpO2 at +3 h is within +/- 2 points of the ruler mean (held flat).
Blood pressure from ABP numerics (SYS/DIAS/MEAN) when present, else NBP numerics.
Measures (15-min block means): HR; shock index SI = HR/SBP; pulse pressure PP = SBP - DBP;
rate-pressure product RPP = HR x SBP / 1000; MAP.
Read: change from ruler at -1, +1, +3, +5 h and (Sundar) 2 h before intubation; recovery
slope +1 to +5 h for SI and RPP; AUC Sundar vs Ajay of the change at +3 and +5 h.
Prediction fixed now: with SpO2 held, Sundar's SI and RPP rise and do not come back
(slope >= 0), PP narrows; Ajay's SI and RPP ease (slope <= 0). Descriptive; small n expected.

## Check C8d (written before running, 2026-11-06)
Cost of holding SpO2 flat. Same candidates and alignment as C8b/C8c (first oxygen step = 0 h;
ruler -4 to -2 h). Kept only if SpO2 at +3 h is within +/- 2 points of the ruler mean (held flat).
Blood pressure from ABP numerics (SYS/DIAS/MEAN) when present, else NBP numerics.
Measures (15-min block means): HR; shock index SI = HR/SBP; pulse pressure PP = SBP - DBP;
rate-pressure product RPP = HR x SBP / 1000; MAP.
Read: change from ruler at -1, +1, +3, +5 h and (Sundar) 2 h before intubation; recovery
slope +1 to +5 h for SI and RPP; AUC Sundar vs Ajay of the change at +3 and +5 h.
Prediction fixed now: with SpO2 held, Sundar's SI and RPP rise and do not come back
(slope >= 0), PP narrows; Ajay's SI and RPP ease (slope <= 0). Descriptive; small n expected.

## Check C8d (written before running, 2026-11-06)
Cost of holding SpO2 flat. Same candidates and alignment as C8b/C8c (first oxygen step = 0 h;
ruler -4 to -2 h). Kept only if SpO2 at +3 h is within +/- 2 points of the ruler mean (held flat).
Blood pressure from ABP numerics (SYS/DIAS/MEAN) when present, else NBP numerics.
Measures (15-min block means): HR; shock index SI = HR/SBP; pulse pressure PP = SBP - DBP;
rate-pressure product RPP = HR x SBP / 1000; MAP.
Read: change from ruler at -1, +1, +3, +5 h and (Sundar) 2 h before intubation; recovery
slope +1 to +5 h for SI and RPP; AUC Sundar vs Ajay of the change at +3 and +5 h.
Prediction fixed now: with SpO2 held, Sundar's SI and RPP rise and do not come back
(slope >= 0), PP narrows; Ajay's SI and RPP ease (slope <= 0). Descriptive; small n expected.

## Check C11 (written before running, 2026-11-06; descriptive)
What happened to Sundars after intubation. Sundars from missh.m3_c8 (vent first, tip >= 6 h).
Pressor after intubation, by delay from first ventilation: none; <= 1 h; 1-6 h; 6-24 h; > 24 h.
ICD-9 codes for the admission: septic shock 785.52; severe sepsis 995.92; respiratory failure
518.81/518.82/518.84/518.51-518.53; pneumonia 480-486. Hospital death.
Split by C8 max oxygen level before tip: airway Sundar (<= 2) vs oxygen Sundar (>= 4).
Codes are end-of-stay billing codes: what happened, not when.

## Check C12 (written before running, 2026-11-06; descriptive / calibration, not confirmatory)
Core on the shock route with minute and beat data. Window: 6 h before tip (pseudo-tip for Ajays).
Groups: escalated Kranthi (pressor first, tip >= 6 h, ABP numerics >= 80% of window); mixed
(both within 1 h, same coverage); recovered Kranthi = Ajay with ABP >= 80% and shock-like strain in
the first 2 h of the window (median SI >= 0.9 or median MAP <= 70); other Ajays (sample up to 120, seed 7).
Numerics, 5-min blocks: HR, MAP, RR, SpO2, SBP, DBP. Core state (HR, MAP, RR, SpO2); ruler = first
2 h of the window (>= 18 of 24 blocks), SD floor 1; worsening direction (+HR, -MAP, +RR, -SpO2)/2.
Per hour -6..-1: Dw, heading (slope cosine), persistence; SI, PP, RPP; hours SI >= 1 or MAP < 65.
ABP waveform (125 Hz): systolic peaks (min spacing 0.3 s, prominence >= 10 mmHg), beat interval
0.3-2.0 s, |change| < 20% between beats. Per 30 min: RMSSD (ms); pressure reflex (sequence method:
>= 3 beats with SBP and next interval moving the same way, SBP step >= 1 mmHg, interval step
>= 4 ms, r >= 0.8; mean slope, ms/mmHg).
Descriptive expectations: escalated Kranthi shows persistence toward worsening, SI not easing,
RMSSD and reflex lower and falling; recovered Kranthi shows SI easing and Dw returning.
Thresholds learned here go to ARCHITECTURE_V2 only after this is recorded.
M2 result (ABP presence measured from the signal, 6 h before tip):
median share of each hour with valid arterial systolic: Ajay sample 0.97-0.99; escalated Kranthi 0.00;
mixed 0.00 (every hour, including -1 h). Patients with ABP >= 80% of the hour: Ajay ~66%;
escalated Kranthi 16% (-6 h) to 28% (-1 h); mixed 21-26%.
Reading: arterial lines in escalated patients were usually placed at or after the pressor decision;
beat-level pressure during the pre-tip slide is essentially absent (~4-7 Kranthis, ~4-5 mixed).
Ajays with ABP are largely patients with lines already in place (often post-operative), a different
population. Pre-tip pressure must come from cuff (NBP) and charted vitals; heart flexibility (RMSSD)
from ECG R-peaks; the pressure reflex is not measurable before the tip for most escalated patients.
ECG presence (lead II, from waveform segment headers, 6 h before tip): median 100% in all groups;
>= 80% of window: escalated Kranthi 76% (~19/25), mixed 100% (19/19), Ajay sample 82%.
Plan: RMSSD from ECG R-peaks (not ABP) in C12v2; report clean beats per hour; pressure reflex
not measurable before the tip for most escalated patients.

## Check C12v2 (written before running, 2026-11-06; descriptive / calibration)
Replaces C12 after deviation M2. Window 6 h before tip (pseudo-tip for Ajays).
Groups: escalated Kranthi (pressor first, tip >= 6 h, any numerics >= 80% of window); mixed (both);
Ajays with any numerics >= 80% (sample up to 200, seed 7), split into recovered Kranthi (early strain:
first-2-h SI >= 0.9 or MAP <= 70) and other Ajay.
Pressure per hour: arterial if valid >= 50% of the hour, else cuff (distinct NBP readings; median);
source recorded. Core vector: 5-min blocks of HR, RR, SpO2, plus MAP (arterial block mean, or last cuff
value carried <= 60 min) only if MAP present in >= 50% of blocks. Ruler: first 2 h, >= 18 of 24 blocks
with HR, RR, SpO2; SD floor 1. Worsening (+HR, +RR, -SpO2, -MAP).
RMSSD per hour from ECG lead II R-peaks (gqrs), beat intervals 300-2000 ms, |change| < 20%;
hour kept if >= 600 clean beats. Pressure reflex not computed.
Per-patient patterns as in the C12 addendum. A reason is logged for every patient dropped.

## Check C13 (written before running, 2026-11-06; descriptive)
Each patient's journey from ICU admission to tip (pseudo-tip for Ajays), hourly charted vitals
(mimiciii_derived.pivoted_vital). Groups: Kranthi (pressor first, tip >= 5 h), mixed, Sundar, Ajay.
Bad hour: shock side (SI >= 1 or MAP <= 65 or PP <= 30) or breathing side (RR >= 25 or SpO2 <= 92).
Start = hours 0-2; near tip = last 3 hours. Journeys: arrived bad/stayed bad; arrived bad/recovered/
relapsed; arrived bad/recovered; arrived good/slid (first bad >= 3 h before tip); arrived good/sudden;
arrived good/stayed good. Journeys > 72 h reported separately.

## Check C13c (written before running, 2026-11-06; descriptive / calibration)
How early does no-return separate? From c13_hourly.csv (hourly charted). Check times: hours 3, 4, 6 after
arrival, using only hours <= check time; patients included only if tip >= check time + 1 h.
Shock-side comparison: Kranthi vs Ajay, both bad on the shock side in hours 0-2. Breathing-side: Sundar vs
Ajay, both bad on the breathing side in hours 0-2.
Measures at check time: burden (sum of max(SI-1,0) + max(65-MAP,0)/10 per hour; breathing: max(RR-25,0)/5 +
max(92-SpO2,0)/2); bad hours; longest run of good hours; SI and MAP slopes over the last 3 h; time to MAP 65
at current slope (capped 24 h); route balance (shock-side minus breathing-side bad hours).
Report medians and AUC (Kranthi or Sundar vs Ajay) per measure and check time, plus lead time (tip - check).

## Check C13d (written before running, 2026-11-06; calibration)
Same patients, check times (3, 4, 6 h) and look-back rules as C13c.
(1) Per-charted-hour versions: burden and bad hours divided by hours with the side's values charted.
(2) Baselines on the same patients and times: NEWS-lite (NEWS2 points for HR, SBP, RR, SpO2 scale 1, temperature,
    latest value within 2 h of check time; consciousness and supplemental oxygen not available), SI latest,
    SI maximum so far.
(3) Breathing side adds oxygen: ladder level at check time (C8 levels, carried <= 12 h) and number of steps up
    (rise >= 1 level) so far, where C8 oxygen records exist (Sundar / Ajay in m3_c8).
(4) Pre-specified combination: mean of percentile ranks of burden-per-hour and (minus) longest good run.
Report AUC (Kranthi or Sundar vs Ajay) for every measure; the combination is compared with NEWS-lite.

## Check C13e (post hoc, after C13d results; exploratory robustness, 2026-11-06)
Purpose: size and fragility of the C13d shock-side gain over NEWS-lite. Not confirmatory.
(1) Bootstrap (2,000 resamples, Kranthi and Ajay resampled separately) 95% intervals for AUC of the
    no-return combination, NEWS-lite and SI latest, and for the paired difference combination - NEWS-lite, at h3, h4, h6.
(2) At false-alarm rates of 10 / 20 / 30% among arrived-bad Ajays: share of Kranthis flagged by each score,
    Kranthis caught per 100 beyond NEWS-lite, and precision (share of flagged who are Kranthi) in this sample.
(3) Fragility at h4: SI line 0.9 / 1.0 / 1.1 x MAP line 65 / 70; plus persistence as longest run of bad hours.

## Check C13f (written before running, 2026-11-06; calibration)
Can arrival severity separate fast crashers? Naveen = medical emergency (naveen_kind.csv), tip 1-3 h after ICU
arrival. Ajay = stable, survived (c13_groups), arrived bad = any line crossed in first 60 min
(SI >= 1, MAP <= 65, PP <= 30, RR >= 25, SpO2 <= 92). Values: charted vitals (pivoted_vital) in the first 60 min;
for Naveens only values charted >= 30 min before tip. Measures: SI max, MAP min, RR max, SpO2 min, HR max,
shock burden (SI-1)+ + (65-MAP)+/10, breathing burden (RR-25)+/5 + (92-SpO2)+/2, NEWS-lite (HR, SBP, RR, SpO2,
temperature; worst value in window), change of SI and MAP from first to last reading (>= 2 readings).
AUC (Naveen worse vs Ajay arrived bad), with 2,000-resample bootstrap 95% CI for burdens and NEWS-lite;
by route: pressor-first / both on shock measures, vent-first / both on breathing measures.

## Cuff check (written before running, 2026-11-07; descriptive)
Window: 6 h before tip (pseudo-tip for Ajays), stays with tip >= 6 h. Charted BP from chartevents,
error != 1, valuenum > 0, distinct charttimes per source. Cuff: 455, 8441, 456, 220179, 220180, 220181.
Arterial: 51, 8368, 52, 220050, 220051, 220052. Per stay: hours (of 6) with cuff / arterial / either;
cuff readings per hour; cuff rate last 2 h vs first 4 h. Arterial-line patient = arterial in >= 4 of 6 h.
Reported per group, cuff-only patients separately; waveform subset (m3_usable: tip >= 6, cov_any >= 0.8) separately.
FLAG if cuff readings/hour among cuff-only differ from Ajay by >= 25%.
Cuff check results (cuff_check.py; query passed via file after argument-length error; no definition change).
Waveform subset: charted arterial >= 4/6 h: Kranthi 0.18, Ajay 0.15, Sundar 0.15, mixed 0.08.
Cuff-only, cuff in >= 4 of 6 h: Kranthi 1.00 (32), Ajay 0.93 (721), Sundar 0.92, mixed 0.91.
Cuff readings/h: Kranthi 1.58 vs Ajay 1.04 (x1.52, FLAG); first 4 h -> last 2 h: Kranthi 1.38 -> 1.97, Ajay 1.06 -> 1.00.
Decisions for rules: one value per hour (hourly median) for all; cuff frequency never an input;
lead time also reported against the first speed-up in cuff cycling (staff's first worried action).
Note: waveform ABP present in 25/39 Kranthis but charted arterial in only ~7: C12v2 reads waveform.
Full cohort (tip >= 6 h, charted BP): charted arterial Kranthi 0.19, Ajay 0.10, Sundar 0.13, mixed 0.05.
Cuff-only, cuff in >= 4 of 6 h: Kranthi 0.85 (332), Ajay 0.93 (4580), Sundar 0.61, mixed 0.25.
Cuff readings/h: Kranthi 1.31 (x1.27, FLAG), Sundar 0.83, mixed 0.43 (x0.42, FLAG) vs Ajay 1.03;
first 4 h -> last 2 h: Kranthi 1.17 -> 1.60, Ajay 1.04 -> 1.01. Kranthi flag confirmed at scale.

## Check C10 (revised, written before running, 2026-11-07; descriptive / calibration)
Supersedes the unrun C10 script. One value per hour (c13d_hourly.csv, charted, cuff or arterial). Window: last 6 h
before tip (pseudo-tip for Ajays), stays with tip >= 6 h. SI valid if HR 20-250 and SBP 40-260; PP = SBP - DBP.
Unreadable: < 4 of 6 h with SI. Straining pump: SI >= 1 and PP <= 35 in >= 3 h, and SI >= 1 in last charted hour.
Silent heart: MAP slope <= -1 mmHg/h and HR slope <= 0.5 bpm/h (least squares, >= 3 h each). Both -> straining pump (overlap reported).
Timing: first strain hour (SI >= 1 and PP <= 35) vs first cuff speed-up hour (>= 2 cuff readings in an hour, cuff_check_events.csv).
Reported for all stays and for the waveform subset (m3_usable: tip >= 6, cov_any >= 0.8).
Prediction: both shapes more common in Kranthi than in Ajay.

## C10b trajectories (written before running, 2026-11-07; descriptive only)
Same stays and shapes as C10 (c10_shapes.csv). Hours 11..0 before tip (pseudo-tip for Ajays), one value per hour
(c13d_hourly.csv). Per group and hour: median SI, PP, MAP, HR; share with SI >= 1; n with SI.
Groups: Kranthi pump / silent heart / neither; Ajay all; Ajay pump-shaped. No tests.
C10b results (c10b_paths.py; medians, descriptive). 11 h -> last hour before tip:
Ajay all: SI 0.72->0.70, PP 58, MAP 75->75, HR 85->83 (flat).
Kranthi pump (41): SI 1.15->1.39, PP 36->28, MAP 64->55, HR 112->103 (SI>=1 in 72-82% already at 11-10 h).
Ajay pump-shaped (75, not ~50): SI 1.09->1.14, PP 33->29, MAP 78->69 (holds ~68-71), HR ~108 flat.
Kranthi silent heart (121): SI 0.78->0.95, MAP 69->54 (drop in last 2-3 h), HR 81->91->80 (answers then fades).
Kranthi neither (194): MAP 61-64 for all 12 h, SI 0.84-0.90.
Lead: all Kranthi groups sit closer to the edge than Ajay for >= 11 h (headroom), slide only in last 2-3 h.
Pump Kranthi vs pump Ajay separate by direction in last ~4 h (SI climbing, MAP falling, HR fading), not by shape.
Possible explanation of Reg 1 null (distance from own start misses patients who arrive near the edge): hypothesis only.
Cautions: medians only; vs all Ajays (needs arrived-sick Ajays); thin n at 11 h; MIMIC-III already explored.

## C10c fixed lines vs direction (written before running, 2026-11-07; descriptive)
Same stays/shapes as C10; hours 11..0 before tip; one value per hour. Rules per hour:
A: SI >= 1 and MAP <= 65. B: MAP <= 65. C: vs 3 h earlier, MAP fell >= 5 and (SI rose >= 0.1 or HR fell >= 5).
Per group: share firing each hour (of those with the needed values). At 8/4/2 h: Kranthi (all shapes) catch,
Ajay false share, precision = K*catch / (K*catch + A*false) with K, A = stays in each group.

## C10e v2 (written before any C10e run, 2026-11-07; replaces C10e fixed cutoffs, which were not run)
Reason: fixed steps (HR +10, SI +0.15, PP -10, RR +5, MAP -5) treat near-misses as nothing. Witnesses read continuously.
Low-sitting definition unchanged (>= 3 MAP hours in 11-8, median MAP <= 65). Own early SD per channel (hours 11-8),
floors HR 2, MAP 2, RR 1, PP 2, SI 0.02. Signed z toward worsening: HR+, SI+, PP-, RR+. Paying = mean of available z.
Slide = (own low - MAP) / own MAP SD. Combined = mean of within-hour percentile ranks of slide and paying.
Report at 4 and 2 h: AUC Kranthi vs Ajay for MAP level, slide, each witness, paying, combined.
Provisional line = Ajay 90th percentile of combined at each hour (stand-in for budget): catch and precision.
Blind spot: low-sitting Kranthis never above that line in hours 7-0, overall and by shape.
C10e v2 results (c10e2_lowfloor.py). Sitting low early: Kranthi 102/222 (0.46), Ajay 607/2685 (0.23);
low Kranthis by shape: neither 57, silent 30, pump 8, unreadable 7.
Within low group, AUC 4 h / 2 h: MAP level 0.69/0.72 (best); slide 0.64/0.66; SI 0.63/0.64; PP narrowing 0.54/0.61;
HR 0.53/0.52; RR 0.52/0.46; paying 0.58/0.58; combined 0.63/0.66.
Line (Ajay 90th pct): caught 0.26/0.27, precision 0.32/0.32. Blind spot: 0.39 never flagged in hours 7-0
(neither 0.39, silent 0.43, pump 0.25).
Findings: depth still separates below 65 (tolerated low mostly low 60s); HR witness carries no information here
(consistent with Reg 1 80% P6 null); SI and late PP narrowing are the working witnesses; averaging diluted them.
Witness choice not changed here (would be post hoc); to be justified physiologically and frozen before eICU.

## C10f does treatment delay the signal? (written before running, 2026-11-07; descriptive)
Low-sitting group as C10e v2. Split by any bolus (m3_bolus.csv) in hours 6-3 before tip. Within each split:
AUC Kranthi vs Ajay at 4 h and 2 h for slide, z_pp (PP narrowing), z_si, MAP level. Counts per cell reported.
C10f results (c10f_bolus.py). Low-sitting: bolus in hours 6-3 Kranthi 35/102 (0.34), Ajay 78/607 (0.13).
Bolus half (K 34, A ~77): 4 h slide 0.62, PP 0.47, SI 0.63, MAP 0.68; 2 h slide 0.70, PP 0.63, SI 0.65, MAP 0.77.
No-bolus half (K ~64, A ~515): 4 h slide 0.61, PP 0.54, SI 0.59, MAP 0.66; 2 h slide 0.63, PP 0.61, SI 0.64, MAP 0.69.
Reading: PP narrowing late in both halves (natural course); fluids hide PP at 4 h; after bolus fades, Kranthi separates
most strongly (MAP 0.77, slide 0.70). Bolus never an input; bolus RESPONSE (gain holds vs fades) to be read in C12v2.
Small n in bolus half: lead, not result.

## C10d headroom x direction x witness (written before running, 2026-11-07; descriptive)
Same stays/shapes/hours as C10c; one value per hour. C (direction): vs 3 h earlier, MAP fell >= 5 and (SI rose >= 0.1 or HR fell >= 5).
D: (SI >= 0.9 or MAP <= 70) and C. E: (SI >= 1 and MAP <= 65) and HR fell >= 5 vs 3 h earlier. F: A or E (A = SI >= 1 and MAP <= 65).
Same counting as C10c: share firing per hour per group; at 8/4/2 h Kranthi caught, Ajay false, precision at the true mix.

## C12v2 (revised, written before running, 2026-11-07; descriptive / calibration)
Supersedes earlier C12v2 plan. Patients: m3_usable tip_h >= 6, cov_any >= 0.8: Kranthi (escalated, route pressor),
mixed (route both), Ajay (stable; random 300, seed 7). Window: 12 h before tip (pseudo-tip for Ajays), minute numerics.
Validity: HR 20-250, RESP 3-60, SpO2 50-100, MAP 20-200, SBP 40-260, DBP 15-150. NBP carried <= 60 min.
5-min blocks, one value each: arterial if ABPMean valid in >= 3 of 5 min, else cuff; source recorded; never a count.
Patients with HR in < 50% of blocks dropped, reason logged.
At 8, 4, 2 h before tip, over the preceding 3 h of blocks: A_share (blocks with SI >= 1 and MAP <= 65), MAP level, SI level,
MAP slope, SI slope, RR slope (creep), heart answering = corr(dMAP_t, dHR_t+1) (higher = not answering),
slow return = lag-1 autocorrelation of detrended MAP. AUC Kranthi vs Ajay; mixed descriptive.
Bolus fade (whole window, boluses >= 120 min before tip): gain = MAP 30-60 min after - 30 min before;
kept = MAP 90-120 min after - before; fade = gain - kept. Per-patient mean; AUC.
Question: do direction and return readings separate Kranthi from Ajay beyond A_share at 5-min resolution?
ECG RMSSD deferred to a second step.
C12v2 first run (c12v2_extract.py, c12v2_read.py): pressure source 'none' in 82-93% of blocks (Kranthi art 0.06, cuff 0.12),
pressure readings on only 5-7 Kranthis, bolus fade on 3-4. Contradicts m3_usable (cov_abp >= 0.8 in 25/39 Kranthis).
Results NOT interpreted. Suspected cause: signal-name variants not mapped. Diagnosis: c12v2_diag.py.
Dropped for HR < 50% of blocks over 12 h: Ajay 59, Kranthi 4, mixed 3 (12 h window longer than 6 h coverage rule).
C12v2 diagnosis (c12v2_diag.py): signal-name variants ('NBP MEAN', '%SpO2', 'ABP MEAN', 'ART MEAN', with spaces) were
not mapped, so cuff pressure and SpO2 were dropped for many records. Fix: alias map, no definition change; run 1 kept as
c12v2_blocks_run1.csv. CORRECTION: m3_usable cov_abp counts signal presence, not valid values; in 3/3 Kranthis with
cov_abp 1.00 the arterial signal was all zero or empty. "25/39 Kranthis with arterial pressure" is not supported;
these Kranthis were followed mainly by cuff (consistent with charted arterial ~0.18).
C12v2 run 2 (alias fix). Pressure source share of blocks: Kranthi art 0.13, cuff 0.40, none 0.47; Ajay 0.08/0.32/0.60.
Pressure readings on 15-22 of 35 Kranthis vs ~250 Ajays (small n; leads only). AUC 8/4/2 h:
SI level 0.77/0.81/0.78 (best, 8 h out); A_share 0.65/0.71/0.77; MAP low 0.66/0.68/0.69; not answering 0.61/0.61/0.64;
MAP falling 0.57/0.46/0.63; SI rising 0.46/0.52/0.64; RR creep 0.39/0.50/0.55 (n 26-35, no signal);
slow return 0.33/0.42/0.36 (INVALID: carried-forward cuff values fake steadiness); bolus fade AUC 0.56 (K 13, A 25).
Reading: position (SI level) separates early at 5-min as at hourly; no movement/return reading beats A_share.
Pressure dynamics untestable with mostly-cuff pressure (MIMIC-III and eICU); requires arterial data (HiRID).
Next: ECG flexibility (RMSSD), continuous regardless of arterial line.

## C15 heart flexibility from ECG (written before running, 2026-11-07; descriptive / calibration)
Patients: as C12v2 (m3_usable tip_h >= 6, cov_any >= 0.8): Kranthi (pressor), mixed (both), Ajay first 100 of the
C12v2 shuffle (seed 7). Window 12 h before tip (pseudo-tip for Ajays). Lead II, 1 min every 15 min (48 samples).
Quick check first: monitor numerics 'HR Variability' and 'pNN50 Percent' (share non-missing and non-zero).
Beats: gqrs; RR 300-2000 ms; clean if |dRR|/RR < 0.20; sample kept if >= 40 clean intervals; irregular if > 20% rejected (excluded).
Flexibility: RMSSD (ms) and RMSSD / mean RR (%, heart-rate corrected). Hourly per-patient medians.
Q1 rigidity: AUC Kranthi vs Ajay at 8, 4, 2 h (lower flexibility = worse), all and by C10 shape.
Q2 rest or quit: hour pairs where ECG HR fell >= 5 bpm vs 1 h earlier; change in corrected flexibility;
Kranthi (last 4 h) vs Ajay; median change, share rising, AUC (flexibility not rising = worse).
C15 quick check (c15_hrv_numerics.py): monitor 'HR Variability' / 'pNN50 Percent' present in only 15 records (20 K + 20 A checked).
Median HR Variability Ajay 12, Kranthi 18; pNN50 Ajay 0, Kranthi 2 (nonzero 0.28 vs 0.61). Opposite of rigidity hypothesis;
likely includes ectopic/irregular beats (method unknown). Not used as flexibility. ECG step separates clean-beat
flexibility from irregular-rhythm share; irregular share to be reported per group as its own reading.

## C10g silent-heart red signal E' (written before running, 2026-11-07; descriptive)
Same stays/hours/counting as C10d. E': MAP <= 70 and, vs 3 h earlier, MAP fell >= 5 and HR fell >= 5 (no SI requirement).
Reported with A and E for reference: share firing per hour per group; at 8/4/2 h Kranthi caught, Ajay false, precision.
Fixed steps kept for comparability with C10d (continuous version to follow if E' shows signal).

## C10h bolus fade, full cohort (written before running, 2026-11-07; descriptive)
Stays as C10 (tip >= 6 h): Kranthi (all shapes) vs Ajay. Boluses (m3_bolus.csv) >= 3 h before tip (pseudo-tip) and >= 1 h
after ICU arrival. Hourly charted MAP: before = hour before bolus hour; after1 = hour after; after2 = 2 h after.
gain = after1 - before; fallback = after1 - after2 (positive = MAP slipped back). Per-patient means; AUC Kranthi vs Ajay
for fallback and for gain; by C10 shape; n reported.

## C10g silent-heart red signal E' (written before running, 2026-11-07; descriptive)
Same stays/hours/counting as C10d. E': MAP <= 70 and, vs 3 h earlier, MAP fell >= 5 and HR fell >= 5 (no SI requirement).
Reported with A and E for reference: share firing per hour per group; at 8/4/2 h Kranthi caught, Ajay false, precision.
Fixed steps kept for comparability with C10d (continuous version to follow if E' shows signal).

## C10h bolus fade, full cohort (written before running, 2026-11-07; descriptive)
Stays as C10 (tip >= 6 h): Kranthi (all shapes) vs Ajay. Boluses (m3_bolus.csv) >= 3 h before tip (pseudo-tip) and >= 1 h
after ICU arrival. Hourly charted MAP: before = hour before bolus hour; after1 = hour after; after2 = 2 h after.
gain = after1 - before; fallback = after1 - after2 (positive = MAP slipped back). Per-patient means; AUC Kranthi vs Ajay
for fallback and for gain; by C10 shape; n reported.

## C10i position on the road between recovery and shock (written before running, 2026-11-07; descriptive)
Anchors from MIMIC-III (to be frozen for eICU): recovery = Ajay median over hours 11-0; shock = Kranthi median at hour 0.
Channels MAP, SI, PP, HR, RR, SpO2. Per channel f = (x - recovery) / (shock - recovery), clipped -0.5..1.5.
Weight = |shock - recovery| / Ajay SD. Road = weighted mean of available f. Witnesses = channels with weight >= 0.2 and f >= 0.5.
Report anchors and weights; median road per hour by Kranthi shape and Ajay; AUC at 8/4/2 h vs all Ajays and vs low-sitting
Ajays (median MAP <= 65 in hours 11-8), with rule A for comparison. Caution: shock anchor from same Kranthis (circular here).
C10i results. Anchors: MAP 75->57 (w 1.14), SI 0.71->0.96 (1.23), PP 58->43 (0.78), HR 84->88 (0.22), RR 19->20 (0.18), SpO2 97->97 (0).
Median road (11 h / 5 h / 0 h): Ajay 0.13/0.12/0.11; pump 1.02/1.13/1.27; neither 0.58/0.58/0.78; silent 0.45/0.43/0.95.
AUC 8/4/2 h: road vs all Ajays 0.70/0.76/0.77; vs low-sitting Ajays 0.54/0.67/0.70 (neither 0.53/0.65/0.66,
silent 0.48/0.62/0.68, pump 0.80/0.92/0.94); witnesses 0.66/0.72/0.71; rule A (binary) 0.55/0.61/0.65.
Reading: neither and silent heart overlap low-sitting Ajays until late; road ~ equal to best single continuous channel
(SI level, MAP depth), not clearly better. Binary vs continuous comparison with A is not fair. Shock anchor circular here.
Next: road vs SI alone, MAP alone, PP alone, NEWS-lite on same rows.

## C10k position + bandwidth + coordinated return (written before running, 2026-11-07; descriptive)
Low-sitting group only (C10i lowA: median MAP <= 65 in hours 11-8), Kranthi vs Ajay. Window: 3 h (hb c..c+2) for c = 8, 4, 2.
Position = mean road (C10i). Bandwidth per channel = (max - min of charted values) / Ajay SD, >= 2 readings; channels MAP, SI, PP, RR.
bw_rr_pp = bw_rr x bw_pp; bw_press = geometric mean of bw_map, bw_si, bw_pp.
Coordinated return = hour steps with road falling >= 0.05 and >= 2 of MAP/SI/PP fractions falling.
Combined = mean percentile rank of road, narrow bw_press, and no return. AUC Kranthi vs Ajay (low-sitting) per reading and by shape.
2x2: near edge (road >= 0.5) x narrow (bw_press <= Ajay median at that hour), shares per group.

## C10l fair comparison: road vs single numbers (written before running, 2026-11-07; descriptive)
Same rows, anchors and road as C10i. Readings: road, SI, MAP (lower worse), PP (lower worse), NEWS-lite (HR, SBP, RR, SpO2, temp;
>= 3 present), rule A. Versions: single hour, and 3-h mean (hb c..c+2). AUC at c = 8/4/2 h: all Kranthis vs all Ajays and vs
low-sitting Ajays (C10i lowA). Decision: road adds only if it beats the best single number by >= 0.02 at all three times vs
low-sitting Ajays (3-h versions); otherwise the alarm uses the simpler number and the road is descriptive.

## C14 real-alarm replay, pressure route (written before running, 2026-11-07; calibration)
All c13 stays; hourly c13d_hourly from hour 0 to min(tip, 72 h). Anchors as C10i (recovery = Ajay median hb 0-11; shock = Kranthi
median hb 0) for MAP, SI, PP; fractions clipped -0.5..1.5. Channel line = Ajay 90th percentile of its fraction (all Ajay hours).
Amber = any channel past its line. Red = (agreement: any past line and all three >= 0.5, two consecutive hours) OR (depleted: >= 2
channels >= 0.5 for 4 consecutive hours and HR fell >= 5 vs 3 h earlier). Comparators: NEWS-lite >= 5; rule A.
Worried action: first bolus after arrival (m3_bolus). Report per group: share alarmed before tip, median lead (h), episodes per
patient-day; Kranthi: red before NEWS-lite and before first bolus. Ajay: red/amber episodes per day by furthest 3-h road band.
Sundar descriptive (no breathing road yet). Lines set on same Ajays: calibration only.

## C14b matched-budget comparison (written before running, 2026-11-07; calibration)
Same stays/hours/anchors as C14. Scores per hour: road (mean MAP/SI/PP fraction), road 3-h mean, SI, MAP (lower worse),
NEWS-lite, NEWS-lite 3-h mean. Alarm = score >= line; episode = rising edge (re-arm when below). For budgets 0.2, 0.44, 1.0, 1.97
episodes per Ajay-day: line = lowest candidate (Ajay quantiles 50-99.99%) with Ajay episodes/day <= budget; actual cost reported.
Report per score x budget: Kranthi warned before tip, median lead (h), warned before first bolus; Sundar warned.
Architecture contributes if, at equal cost, road warns more Kranthis or earlier than NEWS-lite and SI.

## C14c ward simulation (written before running, 2026-11-07; calibration, descriptive)
Naveen = naveen_kind rows marked medical (true fast crashers), tip (first pressor or ventilator, m3_cohort) 1-3 h after arrival;
hourly vitals from mimiciii_derived.pivoted_vital (hourly mean), hours before tip. Ajay/Kranthi as C14 (Ajay present to pseudo-tip).
Same anchors/fractions as C14; road = mean MAP/SI/PP fraction; scores road 3-h mean and NEWS-lite 3-h mean, carried forward.
Ward: all admitted hour 0, horizon 48 h; each hour rank patients present; top 5% (at least 1) = red. 200 random wards per mix:
30 Ajay / 30 Kranthi / 30 Naveen, and real mix (pool proportions scaled to 100). Report: Kranthi and Naveen reaching red before
tip, median lead; share of red slots by group; Ajay red episodes per Ajay-day. Road vs NEWS-lite.

## C14d road OR NEWS-lite at matched budget (written before running, 2026-11-07; calibration)
Same hourly table as C14b (road 3-h mean, NEWS-lite 3-h mean). Alarm = road3 >= tr OR news3 >= tn; episode = rising edge.
Budgets 0.2, 0.44, 1.0, 1.97 Ajay episodes/day. (1) Split budget (primary): tr, tn each the lowest line costing <= b/2 alone.
(2) Best pair (optimistic, tuned on these Kranthis): grid over both lines maximising Kranthis warned at cost <= b.
Report: Kranthi warned, median lead, before first bolus, Sundar warned, which part fired first; plus road3 alone and news3 alone.
Combination contributes if split-budget OR warns more Kranthis than both alone at equal cost, with lead >= the better single.

## C14f timeline: road vs clinical NEWS lines (written before running, 2026-11-07; descriptive)
Same hourly table as C14b. Road amber = road3 at line costing <= 1.0 Ajay episodes/day. NEWS-lite (single hour) >= 5 and >= 7.
Per Kranthi: first hour of each, tip. Report: lead (median, IQR); road-to-NEWS5 and road-to-NEWS7 gaps; NEWS5/NEWS7 to tip;
road only / NEWS5 only / both / neither; road3 position when NEWS5 first fires; Ajay episodes/day for each alarm.

## C14g sudden slip and all-stay fast track (written before running, 2026-11-08; calibration)
Same hourly table as C14b/C14f. Road amber = road3 at line costing <= 1.0 Ajay episodes/day. Kranthi classes by first amber:
early (>= 2 h before tip), late (< 2 h), never; late + never = sudden slippers; crossed with NEWS-lite >= 5.
Last 3 h before tip: max one-hour road jump, max one-hour MAP drop, max one-hour SI rise; slippers vs early.
Fast track (all stay): one-hour road jump >= J and road >= 0.5; J = smallest with Ajay firing hours <= 0.2 per Ajay-day.
Report: slippers caught by fast track before tip (lead); all Kranthis; amber OR fast track: Kranthis warned and total Ajay cost.
C14g follow-up (SI by slip class). 3 h before pressor: caught early median 0.99 (>= 1: 0.49); slippers 0.62 (0.00).
Last hour: caught early 1.01 (0.54); slippers 0.77 (0.28). Slippers within range (below typical Ajay 0.71) 3 h out,
then SI rises ~0.15 and a quarter cross 1 only in the last hour. Fast track excluded them (required road >= 0.5).
Idea (not adopted): rise-from-low rule (e.g. SI +0.15 within 3 h from below 0.8), must be priced on Ajays (C14g2) before use.
C14g2 AMENDED before running (2026-11-08): MAP-drop witness misses strained hearts that hold MAP by vasoconstriction while
pulse pressure narrows. Witness variants, each priced separately at Ajay <= 0.2 firing hours/day: (a) MAP drop >= 5 vs 3-h high;
(b) PP narrowing >= 5 vs 3-h high; (c) either (PRIMARY, pre-specified). All other C14g2 terms unchanged.

## C14h Naveen vs sudden slippers; Naveen fast track (written before running, 2026-11-08; calibration)
Naveen as C14c (medical emergency, tip 1-3 h, hourly vitals). Road and anchors as C14. Jump = one-hour change in road.
(1) Naveen first-reading road and max jump before tip vs C14g slippers / early-caught (c14g_kranthi.csv).
(2) Jump rule: jump >= J and road >= 0.5, J = smallest with Ajay firing hours <= 0.2 per Ajay-day; Naveens caught, lead.
(3) Arrival rule: max road in first 3 h >= La, La = Ajay 90th percentile of that maximum (flags 10% of arriving Ajays);
Naveens caught before tip, lead; Kranthis flagged at arrival. (4) Arrival OR jump for Naveen.
C14i/C14j AMENDED before running (2026-11-08): include Sundar and mixed. C14i event = any escalation within 3 h
(Kranthi pressor, Sundar ventilator, mixed both), reported by route; quiet hours from all four groups. C14j catch reported for
Kranthi, Sundar, mixed. Purpose: measure the pressure road's blind spot for breathing-route and atypical escalations.
C14i results (all routes). Escalations within 3 h per 1,000 quiet hours: road 29.8 (93,634 h); NEWS-lite<5 20.2; both 17.6.
Road-quiet escalations by route: Sundar 0.76, Kranthi 0.14, mixed 0.10. Quiet-on-both: Sundar 0.70, Kranthi 0.19, mixed 0.11.
By time since last amber: 0-2 h 38.7; 3-5 h 38.0; 6-11 h 39.1; 12+ h 33.0; never amber 26.8.
Reading: pressure-road quiet is breached mostly via breathing route; recently-amber quiet ~40% riskier than never-amber.
C14j results (climb >= 0.50 over 3 rising hours, below amber; Ajay 0.20 h/day): Kranthi 0.09 (lead 9.8 h), amber OR climb 0.86 vs 0.83;
Sundar 0.15 (17.5 h), OR 0.51 vs 0.44; mixed 0.09 (21 h), OR 0.41 vs 0.37. Kranthi climb before amber 0.44 (median 2.5 h earlier);
slippers 16/114. Long Sundar/mixed leads likely non-specific. Breathing road = top priority; 'recently amber' state proposed.

## C14h2 arrival curve for Naveen (written before running, 2026-11-08; descriptive)
Same data as C14h. Arrival score = max road over readings in hours 0-2 (Naveen: only before tip). Lines 0.2..1.2 step 0.1:
Naveens caught by route (before tip; lead), arriving Ajays flagged (share), arriving Kranthis flagged. NEWS-lite max in same
window >= 5 and >= 7 for comparison. Share of Naveens with no reading before tip. Red rule noted as structurally unable to fire
within 3 h (requires 2-4 h); Naveen needs own arrival budget.

## C14h3 does he come back after an arrival flag (written before running, 2026-11-08; descriptive)
Same data as C14h. Arrival flag = road >= 0.6 at a reading in hours 0-2 (Naveen: before tip). Next reading = road one hour later.
Came back = next road <= flagged road - 0.1. Report share coming back for Ajay, Kranthi, Naveen by route. Two-reading red =
flagged and next reading not came back; Naveens caught before tip (lead), Naveens tipping before a next reading, Ajays flagged.
C14h3 results (arrival flag road >= 0.6 in hours 0-2). Flagged / had next reading / came back:
Ajay 1507 (0.30 of Ajays) / 0.96 / 0.56; Kranthi 248 / 0.98 / 0.40; Naveen pressor-first 363 / 0.40 / 0.51;
both 134 / 0.17 / 0.43; vent-first 225 / 0.20 / 0.48. Two-reading red: Naveens caught 0.05 (107/2266), lead 0.5 h;
509 flagged Naveens tipped before a next reading; Ajays with two-reading red 0.13. 805 Ajays flagged then came back.
Reading: hourly data cannot test 'coming back' for Naveen (most tip before a second reading); came-back rates similar
Naveen vs Ajay among those with a next reading; Kranthi comes back less (0.40 vs 0.56). Naveen needs within-hour data (eICU 5-min, ED).
C14h3 results (arrival flag road >= 0.6 in hours 0-2). Flagged / had next reading / came back:
Ajay 1507 (0.30 of Ajays) / 0.96 / 0.56; Kranthi 248 / 0.98 / 0.40; Naveen pressor-first 363 / 0.40 / 0.51;
both 134 / 0.17 / 0.43; vent-first 225 / 0.20 / 0.48. Two-reading red: Naveens caught 0.05 (107/2266), lead 0.5 h;
509 flagged Naveens tipped before a next reading; Ajays with two-reading red 0.13. 805 Ajays flagged then came back.
Reading: hourly data cannot test 'coming back' for Naveen (most tip before a second reading); came-back rates similar
Naveen vs Ajay among those with a next reading; Kranthi comes back less (0.40 vs 0.56). Naveen needs within-hour data (eICU 5-min, ED).

## C16 breathing road (written before running, 2026-11-08; calibration)
Hourly table as C14b, all groups. FiO2 per hour: charted FiO2 (fraction; /100 if > 1) overrides; else from last device + flow:
room air/none 0.21; nasal cannula 0.21 + 0.04 x L/min (2 if missing), max 0.44; simple/venturi/face tent/trach/aerosol mask 0.40;
non-rebreather 0.85; high-flow nasal 0.60; BiPAP/CPAP/NIV 0.50; ETT/ventilator -> missing. Carried forward <= 12 h. Bedside estimates.
S/F = SpO2 / FiO2; ROX = S/F / RR; NEWS with O2 = NEWS-lite + 2 if FiO2 > 0.21.
Breathing road: channels S/F (lower worse), RR (higher worse), FiO2 (higher worse); recovery = Ajay median hb 0-11; failure end =
Sundar median hb 0; fractions clipped -0.5..1.5; mean of available; 3-h mean. Matched budgets 0.44 and 1.0 Ajay episodes/day:
breathing road, pressure road, NEWS-lite, NEWS with O2, ROX (lower worse), S/F (lower worse). Report Sundar, Kranthi, mixed warned
and lead; share of hours with charted vs estimated FiO2. Comparators fixed in advance: NEWS with O2 and ROX.
C16 results. FiO2 source (charted/estimated/none): Ajay 0.14/0.56/0.30; Sundar 0.31/0.48/0.21; Kranthi 0.15/0.59/0.26; mixed 0.15/0.51/0.33.
Sundar warned (lead) at budget 0.44 / 1.0: S/F 0.57 (9.2 h) / 0.72 (13.6 h); breathing road 0.36 / 0.71; ROX 0.44 / 0.62;
pressure road 0.21 / 0.44; NEWS-lite 0.27 (cost 0.26) / 0.43 (cost 0.63); NEWS with O2 0.26 (0.23) / 0.40 (0.54).
Kranthi at 1.0: pressure road 0.83, S/F 0.58, breathing road 0.51. Mixed breathing-road lead 0.7-0.9 h (likely pre-intubation O2).
Reading: S/F alone strongest for Sundar; breathing road adds nothing over S/F; S/F > ROX at both budgets; NEWS not cost-matched
(integer steps). Pressure road (Kranthi) and S/F (Sundar) complementary: run both on all patients.
CAUTION: FiO2 reflects clinician oxygen escalation (treatment decision, path to ventilator). Pending: RR+SpO2-only check without
FiO2; S/F lead vs first oxygen step-up.

## C16b oxygen step-up, no-FiO2 reading, both readings (written before running, 2026-11-08; calibration)
From c16_hourly.csv. (1) First oxygen step-up = first hour with FiO2 > previous hour's FiO2 + 0.02 (both known). For Sundars warned
by S/F (budgets 0.44, 1.0): share warned before first step-up (or never stepped up), median gap. (2) No-FiO2 reading: road from
RR (higher worse) and SpO2 (lower worse), anchors Ajay median hb 0-11 and Sundar median hb 0, 3-h mean; also RR alone, SpO2 alone;
matched budgets vs S/F; Sundar, Kranthi, mixed warned. (3) Pressure road3 and S/F each at half the budget, OR: warned by group,
share with no alarm before tip (sneaked through).

## C16d leading channel vs averaged road (written before running, 2026-11-08; calibration)
Hourly table as C14b with per-channel fractions (MAP, SI, PP) from C14. Scores: road 3-h (current), road 1-h, leading channel
(max fraction) 1-h and 3-h mean, PP fraction alone, any channel past its own line (common Ajay percentile per channel, chosen so
OR cost meets budget). Budgets 0.44 and 1.0 Ajay episodes/day. Report Kranthi caught (lead), C14g sudden slippers caught,
Sundar caught. If leading-channel readings catch more slippers at equal cost, they join the alarm before C16c.
C16d results. Budget 1.0: road3 Kranthi 0.83 (8.8 h), slippers 33/114, Sundar 0.44; road 1-h 0.77, 36/114, 0.32;
leading channel 3-h 0.85 (8.3 h), slippers 60/114, Sundar 0.43. Budget 0.44: road3 0.62, 16/114; road 1-h 0.59, 22/114;
leading 3-h 0.61, 36/114. Leading 1-h, PP alone, any-channel-own-line could not meet budget: fractions capped at 1.5 and many
Ajay hours at cap (narrow PP common in Ajays). Caution: slippers defined as road3 misses, so gain inflated; net Kranthi gain
+2 points (~9/470). Design: pressure reading = leading channel, 3-h mean (replaces road3) for C16c.

## C16c whole-ward alarm vs NEWS at matched cost (written before running, 2026-11-08; calibration)
Pressure reading = leading channel 3-h mean (C16d); breathing reading = S/F (C16). Alarm = either crosses its line.
Splits 0.2..0.8 of budget to pressure; both budgets scaled up together until OR cost reaches 1.0 Ajay episodes/day.
Best split = most Kranthi + Sundar + mixed warned in total; frozen for eICU. Comparators at cost <= 1.0: NEWS-lite 3-h mean,
NEWS with O2 3-h mean; also each reading alone. Report warned by group, lead, sneaked through, total.
Claim if best split warns more in total than both NEWS versions, and not fewer Kranthis than NEWS.
C16c results (cost ~1.0). Kranthi / Sundar / mixed / TOTAL: shared 0.4/0.6 0.76 / 0.70 / 0.46 / 1502;
NEWS-lite 3-h 0.73 / 0.59 / 0.31 / 1263; NEWS with O2 3-h 0.69 / 0.57 / 0.31 / 1216 (cost 0.89);
pressure alone 0.85 / 0.43 / 0.34 / 1141; S/F alone 0.58 / 0.72 / 0.45 / 1434. Splits 0.4-0.6 plateau (1481-1502).
Leads: shared Kranthi 8.3 h, Sundar 12.2 h; NEWS-lite 9.0 h, 15.4 h. Mixed sneaked through 0.54.
DECISION (pre-specified): claim MET (total > both NEWS; Kranthi not fewer). Freeze split 0.4/0.6; lines lead3 1.5 (= fraction cap),
S/F 247.5. Cautions: in-sample; FiO2 mostly estimated; NEWS-lite lacks consciousness; NEWS slightly earlier on those it catches.

## C16e ward pace replay of the frozen setup (written before running, 2026-11-08; calibration)
Same patients/values as C16c. Ward pace: one observation every 4 h per patient (random start offset 0-3 h, seed 7); between
observations last values carried forward (<= 3 h). Readings recomputed from thinned values: leading channel 3-h mean; S/F; NEWS-lite
3-h mean; NEWS-lite >= 5. (a) Frozen lines (lead3 1.5, S/F 247.5): cost and warned by group. (b) Same setup re-matched to cost 1.0
at ward pace (split 0.4/0.6, topped up). (c) NEWS-lite 3-h at cost <= 1.0; NEWS-lite >= 5 clinical. Report Kranthi, Sundar,
mixed warned, lead, total.

## C17 full ward test (written before running, 2026-11-08; calibration, descriptive)
Patients: Ajay, Kranthi, Sundar, mixed (C16e table) and Naveen (C14c: medical emergency, tip 1-3 h; pressure only, no FiO2).
Amber: ICU lead3 >= 1.5 or S/F <= 247.5; ward pace (4-hourly, C16e) lead3 >= 1.42 or S/F <= 287.9. Arrival watch: road >= 0.6
in hours 0-2. Ward: 20 beds, 720 h, beds refilled on discharge/tip from the real mix (pool proportions), 100 runs, seed 7.
Report per character: caught before tip (amber or arrival), lead, sneaked through; per 12-h shift: amber episodes, share on patients
who later tip, arrival flags; Ajay amber episodes per Ajay-day. Both paces.
C17 results (20 beds, 720 h, 100 runs). Admission mix: Ajay 0.52, Naveen 0.24, Sundar 0.13, mixed 0.06, Kranthi 0.05.
ICU pace: amber 11.5/shift (90th pct 16), 0.47 on patients who later tipped; arrival flags 5.0/shift; Ajay 1.01/day.
  Caught (lead): Kranthi 0.83 (8.9 h), Sundar 0.73 (12.7 h), mixed 0.48 (9.0 h), Naveen 0.35 (0.7 h).
Ward pace: amber 9.8/shift (90th pct 13), 0.38 real; arrival 2.0/shift; Ajay 1.00/day.
  Caught: Kranthi 0.80 (8.2 h), Sundar 0.70 (15.1 h), mixed 0.42 (12.7 h), Naveen 0.12 (0.7 h).
Reading: ~1 amber/hour per 20 beds, about half real; Kranthi and Sundar well covered at both paces; Naveen the main gap
(short stay; ward obs often after crash; no FiO2 in Naveen data). Mixed ~half.

## C18 red level with fast path (written before running, 2026-11-08; calibration)
ICU pace, C16e table. Amber as frozen (lead3 >= 1.5 or S/F <= 247.5). Slow red: amber held D consecutive hours (D smallest with
Ajay red episodes <= 0.2/day); variants (i) dwell only, (ii) dwell + not easing (lead3 >= its value 3 h earlier or S/F <= its value
3 h earlier). Fast red: one-hour leading-channel jump >= Jp with lead1 >= 1.0, or one-hour S/F drop >= Js with S/F <= 300; Jp and Js
each priced at <= 0.05 Ajay episodes/day. Red = slow (ii) or fast. Comparators: NEWS-lite >= 7; NEWS-lite 3-h at red's cost.
Report Kranthi, Sundar, mixed, Naveen (pressure fast red only) reaching red before tip, lead, hours from first amber to red.

## C20 guardian lines (written before running, 2026-11-08; descriptive)
Per channel 3-h rolling mean (min_periods 1): MAP (low worse), SI (high worse), S/F (low worse). Each patient's worst 3-h value
over the stay (before tip for deteriorating). Guardian = Ajay 1st (low-worse) or 99th (high-worse) percentile of that worst value
(1% of Ajays ever reach it). Report guardian values; per group share crossing before tip and median hours from first crossing
to tip; any-guardian. Naveen: MAP and SI only (C14c data).

## C16f own 3-hour lines per pressure channel (written before running, 2026-11-08; calibration)
Same table as C16c. Each pressure channel fraction (MAP, SI, PP) as 3-h mean; own lines = common Ajay percentile q per channel,
q chosen so any-channel OR meets budget. Compared with leading channel 3-h (line 1.5) and MAP 3-h alone at budgets 0.4 and 1.0.
Shared setup with S/F (split 0.4/0.6, topped up to 1.0): own lines vs C16c total 1502. Report Kranthi all, silent heart (C10),
low-SI Kranthi (mean SI < 0.8 in last 6 h), C14g slippers, Sundar, mixed, total; lines translated to raw values.
C16f results (pressure alone). Budget 1.0: leading 3-h Kranthi 0.85, silent heart 0.90, low-SI 0.69, slippers 0.53, total 1141;
own 3-h lines (MAP <= 57.7, SI >= 1.04, PP <= 38.0) 0.83 / 0.85 / 0.68 / 0.50, total 1116; MAP alone 3-h 0.79 / 0.83 / 0.69 / 0.44.
Budget 0.4: leading 3-h and own lines cannot fit (Ajay hours at cap); MAP alone 0.55 / 0.60 / 0.50 / 0.27.
Shared own-lines setup not built (own lines infeasible at 0.4 share). Reading: own lines do not beat leading channel; leading
channel already catches 90% of silent hearts (via PP); ~31% of low-SI Kranthis missed by all versions (not a MAP-line problem).
DECISION: keep leading channel 3-h in frozen setup.

## C18b red by agreement (written before running, 2026-11-08; calibration)
Amber frozen (lead3 >= 1.5 or S/F <= 247.5; Naveen pressure only). Red = amber AND NEWS-lite 3-h >= t, t lowest with Ajay red
episodes <= budget (0.2 and 0.28). Comparators: NEWS-lite 3-h alone at same cost; NEWS-lite >= 7. Report Kranthi, Sundar, mixed,
Naveen reaching red before tip, lead, amber-to-red hours, total. Adopt as registered red if it catches more deteriorating patients
in total than NEWS alone at equal cost, without fewer Kranthis; otherwise red = NEWS >= 7 (stated as NEWS) or exploratory.

## C19 path replay for example patients (written before running, 2026-11-08; descriptive only)
One patient per kind, chosen at random with seed 7 from: Kranthi caught early (C14g early), Kranthi sudden slipper (C14g slip),
Sundar, near-miss Ajay (C14 furthest >= 0.8), Naveen (C14c). Panels per hour: MAP/SI/PP fractions and leading channel 3-h with
line 1.5; S/F with line 247.5 (not Naveen); NEWS-lite with 5 and 7. Marks: first amber, tip. Descriptive; no claims.

## C16h intubation check (written before running, 2026-11-08; integrity)
Vent device hour = device text matching endotrach|ett|ventilator|intubat (c16_hourly). Corrected tip = min(official tip, first vent
device hour). Count S/F crossings (S/F <= 247.5) in vent-device hours. Recompute frozen setup (lead3 >= 1.5 or S/F <= 247.5) and
S/F alone using only hours before corrected tip; compare with original; tip shift; share with no readings before corrected tip.
If corrected catch differs materially, frozen setup and C16/C16c numbers are revised before signing.

## C16h2 NEWS corrected (written before running, 2026-11-08; integrity)
Same corrected tip as C16h (earliest of official tip and first vent device). NEWS-lite 3-h and NEWS with O2 3-h at cost <= 1.0;
only hours before corrected tip count. Compared with frozen setup corrected total 1375. Claim holds if NEWS corrected totals are
below 1375 and NEWS Kranthi share is not above the frozen setup's (0.76).
C16h2 results (corrected tip). NEWS-lite 3-h (line 4.50, cost 0.98): Kranthi 0.73, Sundar 0.58, mixed 0.30, total 1246;
NEWS with O2 3-h (6.33, 0.89): 0.68 / 0.56 / 0.30, total 1199. Frozen setup corrected 1375 (0.76 / 0.65 / 0.36).
DECISION (pre-specified): claim HOLDS on corrected numbers (+129 vs NEWS-lite, ~10%; Kranthi not lower). NEWS barely changed
(1263 -> 1246); setup changed more (1502 -> 1375) because S/F fired on ventilator settings. NEWS slightly earlier on caught patients.
C16g AMENDED before running (2026-11-08): requiring HR high hides compensation in hearts that cannot speed up (beta-blocked,
silent heart). PRIMARY effort witness = RR 3-h >= Ajay q-quantile AND (SpO2 3-h >= 92 or FiO2 not recorded); HR not required.
Variant (comparison only) = RR and HR both >= q-quantile. Setups as before for each. Decision rule unchanged, applied to PRIMARY.

## C16g breathing effort as witness (written before running, 2026-11-08; calibration)
Corrected tip (C16h). Effort witness per amendment above (PRIMARY RR-led; variant RR and HR), each with SpO2 3-h >= 92 or FiO2 not
recorded. Shared setups topped up to 1.0 Ajay episodes/day: (1) frozen lead3 + S/F; (2) lead3 (0.4) + S/F (0.3) + effort (0.3);
(3) lead3 (0.4) + effort (0.6). Report Kranthi, Sundar, mixed, total, Sundars first warned with no FiO2 recorded.
Adopt PRIMARY effort witness if (2) total > 1375 and Kranthi not lower.

## C16i breathing fallback (written before running, 2026-11-08; calibration)
Corrected tip. Breathing = S/F <= ts in hours with FiO2 recorded, OR RR 3-h >= r in hours with FiO2 not recorded. Pressure lead3.
Shared budget topped up to 1.0: pressure 0.4; breathing 0.6 split S/F/effort 0.8/0.2 and 0.6/0.4 (both pre-specified).
Report Kranthi, Sundar, mixed, total, Sundars first warned with no FiO2. Adopt if a version > 1375 total and Kranthi not lower.
C16i results (corrected tip, cost ~1.0). Frozen 1375 (Kranthi 0.76, Sundar 0.65, mixed 0.36; no-FiO2 first warned 54).
Fallback S/F 0.8 / effort 0.2: 0.74 / 0.64 / 0.37, total 1369, no-FiO2 131 (S/F <= 230, RR >= 26.7).
Fallback S/F 0.6 / effort 0.4: 0.75 / 0.64 / 0.36, total 1366, no-FiO2 182 (S/F <= 209, RR >= 23.3).
DECISION (pre-specified): not adopted for MIMIC-III (total not above 1375; Kranthi lower). Fallback is cost-neutral and triples
catches in hours without FiO2. PRE-SET eICU RULE (written before F8): if eICU hours with no FiO2 recorded >= 40%, breathing uses
fallback (S/F 0.6 / effort 0.4), lines set on MIMIC-III resampled to eICU pattern; otherwise frozen S/F.

## C22 kinds of Ajay curves (written before running, 2026-11-08; descriptive)
Frozen amber (lead3 >= 1.5 or S/F <= 247.5). Ajays banded by: max lead3 over stay (<0.5, 0.5-0.8, 0.8-1.1, 1.1-1.4, >=1.4);
min S/F over stay (>400, 300-400, 250-300, 200-250, <200); max lead1 in hours 0-2 (same bands as pressure); quiet = max lead3 < 0.5
and min S/F > 300. Report per band: Ajays, Ajay-days, amber episodes per Ajay-day, share of all Ajay amber episodes.
C22 results (frozen amber; 5031 Ajays, 3566 days, 0.99 eps/day). By max pressure lead3: <0.5 0.72/day (share 0.10); 0.5-0.8 0.67 (0.08);
0.8-1.1 0.65 (0.11); 1.1-1.4 0.64 (0.14); >=1.4 1.57 (0.57). By min S/F: <200 2.01 (0.43); 200-250 1.83 (0.28); 250-300 0.44 (0.09);
300-400 0.44 (0.11); >400 0.00 (9 Ajays). First 3 h >=1.4: 1.62/day (0.45). Quiet Ajays (pressure < 0.5 and S/F > 300 all stay):
216, 0.000/day. Reading: false alarms fall on Ajays near the pressure edge or needing substantial oxygen; none on quiet Ajays.
Only 4% of Ajays were quiet (septic ICU survivors mostly approach an edge; 99.8% needed some oxygen).

## C23 era check (written before running, 2026-11-08; robustness)
Era = icustays.dbsource (carevue / metavision / both). Frozen lines, not re-tuned: setup lead3 >= 1.5 or S/F <= 247.5;
NEWS-lite 3-h >= 4.50. Corrected tip. Per era: Ajay amber episodes/day for each, Kranthi / Sundar / mixed warned before tip,
total, FiO2 source shares. Stable if setup ahead of NEWS in each era and costs within ~25% of 1.0.
C23 results (frozen lines, corrected tip). Stays: carevue 2965, metavision 4341, both 20 (too few).
CareVue: setup cost 0.97, Kranthi 0.73, Sundar 0.73, mixed 0.59, total 649; NEWS-lite 0.90, 0.71 / 0.64 / 0.44, total 578.
MetaVision: setup 1.01, 0.78 / 0.58 / 0.29, total 717; NEWS-lite 1.04, 0.75 / 0.53 / 0.26, total 662.
FiO2 none: carevue 0.24, metavision 0.30. DECISION (pre-specified): STABLE (setup ahead of NEWS in both eras; costs within 25%).
Sundar/mixed lower in MetaVision for both alarms (era effect: more mixed with precise timestamps), not architecture-specific.

## C24 lines for eICU (written before running, 2026-11-08; calibration)
Corrected tip. MIMIC-III oxygen information thinned at random (seed 24) to eICU's pooled no-FiO2 share 0.56 (not by cast); thinned
hours lose S/F. Fallback: lead3 (budget share 0.4) OR S/F in FiO2-recorded hours (0.36) OR RR 3-h in FiO2-missing hours (0.24),
topped up to 1.0 Ajay episodes/day. Lines printed are FROZEN for eICU. Sanity: NEWS-lite 3-h at cost 1.0 on same thinned data.

## C24b split and gate search on eICU-like oxygen charting (written before running, 2026-11-08; calibration)
Same thinned data as C24 (seed 24, no-FiO2 0.56), corrected tip. 20 versions, each topped up to 1.0 Ajay episodes/day:
pressure share 0.4/0.5/0.6/0.7/0.8 (rest: S/F 0.6, effort 0.4); effort A = RR 3-h, B = mean of RR and SpO2 3-h positions vs Ajay
range (median to 95th / 5th pct); gate off/on (on: each reading fires only if not improving vs 3 h earlier). Compare NEWS-lite 3-h at
cost 1.0. Freeze best total if > NEWS total and Kranthi not lower; otherwise rewrite primary claim before signing. Selection among
20 versions on same data is optimistic; eICU is the test.

## C24d Sundar path on eICU-like oxygen charting (written before running, 2026-11-08; descriptive)
Thinned data (C24), frozen candidate B / gate off / pressure 0.7. Sundars by share of pre-tip hours with oxygen recorded (<25, 25-50,
50-75, >75%): caught and lead, architecture vs NEWS-lite 3-h at cost 1.0. For caught Sundars: first reading (S/F, effort, pressure)
and lead. Last 12 h (every 2 h): medians of lead3, S/F, RR 3-h, SpO2 3-h, effort position, oxygen-recorded share; caught vs missed.

## C25 dress rehearsal (written before running, 2026-11-09; rehearsal, not evidence)
MIMIC-III as charted, corrected tip, frozen alarm (lead3 >= 1.35 | S/F <= 98.9 with O2 recorded | effort >= 1.06 without; anchors
RR 19/29, SpO2 97/92.3). Full NEWS = NEWS-lite + 2 if FiO2 > 0.21 + 3 if last GCS (<= 12 h) < 15; 3-h mean; line set to the
architecture's Ajay cost. All pre-set reports printed. Same code to be run once on eICU after signing.
C25 rehearsal (MIMIC-III as charted; not evidence). Cost arch 0.87 / full NEWS 0.86 (line 7.50). PRIMARY Kranthi 0.798 vs 0.643
(+0.155; discordant 105 vs 32; z 6.24). Sundar 0.49 vs 0.58; mixed 0.34 vs 0.29; total 1182 vs 1203; effort-only 1150.
Sundar by O2 band: <25% 0.17 vs 0.12; 25-50% 0.40 vs 0.55; 50-75% 0.46 vs 0.62; >75% 0.61 vs 0.73. First reading: pressure 0.75,
S/F 0.21, effort 0.03. On improving: 0.44 vs 0.46. Load 9.6 vs 9.5 per 20-bed shift. Low-SI Kranthis 0.59 vs 0.42; slippers 0.48 vs 0.37.
All pre-set reports print. Pipeline ready.

## C21 treatment-aware course (written before running, 2026-11-09; DESCRIPTIVE; any red is exploratory, not primary)
MIMIC-III as charted, frozen alarm (C25 table), corrected tip. Per patient with first amber before tip (Ajays to pseudo-tip):
treated within 2 h of amber (bolus from m3_bolus, or FiO2 rise > 0.02); amber cleared at +3 h; tipped within 3 h. Exploratory red R =
treated within 2 h and still amber at +3 h; compared with still-amber-at-+3 h regardless of treatment. Report by group: n, treated,
came back (treated vs untreated), tipped within 3 h, R share and hours from R to tip, Ajays with R per Ajay-day. Confounded by
indication; hourly resolution.
C25b addition (2026-11-09, before running): exploratory re-check red in the rehearsal/eICU script. For every amber episode starting at
hour t0, red fires at t0 + 3 if amber is still present. Comparators: NEWS re-check (NEWS amber at frozen line still present at +3 h)
and NEWS alone at the same Ajay red cost. Report red cost, caught before tip by group, lead, total. Exploratory; not primary.
C25c Naveen report (2026-11-09, before running): Naveens (medical emergency, tip 1-3 h; no oxygen or GCS data) watched by frozen
pressure (lead3 >= 1.35) and effort (>= 1.06, all hours). Report caught before tip and lead, overall and by route. Descriptive.
C25d NEWS re-check matched (2026-11-09, before running): comparator only. NEWS amber line raised (3-h mean full NEWS) until the NEWS
3-hour re-check red costs <= the architecture re-check red cost on Ajays. Report Kranthi, Sundar, mixed, total, lead.
C25d results (comparator). NEWS re-check, amber line 8.33: red cost 0.244 (arch 0.302); Kranthi 0.31 (6.7 h), Sundar 0.29, mixed 0.15,
total 594. NEWS re-check at line 7.50: cost 0.377, Kranthi 0.42. Interpolated at cost 0.30: Kranthi ~0.35-0.36.
Reading: architecture re-check red Kranthi 0.47 leads NEWS (alone or re-check) by ~11-12 points at matched cost; gain is from what the
architecture reads, not only the rhythm. Sundar: NEWS ahead; totals about even. eICU: NEWS re-check line set to nearest cost at or
below the architecture's (as here), interpolation reported.
C25e S/F-forward secondary (2026-11-09, before running): versions A and B as in ARCHITECTURE_V2 correction; NEWS line matched to each
version's Ajay cost; report Kranthi, Sundar, mixed, total, lead; Sundar by oxygen-recorded band.
C25e results (MIMIC-III as charted; rehearsal). Full NEWS matched line 7.33, cost 0.92: Kranthi 0.67, Sundar 0.60, mixed 0.30,
total 1250; Sundar by O2 band 0.14 / 0.57 / 0.66 / 0.76. S/F-forward A (cost 0.99): 0.76 / 0.65 / 0.36, total 1375; bands 0.23 /
0.55 / 0.65 / 0.79. B (cost 0.95): 0.75 / 0.64 / 0.36, total 1364; bands 0.35 / 0.60 / 0.63 / 0.74. Frozen alarm: 0.80 / 0.49 / 0.34,
total 1182. Reading: with room, S/F beats full NEWS for Sundar on as-charted data; B's RR fallback strongest where O2 missing.
Primary stays the frozen alarm (tuned for eICU-like charting); A and B remain pre-specified secondaries. No switch after looking.
