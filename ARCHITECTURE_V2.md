
## Ajay test rules (Registration 2a)

### Who is Ajay
- Septic, never received a vasopressor or invasive ventilation, survived the hospital stay.
- Not Ajay, reported in own rows: arrived on support; died without escalating; grey zone (tipped at 3-5 h).
- Funnel must close exactly in both datasets before signing.

### Watching window
- Matched clock: each Ajay gets a pseudo-tip drawn from the deteriorating patients' tip-time distribution.
- Whole-stay count: false alarms also counted per Ajay-day, up to 72 h.
- Treatment and sedation pause the count, same as for deteriorating patients.

### False alarm (STRICT, primary, no adjusted version)
- Any red on an Ajay is a false alarm. No adjustment for how close he came.
- Amber on an Ajay counted and reported separately.

### Episodes, not a fixed quiet period
- One alarm per episode; while the slide continues the alarm stays on, not re-fired.
- Re-arm only after recovery: back within his own band for RE_ARM_MIN minutes.
- After re-arming, a new slide fires immediately. A new route (shock -> breathing) fires immediately, even mid-episode.
- Each episode's red on an Ajay = one false alarm.

### Kinds of Ajay (sorted by path only; same rule applied to deteriorating patients)
- Quiet / Shock-path / Breathing-path / Fast-start. One Ajay may be in several rows.
- No Ajay is dropped; rows are reported in addition to the total.

### Budgets (set before tuning)
- Red: RED_BUDGET false reds per Ajay-day.
- Amber: AMBER_BUDGET per Ajay-day.
- Fast track: FAST_BUDGET, set on first-3-hour Ajays only.

### Order
1. Fix RED_BUDGET, AMBER_BUDGET, FAST_BUDGET, RE_ARM_MIN and the path-sorting cut-offs.
2. Tune lines on MIMIC-III Ajays to the budgets. Era check (CareVue vs MetaVision).
3. Freeze, sign Registration 2a, run eICU once. No line moves after.

### Reported
- False reds and ambers per Ajay-day: overall; by kind of Ajay; by age band, beta-blocker/pacemaker,
  surgical vs medical; by hospital (eICU).
- Share of reds that were true deteriorating patients.

## Sundar (breathing route): reporting rules
- Blind window is BEFORE intubation (cannula/mask/high-flow), where FiO2 is estimated, not measured.
- Report Sundar results split by charting: >=4 of last 6 h charted vs fewer. No-reading Sundars reported as blind spot, never dropped.
- Breathing side read from the oxygen ladder (device/flow steps) and the S/F trend after each step, not SpO2 level alone.
- MIMIC-III hourly cannot show early detection of Sundar; eICU (5-min SpO2/RR) is the test.

## Comparators (Registration 2a)
- NEWS (as available).
- Rule A, the simple two-number rule: shock index >= 1 and MAP <= 65. New readings (direction, return, fading heart,
  bolus fade) must be shown to add beyond Rule A, not only beyond NEWS.

## Frozen candidates from MIMIC-III (C16c), to be confirmed before signing
- Pressure reading: leading channel (max of MAP, SI, PP road fractions, each clipped -0.5..1.5), 3-h mean. Anchors: recovery
  MAP 75, SI 0.71, PP 58; shock MAP 58, SI 0.96, PP 43. Amber line 1.5 (channel pinned at shock end for 3 h).
- Breathing reading: S/F = SpO2 / FiO2 (FiO2 charted, else device table). Amber line S/F <= 247.5.
- Alarm: either reading crosses. Budget split 0.4 pressure / 0.6 breathing, total 1.0 false alarm per Ajay-day.
- Primary claim for eICU: at matched cost, warns more deteriorating septic patients (pressor, ventilator or both) than full NEWS
  (3-h mean), without warning fewer Kranthis. Secondary: lead time; sneaked-through share by route.
- Tip definition (all analyses and eICU): earliest of pressor start, ventilator start, first charted tube/ventilator device.
- Corrected MIMIC-III result: frozen setup 1375 vs NEWS-lite 3-h 1246 at matched cost (~1.0 per Ajay-day); Kranthi 0.76 vs 0.73.
- Breathing reading for eICU: frozen S/F, unless eICU hours with no FiO2 recorded >= 40% (F8), in which case fallback
  (S/F when FiO2 recorded, RR-led effort when not; budget 0.6 of breathing to S/F, 0.4 to effort). Decided before any eICU outcome.
- Full NEWS for eICU: consciousness from last GCS carried forward <= 12 h (GCS < 15 = not alert); if none, alert. Oxygen points
  from FiO2/device/flow charted (carried <= 12 h).
- Pre-set secondary analysis: breathing read by RR-led effort only (no S/F), at the same total budget, to show the primary result
  does not depend on lopsided oxygen charting (eICU oxygen info: Kranthi 0.86 vs Ajay 0.19 of hours).
