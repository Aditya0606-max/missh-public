# LESSONS_REG1 — carried into Registration 2

## L0. Waveform availability (checked 2026-11-03/04)
MIMIC-IV Waveform Database v0.1.0: 198 patients (RECORDS). Of these, 76 are
in the registration-1 sepsis cohort (20 calibration, 56 test; missh.wave_subjects
joined to missh.split_reg1). Far below the ~150-200 deteriorating patients with
pre-anchor coverage needed per split. Use as practice ground only.
Candidate source for Registration 2: HiRID (~34k admissions, 2-min resolution).

### L0 update — coverage against WAVE_COVERAGE_RULE (2026-11-04)
Of 76 waveform subjects in the sepsis cohort, 41 have a recording overlapping
their cohort stay (22 escalated, 15 stable, 4 rescued/other). Checked against
the rule windows (-6 to -4 h and -2 to 0 h before esc_h): deteriorating usable
= 1 (16848565), borderline = 1 (11552552, late window 75% covered); all others,
including all 7 hyper-acute, have no recording before escalation. Hyper-acute
recordings mostly begin at the moment of escalation (monitor registration lags
resuscitation). Stable with most of first 12 h recorded = ~7. Summed hours
before escalation overstated coverage; the rule's window check is what counts.
Signals in the two inspected records: HR, beat-to-beat HR, RR, SpO2, perfusion
index every ~1 s; BP by cuff only (no arterial line). Cuff frequency higher in
the escalated patient: never use measurement frequency as a signal.

### L0b — origin-ruler watch on waveform pilot (CORE_WATCH_RULE, 2026-11-04)
37 labelled patients (22 escalated, 15 stable): all 37 obtained an origin ruler
from continuous HR/RR/SpO2 (vs 43% without HR-MAP ruler at hourly charting).
Pre-tip watch possible in 2: 16848565 stepped toward worsening ~2 h and ~1 h
before tip (cos 0.88, 0.76); 11552552 stepped away (-0.89, -0.75). No pattern.
At-tip on support (n=6): median Dw drifted away from worsening (-0.4 to -1.8);
exception 14695840 moved +13 to +15 and stayed. Stable patients reached +6 and
-13; toward-shares ~0.4-0.6 (chance). Measurement note: many cosines exactly
+/-0.58 or +/-1.00 = single-channel integer steps between 15-min medians; use
means or beat-to-beat HR in future readers. Descriptive pilot only.

### L0e — compensated shock hidden by his own origin (2026-11-04, one patient)
16848565 (pressor 9.0 h): own-origin path stayed near home, but against stable patients
at hours 2-9: shock index 1.00-1.43 (stable 0.72-0.94), cuff MAP 64.5-73, pulse pressure
22-32 (stable 38-61), HR 106-120, RMSSD 2.8-11 ms (stable median 35), HR wobble low.
He arrived in compensated shock; his ruler was taken in that state, so relative measures
could not see it. Valley signature here = rigidity (low variability), not wider wobble.
Lesson: read relative path AND absolute cost (shock index, pulse pressure, HRV vs
physiological lines). Check sick-stable patients before reading cost as tipping vs severity.

### L0i — check C3: how Kranthis climbed toward the tip (hourly, exploratory)
Kranthi (esc >= 8 h, n=1921) vs sick stable with pseudo-tips (n=1351), hours -8 to -1.
Median SI 0.77 -> 0.82 (stable flat 0.73-0.75); SI >= 1 19% -> 28% (stable 12-14%);
HR +3, SBP -5, PP -2 in Kranthis; stable flat. Gap already present at -8 h.
SI slope median +0.003/h (stable -0.002/h), IQRs overlap almost fully.
Shapes: high_throughout 13.4% vs 6.7%; climber 11.2% vs 5.1%; eased 6.5% vs 6.4%;
spiked 10.1% vs 9.7%; never_high 58.8% vs 72.0%.
Reading: ~1 in 4 Kranthis show a visibly straining heart (2x stable), slow and small
relative to hourly wobble; ~6 in 10 never cross SI 1 before the tip. Next: split by
escalation type (pressor-first vs ventilator-first) to name the route.

### L0l — check C5b: breathing witness (hourly, exploratory)
RR median -8 -> -1 h: pressor never_high 19 -> 19; strain 22 -> 22; sick stable 19 -> 19;
vent-first 21 -> 23. SpO2 96-97 in all groups (oxygen therapy likely holding it up).
"acid" (RR up, SpO2 steady): never_high 13.4%, strain 13.6%, stable 15.0%, vent 19.5%.
"lung" (RR up, SpO2 falling): never_high 9.8%, strain 10.2%, stable 6.3%, vent 12.2%.
Prediction 1 (never_high more acid than stable): NOT supported.
Prediction 2 (vent-first more lung than stable): supported, weakly (2x, tiny slopes).
Reading: the silent-heart group shows neither heart nor breathing response; only
pressure slides. Raises whether they are sedated/ventilated, beta-blocked or
post-cardiac-surgery patients rather than a hidden septic route. Next: who they are.

