# ROUTE_OF_MISSED — exploratory, written before running (2026-11-06)
Question: among Registration 1's deteriorating test-split patients (80%), what share were
ventilator-first (Sundar), pressor-first (Kranthi) or both, among those the alarm missed
vs caught? Not identical to the calibration "~94% compensating" figure; labelled "missed by alarm".
Source: describe_80.py re-run as a private copy (outputs to ~/missh_data/d80_ids/, patient ID kept);
Registration 1 result files untouched. Check: the copy's per-patient file, without IDs,
must equal results_80/DESCRIBE_PER_PATIENT.csv.
Missed = main_cat "never" (primary alarm) and, separately, sens_cat "never" (sensitivity-first).
Route = first_type from ~/missh_data/esc_type.csv (vent / pressor / both), joined on stay_id;
unmatched reported. Also split by anchor_type (NEWS vs event) and tier.

## Result (run 2026-11-06)
Copy matched results_80/DESCRIBE_PER_PATIENT.csv exactly (2,685 deteriorating test-split patients).
Route: Sundar (vent first) 1,648 (61.4%); Kranthi (pressor first) 843 (31.4%); both 89 (3.3%);
no route match 105 (3.9%).
Primary alarm caught 14 (Kranthi 4, Sundar 9, both 1).
Sensitivity alarm never caught before anchor: Kranthi 82.0%, Sundar 82.2%, both 87.6%,
no route match 64.8%. Route mix of missed vs caught nearly identical (Sundar 61.8% vs 59.5%).
Reading: Registration 1 missed Kranthis as often as Sundars. Sundars dominated the missed
because they dominated the cohort, not because they were missed more. Route blindness was not
the main cause of the null; coarse, late, origin-relative measurement missed both routes.

## Result (run 2026-11-06)
Copy matched results_80/DESCRIBE_PER_PATIENT.csv exactly (2,685 deteriorating test-split patients).
Route: Sundar (vent first) 1,648 (61.4%); Kranthi (pressor first) 843 (31.4%); both 89 (3.3%);
no route match 105 (3.9%).
Primary alarm caught 14 (Kranthi 4, Sundar 9, both 1).
Sensitivity alarm never caught before anchor: Kranthi 82.0%, Sundar 82.2%, both 87.6%,
no route match 64.8%. Route mix of missed vs caught nearly identical (Sundar 61.8% vs 59.5%).
Reading: Registration 1 missed Kranthis as often as Sundars. Sundars dominated the missed
because they dominated the cohort, not because they were missed more. Route blindness was not
the main cause of the null; coarse, late, origin-relative measurement missed both routes.