- eICU tip definition (F5/F5b): earliest of respiratorycare vent start, treatment-table mechanical ventilation, tube/ventilator charted
  as oxygen device, first pressor. Settings-only excluded. Treatment-table times run ~8 h after respiratorycare when both exist.
- eICU oxygen mapping (from A5 listing; same FiO2 table as MIMIC-III): room air (ra, r/a, room air, none (room air)) 0.21;
  nasal cannula (nasal cannula, nc, oxymizer, oximizer) 0.21 + 0.04 x L/min (2 if missing), max 0.44; masks/trach (venturi, face,
  simple, oxymask, cool aerosol, trach collar, tc, trach mask/collar) 0.40; non-rebreather 0.85; high-flow (hfnc, high flow,
  [heated] high flow nasal cannula) 0.60; non-invasive (bipap, bi-pap, bipap/cpap, cpap) 0.50; ventilator/vent/mechanical
  ventilator = tip sign, not S/F; other = no estimate. Numbers: O2 L/% 1-15 = L/min, 21-100 = percent, 0-1 = fraction, else ignored;
  FiO2 / FIO2 (%) 21-100 = percent, 0-1 = fraction, else ignored. Charted FiO2 overrides device; carry-forward <= 12 h.
- eICU resolution: vitals averaged to hourly values (same pipeline as MIMIC-III). 5-min density not used in this registration (limit).
- Ajays in eICU watched to a pseudo-tip drawn as in MIMIC-III (matched clock), so false alarms per Ajay-day are comparable.
- Pre-set secondary (eICU): share of alarm episodes (architecture vs NEWS) starting while the patient's readings were improving
  (leading pressure channel falling, S/F rising, or RR falling vs 3 h earlier). Tests whether NEWS spends more alarms on recovering
  patients. Descriptive; no claim depends on it.
- Pre-registered exploratory (eICU): "not coming back" gate re-tested on 15-minute aggregated vitals; reported either way.
- Path view shows "coming back" / "still sliding" beside each amber (display only).

## Registration 2a: primary claim and frozen alarm (draft, 2026-11-08)
Frozen ward alarm (version B, gate off, pressure share 0.7; lines set on MIMIC-III thinned to eICU oxygen charting, as printed by
c24c_freeze.py): amber if ANY of
  (1) pressure leading channel (max of MAP, SI, PP road positions, 3-h mean) >= 1.35;
  (2) S/F <= 99, in hours with oxygen recorded;
  (3) breathing effort position (mean of RR and SpO2 positions vs Ajay range, 3-h mean) >= 1.06, in hours without oxygen recorded.
Total cost 1.0 amber episode per Ajay-day. Tip = earliest of pressor, respiratorycare vent start, treatment ventilation, tube charted.
PRIMARY (one-sided): at matched cost against full NEWS (3-h mean, line set to the same Ajay cost on eICU), the frozen alarm warns a
larger share of Kranthis (pressor-first, tip >= 5 h) before the tip. MIMIC-III support: 0.80 vs 0.73 (eICU-like oxygen), 0.76 vs 0.73
(corrected tip), both eras ahead, pressure-alone 0.83 vs 0.73.
KEY SECONDARY (two-sided, no predicted winner): whole-ward total (Kranthi + Sundar + mixed). MIMIC-III eICU-like: 1216 vs NEWS 1246.

## Sundar: how the architecture reads the breathing path into sepsis (pre-specified descriptive secondary)
What it reads: S/F (SpO2 read against the oxygen it took) when oxygen is recorded; when it is not, breathing rate and SpO2 together,
as a position against the range recovered patients show. Pressure is watched for every patient, Sundar included.
What MIMIC-III (thinned to eICU oxygen charting) showed:
- Caught Sundars show a visible path: over the last 12 h, SpO2 held near 95 while S/F fell from ~230 to ~100 and breathing rose
  from ~23 to ~24.5; their pressure channel also sat near the shock end (0.8). Pressure spoke first in 59% of caught Sundars
  (median 16.8 h before the tube), S/F in 22% (11.3 h), breathing effort in 18% (12.1 h).
- Missing oxygen records cost Sundars: caught share rises with oxygen-recorded hours (22% below 25%, 52%, 68%, 53% above 75%).
- Missed Sundars looked calm on every channel read (breathing 18-20, SpO2 96-97, pressure near the recovered end, oxygen mostly
  unrecorded): their decline was not visible in these vitals.
- NEWS caught more Sundars in every oxygen band (28 / 62 / 73 / 66%), at the same cost. Expected in eICU: NEWS ahead for Sundar.
Pre-set reports for eICU: Sundar caught and lead time by oxygen-recorded band; first reading to speak; last-12-h path medians for
caught vs missed; the same for NEWS. No claim of superiority for Sundar.
Why: in eICU, oxygen information is absent in 56% of pre-tip hours (more often for recovered patients and Sundars than Kranthis),
so the oxygen dose that reveals a masked decline is often unknown; NEWS reads several other signs every hour.

