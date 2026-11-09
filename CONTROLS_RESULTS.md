# C1 Charting (MIMIC-III, c1_charting.py, c1b_mixed.py, c1c_rows.py)
- Share of watched hours with vitals: Ajay 0.86, Kranthi 0.80 (0.93x), Sundar 0.71 (0.83x), mixed 0.41 (0.48x).
- FLAG: mixed (Kranthi+Sundar). Cause is charting, not extraction: ~half their hours have no chart entry at all.
- Not flagged: Kranthi, Sundar. Deteriorating patients charted LESS than Ajay, not more: no attention inflation.
- All groups: last 1-2 h before tip (or pseudo-tip) often uncharted (~44-54% of stays); readings at tip-2 h often carried forward.
- Action: mixed reported descriptively and binned in C4; C3/C4 to record whether a fresh reading existed at each check time.

# C2 Treatment ledger (MIMIC-III, c2_ledger.py, m3_bolus.sql, c2b_o2_coverage.py)
- Shock-side recoveries after a bolus (prior/same hour): Ajay 0.11 (n=6796), Kranthi 0.17, Sundar 0.09, mixed 0.10. PASS.
- Breathing-side recoveries after an O2 increase: Ajay 0.07 (n=6644), Sundar 0.12. PASS on available data.
- O2 records exist for Ajay 4867/5093, Sundar 945/1294, Kranthi 0/475, mixed 0/562: extraction gap.
  Breathing-side C2 for Kranthi and mixed is BLANK, not zero. Re-extract O2 for all groups before C3/C4.
- Recoveries counted hour-to-hour across fixed lines; many may be threshold wobble. Supports sustained re-arm.
- Not covered: treatment >1 h earlier, infusions, antibiotics, device changes without a flow value.
- C2 rerun with m3_o2_events_all.csv (O2 now for Ajay 5008, Kranthi 470, Sundar 1285, mixed 561 stays):
  breathing-side recoveries after O2 increase: Ajay 0.07, Kranthi 0.11, Sundar 0.16, mixed 0.12. PASS.
  Shock side unchanged. Deteriorating patients' returns slightly more treatment-linked than Ajay's (Kranthi shock 0.17, Sundar breathing 0.16).
  Note for rule: a return within 1 h of a bolus/O2 step = weaker evidence of reserve than an untreated return.
