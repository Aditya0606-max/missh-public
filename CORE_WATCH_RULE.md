# CORE_WATCH_RULE — waveform pilot, written before viewing (2026-11-04)
Patients: MIMIC-IV waveform v0.1.0 records overlapping the cohort ICU stay;
labels escalated / escalated_hyperacute / escalated_after_72h / stable.
State: HR, RR, SpO2 (no MAP axis; cuff only). Worsening direction (+1,+1,-1)/sqrt3.
Blocks: 15-min medians. Origin ruler: first 8 consecutive blocks (2 h) with >= 7
complete; mean and SD per channel, SD floor 1 unit.
Watch: Dw and last-hour step cosine at +2, +4, +6, +8, +10 h after the ruler closes.
Groups by recording start vs esc_h: A >= 4 h before; A2 1-4 h before; B within 1 h;
C > 1 h after; D stable. Groups reported separately, never pooled.
Descriptive pilot only: no thresholds tuned, no claims.
