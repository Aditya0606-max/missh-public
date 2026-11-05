
### Baseline under missingness — CLOSED
min_baseline_n = 8. A patient whose 24h baseline holds fewer than 8 admissible
observations is UNANALYZABLE and excluded. No base_rho is manufactured.
Rationale: 8 is the floor below which a correlation estimate carries no usable
information. Above it, the architecture attempts a personal reference rather
than refusing, on the grounds that a degraded reference still beats no
monitoring in a ward where the alternative is nothing.
TRADE ACCEPTED AND STATED: at 40% loss the mean baseline holds ~14 observations,
so a floor of 8 excludes very few patients. Thin baselines therefore propagate
into the record rather than being caught at the door, and their noise surfaces
in the false-alert rate instead of the exclusion count. A higher floor (e.g. 12)
would move that cost from false alerts to coverage. This was chosen knowingly.
Exclusion rate and baseline-n distribution are both reported.

### DEFECT 2026-08-19 — coverage endpoint miscomputed, first S0 run void
First S0 run reported coverage 0.965 identically across complete-cadence and
40%-missing conditions. That is impossible: under clustered 40% loss most 6h
windows hold fewer than min_eff_n=5 observations and must be dropped.
Cause: `analyzable += 1` incremented before the min_eff_n check, counting
SCHEDULED windows rather than USABLE ones. 0.965 = 139/144, a fencepost
artifact independent of missingness.
This is a defect in the implementation of a pre-declared endpoint, NOT a
parameter change made after seeing results. No threshold, seed, sample size, or
pass criterion is altered. The counter is moved after the eligibility check and
the run is repeated at the same evaluation seed 20260819.
The first run's coverage figures are void. Its episode counts came from windows
that had passed the check and are unaffected, but the run is superseded whole
rather than partially retained.
