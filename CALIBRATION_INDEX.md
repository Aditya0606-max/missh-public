# Calibration index (MIMIC-III; not evidence)

Each check: its rule and recorded result are in `MIMIC3_COVERAGE_RULE.md` (search the check name); its script and printed output are listed here.

| Check | Script | Script first committed | Output |
| --- | --- | --- | --- |
| C10 | `c10_shapes.py` | e8491be 2026-11-07 | `calibration/c10_out.txt` |
| C10B | `c10b_paths.py` | 34d0fe8 2026-11-07 | `calibration/c10b_out.txt` |
| C10C | `c10c_rules.py` | 23a0db1 2026-11-07 | `calibration/c10c_out.txt` |
| C10D | `c10d_rules.py` | 05f3857 2026-11-07 | `calibration/c10d_out.txt` |
| C10E2 | `c10e2_lowfloor.py` | cc34d95 2026-11-07 | `calibration/c10e2_out.txt` |
| C10F | `c10f_bolus.py` | 5475a0e 2026-11-07 | `calibration/c10f_out.txt` |
| C10G | `c10g_silent.py` | 07e2d92 2026-11-07 | `calibration/c10g_out.txt` |
| C10H | `c10h_fade.py` | 07e2d92 2026-11-07 | `calibration/c10h_out.txt` |
| C10I | `c10i_road.py` | 83963d0 2026-11-07 | `calibration/c10i_out.txt` |
| C10K | `c10k_band.py` | ea54b5e 2026-11-07 | `calibration/c10k_out.txt` |
| C10L | `c10l_fair.py` | d48dc09 2026-11-07 | `calibration/c10l_out.txt` |
| C12V2 | `c12v2_extract.py` | 4bf75fd 2026-11-07 | private (contains record names), `calibration/c12v2_extract_out.txt`, `calibration/c12v2_out.txt` |
| C12V2 | `c12v2_read.py` | 16d9ce8 2026-11-07 | private (contains record names), `calibration/c12v2_extract_out.txt`, `calibration/c12v2_out.txt` |
| C14 | `c14_replay.py` | 316dcd6 2026-11-07 | `calibration/c14_out.txt` |
| C14B | `c14b_budget.py` | 6390b14 2026-11-07 | `calibration/c14b_out.txt` |
| C14C | `c14c_ward.py` | 4b8ab5d 2026-11-08 | `calibration/c14c_out.txt` |
| C14D | `c14d_combo.py` | 419bc80 2026-11-08 | `calibration/c14d_out.txt` |
| C14F | `c14f_timeline.py` | a43ac9f 2026-11-08 | `calibration/c14f_out.txt` |
| C14G2 | `c14g2_rise.py` | 1800fdb 2026-11-08 | `calibration/c14g2_out.txt` |
| C14G | `c14g_slip.py` | e65b911 2026-11-08 | `calibration/c14g_out.txt` |
| C14H2 | `c14h2_arrival.py` | 9e12bc1 2026-11-08 | `calibration/c14h2_out.txt` |
| C14H3 | `c14h3_comeback.py` | 71f5750 2026-11-08 | `calibration/c14h3_out.txt` |
| C14H | `c14h_naveen.py` | 8de9291 2026-11-08 | `calibration/c14h_out.txt` |
| C14IJ | `c14ij_flutter.py` | 172f332 2026-11-08 | `calibration/c14ij_out.txt` |
| C15 | `c15_ecg_extract.py` | 7561a41 2026-11-07 | `calibration/c15_extract_out.txt`, `calibration/c15_hrv_numerics_out.txt`, `calibration/c15_out.txt` |
| C15 | `c15_hrv_numerics.py` | 7561a41 2026-11-07 | `calibration/c15_extract_out.txt`, `calibration/c15_hrv_numerics_out.txt`, `calibration/c15_out.txt` |
| C15 | `c15_read.py` | a0e48cc 2026-11-07 | `calibration/c15_extract_out.txt`, `calibration/c15_hrv_numerics_out.txt`, `calibration/c15_out.txt` |
| C16 | `c16_breath.py` | de50359 2026-11-08 | `calibration/c16_out.txt` |
| C16B | `c16b_checks.py` | 4a0e2c5 2026-11-08 | `calibration/c16b_out.txt` |
| C16C | `c16c_ward.py` | 1c6b4d6 2026-11-08 | `calibration/c16c_out.txt` |
| C16D | `c16d_lead.py` | ff737ee 2026-11-08 | `calibration/c16d_out.txt` |
| C16E | `c16e_wardpace.py` | 70edc8c 2026-11-08 | `calibration/c16e_out.txt` |
| C16F | `c16f_own.py` | aa38e14 2026-11-08 | `calibration/c16f_out.txt` |
| C16G | `c16g_effort.py` | 8610932 2026-11-08 | `calibration/c16g_out.txt` |
| C16H2 | `c16h2_news.py` | 17b17bf 2026-11-08 | `calibration/c16h2_out.txt` |
| C16H | `c16h_vent.py` | 10d22f6 2026-11-08 | `calibration/c16h_out.txt` |
| C16I | `c16i_fallback.py` | 3b8610b 2026-11-08 | `calibration/c16i_out.txt` |
| C17 | `c17_ward.py` | 5f257e1 2026-11-08 | `calibration/c17_out.txt` |
| C18 | `c18_red.py` | 87d7664 2026-11-08 | `calibration/c18_out.txt` |
| C18B | `c18b_agree.py` | 291d5bf 2026-11-08 | `calibration/c18b_out.txt` |
| C19 | `c19_paths.py` | f4eb60c 2026-11-08 | `calibration/c19_out.txt` |
| C1 | `c1_charting.py` | e818de2 2026-11-07 | `calibration/c1_out.txt` |
| C20 | `c20_guardian.py` | 7281391 2026-11-08 | `calibration/c20_out.txt` |
| C21 | `c21_treat.py` | f0254a7 2026-11-09 | `calibration/c21_out.txt` |
| C22 | `c22_ajay.py` | 12a677e 2026-11-08 | `calibration/c22_out.txt` |
| C23 | `c23_era.py` | c4719a3 2026-11-08 | `calibration/c23_out.txt` |
| C24 | `c24_lines.py` | c060833 2026-11-09 | `calibration/c24_out.txt` |
| C24B | `c24b_search.py` | e1b18b4 2026-11-09 | `calibration/c24b_out.txt` |
| C24C | `c24c_freeze.py` | db9da63 2026-11-09 | `calibration/c24c_out.txt` |
| C24D | `c24d_sundar.py` | 47c1727 2026-11-09 | `calibration/c24d_out.txt` |
| C25 | `c25_rehearsal.py` | 8b7c1c1 2026-11-09 | `calibration/c25_out.txt` |
| C2 | `c2_ledger.py` | 312eb01 2026-11-07 | `calibration/c2_out.txt` |
