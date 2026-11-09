# Pre-freeze controls (MIMIC-III only; eICU untouched)

C1 Charting: readings/hour per channel, per character, cuff vs arterial. FLAG if any group differs from Ajay by >=25%.
C2 Treatment ledger: share of recoveries with a bolus/O2 step/other treatment in the prior hour, per character. FLAG if >50% of Ajay returns follow treatment.
C3 Positive control: current no-return combination at the tip, Kranthi vs Ajay, Sundar vs Ajay. FLAG if AUC < 0.65.
C4 Blind-spot rehearsal: misses at 2 h before tip, binned: no readings / cuff-only sparse / witness absent / treatment masked / no sign. FLAG if one bin holds >50% of misses.

Order: C1, C2, C3, C4. Results recorded in CONTROLS_RESULTS.md, not used to move any line already committed.
