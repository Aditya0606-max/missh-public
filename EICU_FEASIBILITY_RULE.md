Amendment A2 (2026-11-08, before running): also allowed before signing: (f) presence (not values) by cast, hour by hour from
admission to tip (<= 72 h), of FiO2 or oxygen-flow information, oxygen device, and GCS; minutes to first vital sign; share of
pre-tip hours with no FiO2/oxygen information (12-h carry-forward, as MIMIC-III). Purpose: full NEWS feasibility and the
pre-set breathing-fallback rule (fallback if pooled no-FiO2 share >= 40%). Label matching listed with counts.
A2 label fix (2026-11-08, after label listing, before hours pull): oxygen information also includes respiratorycharting labels
'O2 Device', 'Oxygen Delivery Method', 'Oxygen Flow Rate' (as device/flow presence). Labels only; no outcome or values seen.
F8 extended, by cast (median share of pre-tip hours): vitals 1.00 all; BP 0.94-1.00; GCS Ajay 0.10, Kranthi 0.13, Sundar 0.12,
mixed 0.13, Naveen 0.50; oxygen info Ajay 0.19, Kranthi 0.86, Sundar 0.33, mixed 0.87, Naveen 1.00.
Pooled no-FiO2: Ajay 0.57, Kranthi 0.41, Naveen 0.40, Sundar 0.54, mixed 0.22; all 0.56.
Caution: oxygen charting lopsided by cast (charting reflects clinical concern); GCS sparse.
Amendment A3 (2026-11-08, before running): F5 ventilation timing, counts and time differences only: source of earliest vent start
(respiratorycare vs treatment), their gap, earlier signs (ventilator settings in respiratorycharting; tube/ventilator charted as
oxygen device), and cast counts under official vs earliest-sign tip. No vital-sign values, no outcomes beyond cast definition.
Amendment A3 (2026-11-08, before running): F5 ventilation timing, counts and time differences only: source of earliest vent start
(respiratorycare vs treatment), their gap, earlier signs (ventilator settings in respiratorycharting; tube/ventilator charted as
oxygen device), and cast counts under official vs earliest-sign tip. No vital-sign values, no outcomes beyond cast definition.
Amendment A3 (2026-11-08, before running): F5 ventilation timing, counts and time differences only: source of earliest vent start
(respiratorycare vs treatment), their gap, earlier signs (ventilator settings in respiratorycharting; tube/ventilator charted as
oxygen device), and cast counts under official vs earliest-sign tip. No vital-sign values, no outcomes beyond cast definition.
Amendment A3 (2026-11-08, before running): F5 ventilation timing, counts and time differences only: source of earliest vent start
(respiratorycare vs treatment), their gap, earlier signs (ventilator settings in respiratorycharting; tube/ventilator charted as
oxygen device), and cast counts under official vs earliest-sign tip. No vital-sign values, no outcomes beyond cast definition.
F5b results: reclassifications mostly settings-only (likely NIV/HFNC). Ajay -> Sundar 395 (tube 20, settings 375);
Ajay -> Naveen 299 (tube 18, settings 281); Naveen -> excluded 227 (tube 50); Sundar -> Naveen 44 (tube 25); Kranthi -> mixed 27 (tube 10).
DECISION (before any outcome analysis): eICU tip = earliest of respiratorycare vent start, treatment mechanical ventilation,
tube/ventilator charted as O2 device (nursecharting O2 Admin Device or respiratorycharting O2 Device / Oxygen Delivery Method),
and first pressor. Ventilator settings alone NOT used (also present with NIV/HFNC). Matches MIMIC-III corrected tip.
Amendment A4 (2026-11-08, before running): final cast funnel under the F5b tip (earliest of respiratorycare vent start, treatment
mechanical ventilation, tube/ventilator charted as O2 device, first pressor). Every septic first stay in one row with reason;
total must equal the septic cohort. Counts only.
Final funnel (A4, new tip; counts only). Total 19514. Ajay 9905; Kranthi 993; Sundar 876; Naveen 2489; mixed 42;
arrived on support 3578; died without escalation 976; no tip with discharge status missing 140 (excluded; survival unknown);
grey zone 507; planned early escalation 8 (the previously unaccounted 8). Funnel closed.
Amendment A5 (2026-11-08, before running): oxygen mapping. Allowed: distinct oxygen device text with counts, and distributions of
'O2 L/%' and FiO2 values (pooled over the septic cohort, not by cast, not linked to outcomes). Purpose: map eICU oxygen records to
the MIMIC-III FiO2 table before setting lines.
