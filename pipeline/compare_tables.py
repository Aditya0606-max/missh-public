# compare_tables.py — practice tables vs original calibration exports.
import pandas as pd
ORIG, PRAC = "/home/muppidiaditya/missh_data", "/home/muppidiaditya/run_prac/missh_data"
keys = {"vitals_hourly_cal.csv": ["stay_id", "hour_idx"], "vitals_hourly_cal_v2.csv": ["stay_id", "hour_idx"],
        "news_hourly_cal.csv": ["stay_id", "hour_idx"], "outcome_cal.csv": ["stay_id"],
        "esc_type_cal.csv": ["stay_id"], "bp_hourly_cal.csv": ["stay_id", "hour_idx"],
        "bolus_cal.csv": ["stay_id", "start_h"], "hyper_hourly_cal.csv": ["stay_id", "hour_idx"],
        "sed_hours_cal.csv": ["stay_id", "hour_idx"]}
ok = True
for f, k in keys.items():
    try:
        a = pd.read_csv(f"{ORIG}/{f}", low_memory=False); b = pd.read_csv(f"{PRAC}/{f}", low_memory=False)
    except FileNotFoundError as e:
        print(f"{f:28s} MISSING ({e.filename})"); ok = False; continue
    a = a.sort_values(list(a.columns)).reset_index(drop=True); b = b.sort_values(list(b.columns)).reset_index(drop=True)
    cols = [c for c in a.columns if c in b.columns]
    same = a.shape == b.shape and a[cols].round(6).astype(str).equals(b[cols].round(6).astype(str))
    print(f"{f:28s} rows orig {len(a):7d}  prac {len(b):7d}  {'IDENTICAL' if same else 'DIFFERENT'}")
    ok &= same
print("\nALL IDENTICAL" if ok else "\nSOME DIFFER — check before going on")
