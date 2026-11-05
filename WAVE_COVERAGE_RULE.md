# WAVE_COVERAGE_RULE — written before viewing per-patient coverage (2026-11-04)
Purpose: decide which waveform patients are usable for a valley (recovery-from-dips)
comparison. Practice/pilot use only; not a confirmatory test.
Deteriorating: recorded hours before esc_h
  >= 6 h  usable (early window -6 to -4 h, late window -2 to 0 h)
  4-6 h   usable with caution (windows -4 to -2 and -2 to 0, back to back)
  < 4 h   not usable; listed, not measured
Each window needs signal present in >= 80% of its minutes.
Record which signals exist per patient (ECG/HR, pleth/SpO2, resp, arterial BP).
Stable: same windows at matched clock hours.
