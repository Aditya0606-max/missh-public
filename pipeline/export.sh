#!/bin/bash
# export.sh SUFFIX — export tables to ~/run_SUFFIX/missh_data with the file names scripts expect.
set -e
SUF=$1; P=project-688c444c-3632-4faa-a13.missh; D=~/run_${SUF}/missh_data
mkdir -p "$D"
q() { bq --quiet query --use_legacy_sql=false --format=csv --max_rows=3000000 "$1" > "$D/$2"; echo "$2: $(wc -l < "$D/$2")"; }
q "SELECT * FROM \`$P.vitals_hourly_${SUF}\` ORDER BY stay_id, hour_idx" vitals_hourly_cal.csv
q "SELECT * FROM \`$P.vitals_hourly_${SUF}_v2\` ORDER BY stay_id, hour_idx" vitals_hourly_cal_v2.csv
q "SELECT stay_id, hour_idx, news, n_items FROM \`$P.news_hourly_${SUF}\` ORDER BY stay_id, hour_idx" news_hourly_cal.csv
q "SELECT * FROM \`$P.outcome_${SUF}\` ORDER BY stay_id" outcome_cal.csv
q "SELECT * FROM \`$P.esc_type_${SUF}\` ORDER BY stay_id" esc_type_cal.csv
q "SELECT * FROM \`$P.bp_hourly_${SUF}\` ORDER BY stay_id, hour_idx" bp_hourly_cal.csv
q "SELECT * FROM \`$P.bolus_${SUF}\` ORDER BY stay_id, start_h" bolus_cal.csv
q "SELECT * FROM \`$P.hyper_hourly_${SUF}\` ORDER BY stay_id, hour_idx" hyper_hourly_cal.csv
q "SELECT * FROM \`$P.sed_hours_${SUF}\` ORDER BY stay_id, hour_idx" sed_hours_cal.csv
q "SELECT * FROM \`$P.age_${SUF}\` ORDER BY stay_id" age_cal.csv