## Search log (every version tried on MIMIC-III before freezing) and honest limits
Tried and set aside: red by dwell or fast jump (C18), red by agreement with NEWS (C18b), own pressure lines (C16f), effort witness
splitting S/F budget (C16g), "not coming back" gate (C24b, 10 versions), RR-only fallback (C24b), budget splits 0.4-0.8 (C24b).
Chosen: B / gate off / pressure 0.7 = best whole-ward total of 20 versions on thinned data (optimistic by selection).
Integrity checks that lowered results: corrected tip (1502 -> 1375), eICU-like oxygen thinning (1375 -> 1176-1216).
Limits: no architecture red (red stays NEWS-based or exploratory); not earlier than NEWS on the clock; Naveen's first hour not
readable at hourly resolution; mixed patients often uncharted before the tube; oxygen charting in eICU partly reflects clinician
concern (effort-only check pre-set); eICU 5-min density unused (hourly pipeline).
Searching stops here. C24f (which NEWS parts catch Sundar) is descriptive only. No further versions before the eICU run.

## FROZEN ALARM (printed by c24c_freeze.py, 2026-11-08; cost on thinned MIMIC-III 0.95)
pressure leading channel 3-h >= 1.350 | S/F <= 98.9 (oxygen recorded) | breathing effort position >= 1.060 (oxygen not recorded)
Effort position = mean of (RR - 19.0) / (29.0 - 19.0) and (97.0 - SpO2) / (97.0 - 92.3), 3-h mean (anchors: MIMIC-III Ajays).
Pressure anchors: recovery MAP 75, SI 0.71, PP 58; shock MAP 58, SI 0.96, PP 43; fractions clipped -0.5..1.5.
- WARD DESIGN (frozen): amber as frozen above; RED = amber still present at the 3-hour re-check after an amber episode starts.
  Origin: C21 (MIMIC-III, after the search stopped); MIMIC-III: red cost 0.20 per Ajay-day, Kranthi 0.40 caught ~6.4 h before the tip.
  Status: pre-specified KEY SECONDARY; one-sided prediction to be fixed after C25b (vs NEWS alone at the same red cost, and vs NEWS with
  the same re-check). Not part of the primary claim.
- Pre-specified SECONDARY (eICU): S/F-forward version from C16c/C16i, no new tuning: pressure leading channel >= 1.5, S/F <= 247.5
  (oxygen recorded), RR-led effort fallback (oxygen not recorded), split 0.4 pressure / 0.6 breathing. Reported for Sundar, Kranthi,
  mixed and total vs NEWS at the same cost. Rationale: the frozen S/F line (99) was set under even oxygen thinning; real eICU oxygen
  charting is far sparser in Ajays (0.19 of hours), so the frozen line may be stricter than needed. Not part of the primary claim.
- CORRECTION (2026-11-09, before running): the S/F-forward secondary is two previously tested versions, unchanged:
  A (C16c) pressure lead3 >= 1.5 OR S/F <= 247.5; B (C16i fallback 0.6/0.4) pressure lead3 >= 1.5 OR S/F <= 209 (oxygen recorded) OR
  RR 3-h >= 23.3 (oxygen not recorded). Each compared with full NEWS at that version's own Ajay cost. Sundar also split by
  oxygen-recorded share. Replaces the earlier untested combination.

## PRIMARY TEST (fixed before signing)
Population: eICU Kranthis (pressor first, tip >= 5 h, corrected tip). For each: caught before tip by the frozen alarm (yes/no) and by
full NEWS (3-h mean, line set to the nearest value whose Ajay amber cost is <= the frozen alarm's). Test: one-sided exact McNemar on
discordant Kranthis (architecture-only vs NEWS-only); supported if architecture share is higher and p < 0.05. Also report the
difference in shares with a 95% CI (paired). If not supported, report as not supported; no re-analysis, no change of lines or groups.
Key secondaries (whole-ward total two-sided; re-check red one-sided vs NEWS alone at equal red cost) use the same paired approach
and are reported without multiplicity claims.

## eICU PIPELINE (built before signing; not run on eICU until signed)
eicu_cast_tip.sql (cast, tip, vaso/vent times, LOS) + eicu_hourly.sql (hourly mean vitals incl. cuff and arterial BP; last FiO2,
flow, device; min GCS; hours -12..95) -> eicu_run.py: Ajay pseudo-tip = random draw (seed 2026) from tips of Kranthi/Sundar/mixed
(5-72 h), capped at LOS; windows to min(tip, 72 h); oxygen mapping, frozen anchors, S/F, effort, NEWS as specified; then the
C25 rehearsal analysis code unchanged, with eICU Naveen (route from vaso/vent times) and slipper (averaged road 3-h >= 0.53;
never or < 2 h before tip) reports substituted. Checked by BigQuery dry run and on synthetic data only.