### L0n — check C7: breathing route seen through oxygen need (hourly, exploratory)
Vent-first Kranthis (n=1224) vs sick stable on oxygen (n=820), hours -8 to -1:
SpO2 flat 96 vs 96-97. FiO2 0.40 -> 0.50 (jump in last hour) vs 0.33 flat.
S/F 248 -> 193 (-22%) vs ~291 flat; ROX 11.1 -> 8.1 vs ~14.4 flat; RR 21 -> 23 vs 19-20.
Already lower at -8 h. Most of the fall in the last 3 h (248 -> 230 by -3 h, ~-7%).
FiO2 step any 17.9% vs 8.7%; step again within 3 h 8.7% vs 3.5%.
RR answered S/F drops 64% vs 57%; HR 51% vs 47% (no separation).
Per-patient S/F slope median -0.14/h; 82% no charted FiO2 step (sparse charting).
Prediction (C7) supported at group level. Cautions: FiO2 is set by staff (late fall partly
clinician action; judge >= 2-3 h before intubation); signal concentrated in a subset;
"no staircase" not usable for airway-protection intubations at this charting density.
Reading: the breathing route's hidden slide is in oxygen need, not SpO2. Registration 2
needs an oxygen-need axis (S/F, ROX), judged before the final hours.

### L0r — check C8: Sundar's oxygen staircase in MIMIC-III (descriptive)
Sundar (vent-first, tip >= 6 h, with oxygen information) n=938 vs Ajay on oxygen n=4,003
(Ajay never on oxygen 850). Start level median 2 vs 1; max before tip median 4 vs 2;
climbed 35% vs 17%; climb size 0.74 vs 0.27; reached mask+ 62% vs 34%; reached
non-rebreather/high-flow/NIV 53% vs 25%; first climb median 9.2 h before tip (Ajay 8.4 h).
Sundar max level: 0-2 ~38% (likely airway-protection intubations), 3 ~8%, 4-5 ~53%.
Reading: oxygen-route Sundars show hours of real, recorded worsening (charting reflects staff
concern, but each step happened). Next (C8b): whether the HR/RR/SpO2 vector moved during
the climb in Sundars with waveform data; if not, the vector lacks an oxygen-support axis.

### L0x — N1/N2: fast crashers (Naveen) in MIMIC-III (counting only)
N1: tip within 3 h = 6,232; heart/vascular surgery 1,292 (21%), surgical 1,214 (19%),
medical emergency 3,726 (60%: vent first 1,953, pressor first 1,039, both 734).
N2 (medical emergencies, signal presence from arrival to tip): any numerics record 1,305; anything
recorded between arrival and tip 364; median journey 76-99 min; recording started ~52-68 min after
arrival; HR present ~10-20% of journey. Watchable from arrival (data by 30 min, HR/RR/SpO2 >= 80%):
36 (pressor first 17, vent first 16, both 3); with ABP >= 80%: 4; with >= 1 cuff reading: 32.
Reading: recording for fast crashers typically starts near the tip; early watching of Naveen is
not testable in MIMIC-III (36 = case series). Check eICU's from-admission charting for Naveen.

### L0y — C13: journeys from ICU arrival to tip (hourly, MIMIC-III; descriptive)
Journeys <= 72 h. Shock side (SI >= 1, MAP <= 65, PP <= 30): Kranthi (n=375) stayed bad 60%, relapsed 13%,
recovered 4%, slid 15%, sudden 4%, stayed good 5%; Ajay (n=4,638) 20 / 7 / 17 / 10 / 5 / 40%;
Sundar (n=793) 16 / 9 / 20 / 9 / 4 / 42%; mixed (n=142) 33 / 10 / 15 / 12 / 7 / 23%.
Breathing side (RR >= 25, SpO2 <= 92): Sundar stayed bad 27%, slid 16%, stayed good 26%;
Ajay 12 / 9 / 52%; Kranthi 19 / 11 / 41%; mixed 30 / 11 / 32%.
Reading: ~3/4 of Kranthis were past shock lines on arrival; only ~15% arrived good and slid (the pattern
Registration 1's own-origin design targeted). Arriving bad is common in Ajays too (44% on shock side);
not recovering separates (stayed bad 60% vs 20%; recovered 4% vs 17%). Each route shows on its own side
(Sundar's shock side resembles Ajay's). Journeys > 72 h: recover-then-relapse common (Kranthi 44%, Sundar 40%).
Cautions: hourly charting; blunt any-line rule; "stayed bad" includes final pre-tip hours; pre-ICU unseen.

### L0z — C13c: how early no-return separates (hourly charted, MIMIC-III; calibration)
Shock side, arrived-bad Kranthi (n=303; 225 at h6) vs arrived-bad Ajay (n=2,103; 1,805 at h6):
AUC burden 0.64 / 0.66 / 0.67 at h3 / h4 / h6 (median lead 7.9 / 6.9 / 8.9 h); bad hours 0.63-0.67;
longest good run 0.62-0.66; SI/MAP slopes and time-to-65 0.50-0.58; route balance 0.55-0.59.
Breathing side, arrived-bad Sundar (n=503) vs Ajay (n=1,581): burden 0.59-0.60, bad hours 0.59-0.60,
good run 0.57-0.60 (lead ~13-14 h); oxygen need not yet included.
Reading: accumulated burden past fixed lines and failure to recover separate moderately, hours before
the tip; speed does not at hourly cadence. Pending: per-charted-hour normalisation (charting-frequency
bias) and comparison with NEWS / SI alone on the same patients and times.
L0cc spread (first hour; arrived-bad Naveen n=143 vs arrived-bad Ajay n=1,304): HR max median 94 vs 95
(IQR 76-112 vs 80-111); MAP min median 60 vs 68 (IQR 53-69 vs 60-81); SI max median 1.01 vs 0.84;
SI >= 1.2 in 23% vs 7%; MAP < 65 with SI < 1 in 26% vs 24% (not distinctive).
Reading: fast crashers differ by DEPTH OF PRESSURE FALL, not faster heart rate; a quarter are fast straining pumps
(SI >= 1.2). Low MAP with modest SI is as common in recovering patients, so it does not mark the fast crasher.
Shock burden (SI excess + MAP deficit) captures both.
