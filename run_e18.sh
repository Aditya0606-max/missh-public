#!/bin/bash
for S in cal test; do
  if [ "$S" = cal ]; then DATA=~/run_prac/missh_data; else DATA=~/run_test/missh_data; fi
  rm -rf ~/run_e18_$S && mkdir -p ~/run_e18_$S
  cp -r ~/run_test/repo ~/run_e18_$S/repo
  cp -r "$DATA" ~/run_e18_$S/missh_data
  cd ~/run_e18_$S/repo
  head -170 describe_80.py > e18_run.py
  sed "s/__SPLIT__/$S/" ~/missh/e18_tail.py >> e18_run.py
  if python3 e18_run.py > ~/e18_$S.log 2>&1; then
    cp E18_EARLY_RULER_$S.txt ~/missh/ && echo "E18 $S done"
  else
    echo "E18 $S FAILED: see ~/e18_$S.log"
  fi
done
echo "ALL E18 DONE"
