#!/bin/bash
# compare_results.sh SUFFIX — compare practice results with the originals.
R=~/run_$1/repo
for f in RULER_COUNTS_V3.txt ANCHOR_COUNTS_V2.txt SUMMARY_P1.txt SUMMARY_P1_K0.txt SUMMARY_P2.txt \
         SUMMARY_P3.txt SUMMARY_PP.txt SUMMARY_E13.txt RANK_REHEARSAL.txt P7_REHEARSAL.txt CONJUNCTION.txt \
         COSINE_TRAJECTORY.txt COS_LONG.txt MOVERS.txt BOLUS_RESPONSE.txt FAST_80_RESULTS.txt; do
  if [ ! -f "$R/$f" ]; then echo "MISSING   $f"; continue; fi
  if [ ! -f ~/missh/$f ]; then echo "NEW ONLY  $f (no original to compare)"; continue; fi
  if diff -q ~/missh/$f "$R/$f" > /dev/null; then echo "SAME      $f"; else echo "DIFFERENT $f"; fi
done
