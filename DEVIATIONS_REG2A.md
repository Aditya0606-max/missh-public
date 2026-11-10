# Registration 2a: deviations (written 9-10 Nov 2026, before the eICU results were read in full)

All times CST (UTC-6), 9 Nov 2026.

D1. Order of steps. The signed registration PDF (SHA-256 7452a0bb49d525258142294c51adcec2c993024166d3efabd6e6872d488e42d7) and the
frozen eICU pipeline were committed privately at 22:48 (c58b837, tag reg2a-signed) and publicly at 22:51 (d5d1cad, tag reg2a-signed).
The eICU run took place at 23:23-23:27, after both, but before the OSF registration. The OSF registration archives the same PDF.

D2. Code executed. eicu_run.py was identical to the public copy at d5d1cad (SHA-256 297f8c57...2ea9). It runs c25_rehearsal.py, which
was identical to the signed private commit c58b837 (SHA-256 50781c8d...d3db). The public copy of c25_rehearsal.py at that time dated
from 04:37 and did not yet include the paired-timing and precision reports (added 22:30, private commits 482d72a and 8de5028).
These reports were therefore fixed before the run (privately, in the signed commit) and published afterwards.

D3. Missing pre-set sub-report. The registration lists paired timing for the ventilation-first group by hospital oxygen-charting
band. This was not implemented in the executed code and was not produced. If computed later, it is labelled post hoc.

D4. OSF_REGISTRATION.txt (committed 23:13) held a placeholder ("OSFLINK"), not a registration; it is corrected once OSF is done.

The eICU output is frozen unedited as EICU_RESULTS.txt (SHA-256 d8daafa44e9952773550c84a592bfc0d8dce196500d17c603ab83bc4c683f0f5,
commit d93a975, tag reg2a-results). No code, line, threshold or definition was changed after the run.
