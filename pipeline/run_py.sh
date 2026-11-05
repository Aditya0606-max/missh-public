#!/bin/bash
# run_py.sh SUFFIX — copy scripts + frozen files to ~/run_SUFFIX/repo and run in order.
set -e
SUF=$1; R=~/run_${SUF}/repo
rm -rf "$R"; mkdir -p "$R"
cp ~/missh/*.py "$R"/
cp ~/missh/FLAG_FROZEN.json ~/missh/FLAG_SENS_FROZEN.json ~/missh/COMBINED_FROZEN.json ~/missh/FAST_REFS.json "$R"/
cd "$R"
STEPS="rulers_03 anchors_02 measure_p1 measure_p1_k0 measure_p2 measure_p3 measure_pp series_p1 \
measure_p1_traj measure_p3_traj measure_pp_traj \
summarize_p1 summarize_p1_k0 summarize_p2 summarize_p3 summarize_pp \
rank_01 p7_01 fast_80 conjunction_01 cosine_traj_01 cos_long_01 movers_01 bolus_01 measure_e13 summarize_e13 describe_80"
for s in $STEPS; do
  echo "== $s  $(date +%H:%M:%S)"
  python3 "$s.py" > "log_$s.txt" 2>&1 || { echo "FAILED: $s (see $R/log_$s.txt)"; exit 1; }
done
echo "ALL STEPS DONE $(date +%H:%M:%S)"
