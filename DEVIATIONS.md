# DEVIATIONS.md — changes after signing (reg1-signed, d016f83)

## D1. Export row limit raised (2026-11-03, before any test-split export)
pipeline/export.sh used --max_rows=500000, enough for calibration (~162k hourly
rows) but below the expected test-split size (~600-650k hourly rows), which
would have truncated files silently. Raised to 3,000,000. No definition,
setting or analysis changes. Made before running any test-split query.

## Note N1. Output title (2026-11-03)
RANK_REHEARSAL.txt on the test split carries the hard-coded title
"(calibration, frozen pieces)" from rank_01.py. Data are the test split
(1,939 deteriorating patients). Label only; no computation affected.

## Note N1. Output title (2026-11-03)
RANK_REHEARSAL.txt on the test split carries the hard-coded title
"(calibration, frozen pieces)" from rank_01.py. Data are the test split
(1,939 deteriorating patients). Label only; no computation affected.

## Note N2. Output heading (2026-11-03)
The combined-model block in RANK_REHEARSAL.txt (test split) carries the
hard-coded heading "in-sample on the 20%" from rank_01.py. To be confirmed
by D2, which recomputes AUC A and AUC B from the test files.

## D2. Combined-model bootstrap interval added (2026-11-03, before computing it)
A16 requires support = AUC(B) - AUC(A) > 0 with a patient-bootstrap 95% CI
lower bound > 0 at k = 2 h. rank_01.py scored models A and B and printed the
gain but omitted the interval. d2_combined_ci.py copies rank_01.py's combined
scoring (lines 69-93) and boot() (lines 36-44) unchanged, and calls boot() with
n = 300 patient resamples, seed 2026, at k = 1, 2, 4 h. Run on the test split
from ~/run_test/repo. No definition, model or setting changes. AUC A and B must
reproduce RANK_REHEARSAL.txt (k=2: 0.863, 0.858).
