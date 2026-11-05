# Admissibility floors
Class R. No data contact.

## 1. Window floor -- 4 actual observations per channel
A pair is computable in a window only if BOTH channels have >= 4 actual
observations in that window. HR, RR, SpO2, MAP, and Temperature each >= 4.

NO CARRY-FORWARD. A missing observation is never filled with a previous value.
A pair failing this is UNANALYZABLE for that window -- not zero, not unchanged.

Rationale: linear detrending consumes 2 df, so 4 points leave 3 residual df --
the minimum at which a detrended correlation exists.

LIMITATION: at n=4, SE(z) = 1.0. A single window's rho is very imprecise and no
claim rests on it. Evidence comes from persistence ACROSS windows, not
precision WITHIN one.

## 2. Reference floor -- 12 observations spanning >= 3 hours
Both conditions per channel; whichever is satisfied later closes the block.
Count alone is insufficient because q15 observations are heavily
autocorrelated. Supersedes min_baseline_n = 8.

## 3. Pair floor -- F4 requires >= 4 admissible pairs
Below 4, F4 = UNANALYZABLE. F4's denominator is the admissible set, never a
fixed 6 or 10.

LIMITATION: 4 is a design choice protecting against F4 running on too little
geometry, NOT a validated physiological threshold.

## 4. Consequences accepted
- tau must be recalibrated; 0.745289 / 0.739094 were derived under fixed-six F4
- DP needs a rule for changing pair availability; same shape as treatment
  suspension and should share one specification
- S0 must be re-run; 0.027/patient-week and 31.1% coverage do not transfer

## 5. Standing conditions
Fixed before data contact, not revised after any result. No interpolation
anywhere. UNANALYZABLE windows and patients are counted and reported.
