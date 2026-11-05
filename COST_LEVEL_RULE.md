# COST_LEVEL_RULE — exploratory, hourly MIMIC, written before running (2026-11-05)
Status: EXPLORATORY. Uses calibration + test splits after Registration 1 closed.
A result here is a lead for Registration 2 (HiRID), never a finding.
Source: physionet-data.mimiciv_3_1_derived.vitalsign, hour = floor(minutes since ICU intime / 60),
hours 0-47; hourly medians of HR, SBP, DBP. Shock index SI = HR/SBP; pulse pressure PP = SBP - DBP.
High-cost hour: SI >= 1.0. Narrow: PP <= 35 mmHg. Runs count consecutive charted hours; a missing hour breaks a run.
Window: escalated = hour 0 to the last hour before esc_h (capped at 24 h); stable = hours 0-23.
Measures per stay:
  arrived_hi        SI >= 1 in first charted hour
  run3, run6        a run of >= 3 / >= 6 high-cost hours
  run3_narrow       a run of >= 3 hours with SI >= 1 AND PP <= 35
  eased_of_arrived  arrived_hi, and SI < 1 at every charted hour from hour 3 to hour 5
  active_at_end     (escalated) SI >= 1 in the last charted hour before esc_h
  hrs_before        (escalated) length of the high-cost run ending at that hour
  from_arrival      (escalated) that run began at the first charted hour
Groups: escalated (Kranthi), escalated_hyperacute (Naveen, reported separately),
stable split into sick (day-1 SOFA >= 6 or 12-h lactate >= 4) and mild.
KEY COMPARISON (decided now): run3_narrow, escalated vs stable_sick and vs stable_mild.
Thresholds SI 1.0 and PP 35 were suggested by the 6-patient pilot (post hoc); stated openly.

## Deviation C1 (after first run, 2026-11-05)
eased_of_arrived counted patients with no charted hour in 3-5 (e.g. escalated before hour 3)
as "not eased", biasing escalated groups down. Corrected: such patients are excluded (NaN).
First-run values kept on record: Kranthi 0.198, stable_sick 0.281, stable_mild 0.303.

## Check C2 (written before running, 2026-11-05)
eased_of_arrived restricted to escalated patients with esc_h >= 8, so hours 3-5 lie
>= 3 h before escalation. Compared with stable_sick and stable_mild as before.
Interpretation fixed now: gap persists -> lead for HiRID; gap closes -> mostly proximity to tip.
Also report denominators (arrived high with a charted hour in 3-5) for every group.

## Check C3 (written before running, 2026-11-05)
Tip-aligned climb. Kranthi = escalated with esc_h >= 8; relative hour = hour - floor(esc_h),
window -8 to -1. Comparator: stable_sick, each given a pseudo-tip drawn (seed 7) from the
Kranthi esc_h distribution (>= 8, capped 24); same window. Per relative hour: median SI,
HR, SBP, PP and share SI >= 1. Climb shape per patient (first vs last charted hour in window):
high_throughout (both >= 1), climber (first < 1, last >= 1), eased (first >= 1, last < 1),
spiked (both < 1, max >= 1), never_high (max < 1). Also SI slope (per hour) over the window.
Descriptive; no threshold chosen from it.

## Check C4 (written before running, 2026-11-05)
Climb shapes and tip-aligned SI from C3, split by escalation route from missh.esc_type_cal/
esc_type_test (labels as stored: e.g. pressor-first, ventilator-first, both, other).
Report per route: n, shape shares, median SI and SI >= 1 by hour -8 to -1; sick stable as reference.
Prediction fixed now: high_throughout + climber share is higher in pressor-first than in
ventilator-first; never_high is higher in ventilator-first.
If so: the straining quarter is mainly the shock route, and the heart-vs-pressure reading
names that route. If not: SI strain does not mark the shock route at hourly charting.

## Check C5a (written before running, 2026-11-05)
Pressor-first Kranthis split by C3 shape: never_high vs strain (high_throughout + climber);
sick stable as reference. Hours -8 to -1 before tip / pseudo-tip. Per hour: median DBP,
SBP, pulse pressure, MAP estimate (SBP + 2*DBP)/3, HR, diastolic shock index DSI = HR/DBP.
Per-patient slopes (per hour, >= 4 charted hours) of PP, DBP, MAP estimate: median, IQR,
share <= -1 mmHg/h (falling) and >= +1 mmHg/h (rising).
Prediction fixed now: pressor never_high shows falling DBP/MAP and rising DSI vs sick stable
(leaking-vessel route); PP may widen (relaxed vessels) or narrow (volume loss);
pressor strain shows narrow PP. If never_high matches sick stable on all: not visible on hourly BP.

## Check C5b (written before running, 2026-11-05)
Breathing witness. Same windows and groups as C5a (pressor never_high, pressor strain,
sick stable), plus vent-first Kranthis (any shape) as the lung-route contrast.
Hourly medians of RR and SpO2 from mimiciv_3_1_derived.vitalsign, hours -8 to -1.
Per-patient slopes (>= 4 charted hours): RR (breaths/min per h), SpO2 (% per h).
Patterns per patient: "acid" = RR slope >= +0.5 and SpO2 slope > -0.25;
"lung" = RR slope >= +0.5 and SpO2 slope <= -0.25; else neither.
Prediction fixed now: pressor never_high shows more "acid" than sick stable;
vent-first shows more "lung" than sick stable.
Caveat stated now: oxygen therapy can hold SpO2 up, hiding a lung pattern.

## Check C6 (written before running, 2026-11-05)
Who are the silent-heart patients? Groups as C5a/C5b: pressor never_high, pressor strain,
vent-first, sick stable (pseudo-tip). Tip hour = hour - rel from climb_window.
Per group: n; age (anchor_age, median); share male; first ICU unit (CVICU, CCU, MICU,
SICU, MICU/SICU, TSICU, Neuro); share elective or same-day surgical admission;
share with sedation (propofol, midazolam, dexmedetomidine, fentanyl) started before tip;
share with a beta-blocker prescription starting before tip.
Prediction fixed now: never_high has higher shares of CVICU, elective/surgical admission,
sedation before tip and beta-blockers than pressor strain and sick stable.
If so: the "silent heart" is largely a different patient type (post-surgical, sedated or
beta-blocked), not a hidden septic route. If not: it remains a candidate septic route.
