# Omega: role, scaling, floors, variability track
Class R. No data contact.

## 1. Omega's role -- CHANGED
Omega was a SEVERITY gate: did the patient move far enough to matter. It could
veto a patient whose coordination was dissolving without large displacement --
the compensating patient, spending reserve to hold his numbers steady, who is
precisely the patient early warning exists for.

Omega is now a NOISE FLOOR: did anything real happen at all. It rejects change
that is statistically detectable but below measurement precision.

Why this is better justified: a noise floor is derivable from device
specification. A severity threshold requires clinical evidence about how much
displacement matters, which this pre-registration does not have. The old Omega
was making that claim implicitly.

CONSEQUENCE ACCEPTED: Omega now rejects fewer patients, so the false-positive
rate rises by an amount not yet characterised. S0 must re-run. Requires an
AMENDMENTS entry alongside the earlier Omega withdrawal.

Floor value: DECIDED 2026-10-31, route-specific (A8).
  Displacement route: Omega_floor = sqrt( (4/m) x sum over present channels
  of (floor_c / SD_used_c)^2 ), the distance produced if every channel were
  off by exactly one charted unit. Smaller travel is indistinguishable from
  rounding.
  Coupling route: 95th percentile of the stable-patient |delta rho| null,
  same window and ruler procedure, calibration split, computed before any
  outcome is viewed.

## 2. Frozen ruler
The per-channel SD used to standardise Omega is computed ONCE from a stated
source and never recomputed. Otherwise a treatment response inflates the SD and
every later Omega is deflated -- the gate going quietest for the patients who
arrived sickest.

Source: DECIDED 2026-10-31 per REFERENCE_RULE.md (1d5e272): his own detrended
SD over clean reference hours, blended with SD_pop (SD_POP.txt, 56dbe50),
i.e. a stated combination of (a) and (c). Options considered:
    (a) a treatment-free stretch, wherever it falls
    (b) a robust estimator (MAD scaled to SD) over the reference block
    (c) a per-channel value from a stated reference population
This choice carries the whole fix.

## 3. Per-channel floors
    SD_used = max(SD_observed, SD_floor)

    SpO2 : 1 %      charted resolution (accuracy figure is bias vs a reference;

                    bias cancels within patient)
    HR   : 1 bpm    charted resolution
    RR   : 1 /min   charted resolution (MIMIC RR may be monitor-derived or counted)
    MAP  : 1 mmHg   charted resolution (NIBP repeat error worse than arterial
                    line; not measured here)

Derivation: device bias is constant within a patient and cancels against his
own centre; what does not cancel is repeat error and charting resolution.
Repeat error per device is not recoverable from the record, so the floor is
the charted resolution: a stated LOWER BOUND, not a tuned value. Larger floors
are tested in the section 5 grid.

The floor limits the leverage an unusually low within-patient SpO2 variability
can exert on Omega. SpO2 remains in three of six pairwise coordinates; only its
standardised displacement is capped.

SCOPE: Omega's scaling only. Correlation is scale-free, so F4 is unaffected by
any SD choice. SpO2's ill-conditioning in the coupling domain has a different
cause and is not addressed here.

## 4. Variability -- separate descriptive track
SD frozen for scaling; per-window variability still tracked and reported.
DESCRIPTIVE ONLY, never gates, no threshold registered.

## 5. Sensitivity grid -- pre-committed
Floors varied for ALL FOUR channels, not SpO2 alone.
Cells: all four floors at 1x, 2x and 3x the resolution floor.
    holds in every cell -> report primary, state stability
    flips in any cell   -> the instability IS the finding
Fixed before the grid runs.

## 6. Standing conditions
Fixed before data contact. Variability never gates. Any floor not justifiable
from device specification is flagged as tuned.
