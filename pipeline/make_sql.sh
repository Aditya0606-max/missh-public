#!/bin/bash
# make_sql.sh SPLIT SUFFIX — rewrite committed SQL for a split and table suffix.
set -e
SPLIT=$1; SUF=$2
OUT=~/missh/pipeline/sql_${SUF}
mkdir -p "$OUT"
for f in vitals_01 vitals_02 news_01 outcome_01 esc_type_01 bp_01 bolus_01 hyper_01 sedation_01 age_01; do
  sed -e "s/_cal_v2/_${SUF}_v2/g" \
      -e "s/_cal\b/_${SUF}/g" \
      -e "s/sp.split = 'calibration'/sp.split = '${SPLIT}'/g" \
      ~/missh/${f}.sql > "$OUT/${f}.sql"
done
if grep -nE "missh\.[a-z_]*_cal([_\`]|\b)" "$OUT"/*.sql; then echo "WARNING: calibration table name left (above)"; else echo "OK: no calibration table names left"; fi
grep -h "CREATE TABLE" "$OUT"/*.sql
grep -h "sp.split" "$OUT"/*.sql | sort -u
