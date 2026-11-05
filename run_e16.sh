#!/bin/bash
for S in cal test; do
  if [ "$S" = cal ]; then DATA=~/run_prac/missh_data; else DATA=~/run_test/missh_data; fi
  rm -rf ~/run_e16_$S && mkdir -p ~/run_e16_$S
  cp -r ~/run_test/repo ~/run_e16_$S/repo
  cp -r "$DATA" ~/run_e16_$S/missh_data
  cp ~/missh_data/f1f3_hourly_$S.csv ~/run_e16_$S/missh_data/f1f3_hourly.csv
  cd ~/run_e16_$S/repo
  head -170 describe_80.py > e16_run.py
  sed "s/__SPLIT__/$S/" ~/missh/e16_tail.py >> e16_run.py
  if python3 e16_run.py > ~/e16_$S.log 2>&1; then
    cp E16_F1F3_$S.txt ~/missh/ && echo "E16 $S done"
  else
    echo "E16 $S FAILED: see ~/e16_$S.log"
  fi
done
echo "ALL E16 DONE"
