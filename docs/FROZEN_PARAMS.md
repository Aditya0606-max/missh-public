# FROZEN PARAMETERS — do not modify after this commit.
# Date: 2026-08-19

TAU = 0.745289
  95th percentile of F4_scalar over 278,000 analyzable windows from 2,000
  stable patient-weeks, development seed 20260807, episode search from i0=b.
  Null: mean 0.4541, median 0.4390, p90 0.6758, p99 0.8688.

  Comparison: with baseline-overlapping windows included (i0=0), tau was
  0.739094 over 326,000 windows. Excluding them raised tau by 0.8%. The
  self-reference effect was real but small; the exclusion is justified on
  principle, not magnitude.

GATE1_K (OCRI) = 1.0     G2_DP = 0.50     G2_AXES = 2
G_MAX = 3 hours          PERSISTENCE = 3 consecutive windows
BASELINE_HOURS = 24      (inherited from forcelab2, NOT derived — open item)
