# Observation cadence and window structure
Class R. No data contact.

## 1. Sampling
    HR, RR, SpO2   pulse oximeter, continuous, q15min
    MAP            NIBP cuff, AUTOMATED cycling, q30min
    Temperature    as charted by the ward; no assumed cadence

RR is derived from the plethysmogram, not measured directly. It degrades with
motion, poor perfusion and arrhythmia -- conditions a deteriorating patient
has. Stated as a limitation, since RR appears in multiple pairs.

## 2. Why q30 for NIBP and not q15
This is a clinical constraint, not a statistical one.

A cuff must occlude arterial flow to measure. At q15 that is 96 inflations per
day on one arm. Documented consequences: sleep disruption, bruising and
petechiae, venous congestion distal to the cuff, skin injury in frail or
anticoagulated patients, and rarely nerve compression. Sustained q15 on a ward
patient is outside routine practice.

The circular problem, which is the binding reason: cuff-disturbed sleep raises
heart rate and alters autonomic tone. At q15 the measurement protocol would
perturb the physiology the architecture is reading.

AUTOMATED cycling is required, not nurse-initiated. Manual cycling stops
overnight, which would take MAP pairs out exactly when a patient is least
observed and when ward deterioration is least likely to be noticed.

## 3. Window structure -- two speed
    Oximeter pairs (HR-RR, HR-SpO2, RR-SpO2)      1-hour windows, 4 points
    MAP pairs (HR-MAP, MAP-RR, MAP-SpO2)          2-hour windows, 4 points
    Temperature pairs                             per admissibility only

Same points per window, different clock. Consequence: MAP pairs close every two
hours, so the perfusion axis reports up to an hour behind the oximeter pairs.

## 4. Open -- DP across mixed speeds
Not yet specified. At hour 3 the oximeter pairs have three closed windows and
the MAP pairs have one. What "N consecutive windows of persistence" means
across differing update rates is undecided.

NOTE: this is structurally the same problem as (a) a treatment suspension and
(b) a pair dropping out of admissibility. All three are "the counter meets a
window where a pair does not update." They should share ONE specification, not
three. Writing them separately would require defending why the same situation
has different answers.

## 5. Confirmatory-run consequence -- unresolved
MIMIC ICU patients largely have arterial-line MAP, continuous and dense.
Kranthi's deployment assumes a q30 cuff. Testing on native arterial MAP would
validate a different instrument from the one deployed.

Options, to be decided before GATE-01:
    (a) decimate MIMIC MAP to q30 to match the ward
    (b) run at native density and state the ward version as an untested
        extrapolation

This is the density confound in a new location and must not be left implicit.

## 6. Standing conditions
- Cadence is fixed before data contact. N (the DP persistence count) is derived
  against this cadence and is invalid under any other.
- No carry-forward or interpolation to satisfy any cadence requirement.
