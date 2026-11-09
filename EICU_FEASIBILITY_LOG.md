# EICU_FEASIBILITY_LOG — outcome-blind checks before Registration 2a (2026-11-06)
## F1. Septic population (no outcomes, no vitals)
All ICU stays 200,859; adult first ICU stays 157,883. Sepsis by APACHE admission diagnosis 19,514; by diagnosis
table 22,768; both 16,416 (84% of APACHE). Hospitals with APACHE sepsis: 204.
Admit source (APACHE sepsis): emergency department 13,521 (69%); floor / acute care / step-down ~3,990 (20%);
direct admit / other hospital ~1,820 (9%); operating room / recovery / PACU 70 (<1%).
Source: pulmonary 7,385 (38%); renal/UTI 4,565 (23%); GI 2,391 (12%); unknown 2,225 (11%);
skin/soft tissue 1,657 (8%); other/gynaecological 1,303 (7%). Unit: Med-Surg ICU 13,034 (67%); MICU 2,518.
Note: APACHE sepsis = admitted because of sepsis; differs from MIMIC Sepsis-3; planned post-operative escalations rare.

## F2. Cast counts (counts only; adult first stays with APACHE sepsis, n=19,514)
Ajay 9,946; arrived on support 3,539; Naveen 2,479 (emergency department 1,626, other 853; pressor first 1,334,
vent first 990, both 155); died never escalated 1,125; Kranthi 1,020; Sundar 850; grey zone (3-5 h) 516;
Kranthi+Sundar 31; early planned 8.
Ventilation start source: respiratorycare and treatment 3,143; treatment only 1,655; respiratorycare only 809.
Flag: mixed route only 31 (MIMIC-III 562); ventilation timing across the two sources to be checked before freezing.

## F3. Charting (all septic stays together, first 24 h)
5-min vitals 98.9%; first vital after unit admission median 7 min (IQR 5-15); HR / RR / SpO2 ~11-12 per hour;
arterial pressure 15.9% of stays (median hospital 6.8%); cuff BP ~2.1 per hour; FiO2 charted in 41.8% (median 2 entries).
Hospitals with dense HR charting (>= 10/h): 188 of 204 (19,393 stays).

## F4. NEWS components and oxygen
GCS in first 24 h: 14,896 stays (76%), ~19 entries per stay. Oxygen labels (stays, first 24 h): FiO2 7,838;
LPM O2 4,723; SaO2 3,869; O2 Device 843; FIO2 (%) 324. Full NEWS mostly buildable; oxygen use partial.
