# F4 ESTIMATOR SPECIFICATION
# Extracted from scripts/forcelab2.py (rev 2), 2026-08-19.
# Extraction, not invention. Two items remain OPEN.

## Pipeline
1. BRI: per channel, z-score against the patient's own baseline mean and SD
   over the first `baseline_hours` observations. Never population-referenced.
2. Analysis window W of length `window_hours`, stride `stride_hours`.
   Windows with fewer than `min_eff_n` observations are DROPPED, not NaN-filled.
3. Within-window linear detrend: slope by least squares on a centered index,
   subtracted per channel.
4. Pearson correlation matrix of the detrended window: rho_W.
5. Baseline correlation rho_B: identical detrend + Pearson on the baseline window.
6. Six-vector: six[p] = rho_W[i,j] - rho_B[i,j] for the six unordered pairs
   HR-MAP, HR-RR, HR-SpO2, MAP-RR, MAP-SpO2, RR-SpO2.

## Gate vs claim separation
F4_scalar = mean(|six|)  -- magnitude only, SIGN-BLIND. This is what the cascade
gates on. The SIGNED six-vector is carried to the downstream arm comparison and
is never consulted by the gate. This implements A1a's firewall.

## Constants as implemented
baseline_hours = 24
window_hours   = 6
stride_hours   = 1
min_eff_n      = 5

## OPEN 1 — irregular Delta-t
_detrend uses t = arange(n), the observation INDEX, not the timestamp. Windows
with observations at 0,1,2,3h and 0,1,2,9h detrend identically. Not defensible
at MIMIC charting cadence, and less so at the 4-hourly deployment reality.
Requires a decision: resample, time-weighted detrend, or reject windows with
gaps beyond a stated tolerance.

## OPEN 2 — min_eff_n conflict
Implemented value is 5. A later draft baseline spec proposed 8. Neither carries
a derivation. This is the II.4 minimum-effective-n field and should come from a
Class S sweep under known ground truth, not be inherited from a testbed default.

## Provenance warning
Constants above are testbed defaults from an exploratory script. Freezing them
unchanged would convert exploratory choices into pre-registered commitments
without reasoning. Each requires justification or a Class S derivation.
