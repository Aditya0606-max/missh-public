#!/bin/bash
# run_sql.sh SUFFIX — run generated SQL in dependency order.
set -e
SUF=$1; D=~/missh/pipeline/sql_${SUF}
for f in vitals_01 vitals_02 news_01 outcome_01 esc_type_01 bp_01 bolus_01 hyper_01 sedation_01 age_01; do
  echo "== $f"; bq query --use_legacy_sql=false < "$D/${f}.sql"
done
