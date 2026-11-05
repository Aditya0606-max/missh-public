**Miss H × VEVFM**

**Track A Confirmatory Pre-Registration**

*Signed Four-Force Ordering Dissociation --- MIMIC-IV*

  ------------------- ---------------------------------------------------
  **Field**           **Value**

  Author              Aditya Muppidi

  Document version    v1.0

  Date drafted        28 July 2026

  Supersedes          Five-force basis (F1, F2a, F2b, F3, F4). F2a and
                      F2b are collapsed into a single F2 for Track A.

  Dataset             MIMIC-IV via BigQuery. PhysioNet credentialed; DUA
                      signed 30 June 2026.

  Scope               Track A only --- charted vitals at ward/CCU
                      cadence. Track B (waveform) is out of scope and
                      firewalled (Part VIII).

  Status              DRAFT --- not in force until Part 0 is completed
                      and signed.
  ------------------- ---------------------------------------------------

**PART 0 --- LOCK DECLARATION AND SIGNATURE**

This document is a pre-registration. Its only function is to commit, in
advance and in writing, to predictions that the confirmatory dataset is
then permitted to falsify. It has force only if signed before any
confirmatory cohort is extracted.

**Declaration**

At the time of signature, the author declares that no record from either
confirmatory cohort has been extracted, inspected, plotted, or
summarised; that no parameter in Part III has been selected by reference
to any confirmatory outcome; and that the pre-analysis diagnostics
permitted under Part X have been run only on the fields and cohorts
named there.

**Blocking conditions --- this document cannot be signed until both are
closed**

B1. The cardiac event anchor is pinned by itemid in MIMIC-IV inputevents
and procedureevents. Until the anchor exists, Arm B has no ground-truth
endpoint, no lead time is measurable, and the dissociation is not
statable.

**UNLOCKED FIELD ---** B1 --- cardiac anchor itemid set (vasopressor /
MCS), with table of origin:
**\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_**

B2. Every unlocked field in Part III and Part V carries a committed
value. An unlocked threshold is a degree of freedom, and a
pre-registration with a free parameter in it is not a pre-registration.

**Signature**

**UNLOCKED FIELD ---** Signed:
**\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_**

**UNLOCKED FIELD ---** Date and time of signature:
**\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_**

**UNLOCKED FIELD ---** Hash / commit reference of this document at
signature:
**\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_**

**PART I --- ARCHITECTURE UNDER TEST**

**I.1 Inference chain**

**X(t) → V(t) → F(t) → R(t) → label**

  ----------- ------------------ ---------------------------------------------
  **Layer**   **Object**         **Definition**

  X(t)        Charted signal     HR, MAP, RR, SpO₂ as recorded in chartevents.
                                 Clinical units, native charting cadence.

  V(t)        BRI-referenced     Displacement from the patient's own admission
              state vector       baseline, in units of that patient's own
                                 dispersion. Dimensionless. Never
                                 population-referenced.

  F(t)        Force vector       Projection of V onto the four-force basis
                                 (Part I.2).

  R(t)        Dominant regime    Which force or force pair is loading at time
                                 t, and in what order.

  label       Syndromic name     Output only. Never an input at any stage.
  ----------- ------------------ ---------------------------------------------

*The one-way property is an architectural commitment, not notation. If
the syndromic label informs F or R at any point, the engine is a
classifier wearing geometry and the dissociation result is circular.*

**I.2 The four forces**

Formally one object: the Jacobian of dL/dt = f(L, u). Input map → F1;
diagonal → F2; forcing magnitude → F3; off-diagonal → F4. No residual
term, which is what makes this a basis rather than a list.

  ------------------- ------------------ ---------------------------------
  **Force**           **Constraint       **Charted read**
                      violated**         

  F1 ---              Delivery-space     Narrowing pulse pressure,
  transport-access    integrity          intravascular escape,
  failure                                forward-output failure

  F2 ---              Return to          Lengthening return time,
  return-capacity     operating point    incomplete return, baseline drift
  failure             after perturbation 

  F3 ---              Driving /          Lactate rising against stable
  energy-generation   actuation capacity MAP, contractile failure,
  insufficiency                          respiratory muscle fatigue

  F4 ---              Cross-scale        Off-diagonal correlation
  coupling-fidelity   coordination       structure, per pair and signed
  loss                                   
  ------------------- ------------------ ---------------------------------

**F2a / F2b collapse.**

The prior basis separated restoring-force degradation (F2a) from
adaptive-range collapse (F2b). No instrument at charted-vitals
resolution separates band width from return rate. F2b is therefore
removed from the Track A basis and retained as a Track B hypothesis with
its own signed prediction (gain collapse with preserved λ), which is not
eligible to rescue any Track A result.

**I.3 Detection layer and attribution layer**

These are distinct and run on different retentions of the same
computation. Conflating them is the failure mode this section exists to
prevent.

  ------------------ ------------------------- ---------------------------
  **Layer**          **Instrument**            **Property**

  Detection (three   Mean absolute             Sign-agnostic.
  gates)             off-diagonal correlation, Condition-agnostic.
                     referenced to personal    Measures magnitude of
                     baseline                  departure from the
                                               patient's own coordination
                                               structure.

  Attribution (F4)   The full pairwise         Sign-bearing. The mean
                     off-diagonal vector,      scalar cannot carry an F4
                     retained per pair with    claim: it dilutes localised
                     sign                      decoupling and discards
                                               direction.
  ------------------ ------------------------- ---------------------------

**I.4 Three-gate cascade**

  ------------- --------------------------- ------------------------------
  **Gate**      **Test**                    **What it excludes**

  Gate 1 ---    Departure from the          Patients who have not moved
  OCRI          patient's own baseline      from their own admission state
                exceeds threshold           

  Gate 2 --- DP Directional persistence     Oscillation,
                positive on ≥ 2 axes        single-observation spikes,
                                            non-committed motion

  Gate 3 --- Ω  Departure from the          Physiologically appropriate
                patient's normal operating  compensation
                regime in either direction  
                (too rigid or too           
                unstable), and not the      
                compensation pattern        
  ------------- --------------------------- ------------------------------

Gate returns are three-valued: STABLE, DRIFTING, UNDEFINED. UNDEFINED
propagates; it never defaults to negative. A gate that cannot be
evaluated for want of data is not evidence of stability.

**PART II --- COHORTS**

**II.1 Arms**

  -------------- ---------------------------- ----------------------------
                 **Arm A --- primary**        **Arm B --- secondary**

  Phenotype      Sepsis-AKI                   Cardiogenic shock

  Role           Statistical anchor; fully    Generalisation arm;
                 powered                      identical untuned engine

  Predicted      F1 + F4 dominant             F2 + F3 dominant
  loading                                     

  Typical        Ward / MICU, coarser         CCU, finer charting
  setting        charting                     

  Anchor         UNLOCKED --- see II.2        UNLOCKED --- blocked on B1
  -------------- ---------------------------- ----------------------------

**II.2 Anchor definitions**

**UNLOCKED FIELD ---** Arm A anchor --- event definition and itemid /
criteria set:
**\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_**

**UNLOCKED FIELD ---** Arm B anchor --- vasopressor initiation itemids
(inputevents):
**\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_**

**UNLOCKED FIELD ---** Arm B anchor --- mechanical circulatory support
itemids (procedureevents):
**\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_**

**UNLOCKED FIELD ---** Anchor tie-breaking rule where multiple
qualifying events occur:
**\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_**

The anchor is the only ground truth in this study. Lead time, gate
performance, and force ordering are all measured against it. It is
defined once, identically in structure across arms, and not revised
after signature.

**II.3 Pre-registered exclusions for phenotype purity**

Exclusions are stated in advance and reported with counts. Post hoc
exclusion is the most common route by which a null becomes a positive.

Mandatory exclusions

--- Patients meeting criteria for both arms (mixed septic-cardiogenic
presentation).

--- Anticholinergic exposure and cardiac pacing during the observation
window (these are exclusions, not covariates --- they abolish the
observable rather than bias it).

--- Cardiac arrest as an index event: the ±10-minute anchor jitter
against a seconds-to-minutes event window makes ordering unmeasurable,
and the withdrawal-of-care population contaminates the cohort.

--- Admissions with insufficient pre-anchor record to establish a BRI
baseline (see II.4).

Mandatory covariates (not exclusions)

--- Pharmacologically active drug exposure, beta blockade in particular.
Beta blockade biases exactly the arm in which blunted return is the
predicted signal, so it is a required covariate rather than an optional
one.

--- Sedation exposure.

--- Charting density (see Part VII).

**II.4 Analyzability preconditions**

Applied identically to both arms, before any outcome is computed, with
exclusion rates reported per arm.

**UNLOCKED FIELD ---** Minimum baseline duration required before BRI is
considered established:
**\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_**

**UNLOCKED FIELD ---** Temporal floor --- minimum charting cadence below
which a record is not analyzable:
**\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_**

**UNLOCKED FIELD ---** Minimum effective sample count per correlation
window:
**\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_**

**UNLOCKED FIELD ---** Maximum permitted carry-forward fraction per
axis:
**\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_**

**PART III --- LOCKED PARAMETER SET**

**One parameter set. Identical across both arms. No arm-conditional
values. The absence of arm-conditional parameters is the condition under
which the dissociation means anything at all; if any value below differs
by arm, the primary claim is void.**

**III.1 Window and cadence**

**UNLOCKED FIELD ---** Correlation window length (single value, both
arms):
**\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_**

**UNLOCKED FIELD ---** Window step / stride:
**\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_**

**UNLOCKED FIELD ---** Observation grid definition (fixed, identical
across arms):
**\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_**

**UNLOCKED FIELD ---** Concurrency tolerance for treating charted values
as simultaneous:
**\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_**

DP is computed only on observed charttimes. No interpolation, no forward
fill, no resampling onto a synthetic grid. Forward-filled values are not
observations and generate directional persistence that does not exist.

**III.2 Baseline and adaptation**

**UNLOCKED FIELD ---** λ₁ --- cadence adaptation constant (noted as
inert at hourly charting; value still committed):
**\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_**

**UNLOCKED FIELD ---** λ₂ --- OCRI EWMA forgetting factor:
**\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_**

**UNLOCKED FIELD ---** λ₃ --- BRI component learning rate, with its
three triggers enumerated:
**\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_**

**UNLOCKED FIELD ---** Cold-start duration before any gate is permitted
to fire:
**\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_**

**III.3 Gate thresholds**

**UNLOCKED FIELD ---** Gate 1 --- OCRI threshold:
**\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_**

**UNLOCKED FIELD ---** Gate 2 --- DP threshold and minimum number of
axes:
**\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_**

**UNLOCKED FIELD ---** Gate 3 --- Ω regime-departure threshold:
**\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_**

**UNLOCKED FIELD ---** Gate 3 --- compensation-template definition,
including the coupling-sign condition (see VII.1):
**\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_**

**PART IV --- SIGNED PREDICTION TABLE**

**This is the substance of the pre-registration. Each cell commits a
sign and an onset rank before any confirmatory record is seen. Presence
or absence of a force is not the claim --- ordering and sign are.**

**IV.1 Arm A --- sepsis-AKI**

  ------------------- ------------------ ------------- --------------- ---------------
  **Force**           **Predicted sign** **Predicted   **Statistic**   **Threshold**
                                         onset rank**                  

  F1 transport-access Loading, early     1st or 2nd    UNLOCKED        UNLOCKED

  F2 return-capacity  Weak / late        3rd or 4th    UNLOCKED        UNLOCKED

  F3                  Preserved early,   3rd or 4th    UNLOCKED        UNLOCKED
  energy-generation   degrading late                                   

  F4                  LOOSENING ---      1st or 2nd    Per-pair signed UNLOCKED
  coupling-fidelity   per-pair                         off-diagonal,   
                      off-diagonal falls               not the mean    
                                                       scalar          
  ------------------- ------------------ ------------- --------------- ---------------

**IV.2 Arm B --- cardiogenic shock**

  ------------------- ------------------ ------------- --------------- ---------------
  **Force**           **Predicted sign** **Predicted   **Statistic**   **Threshold**
                                         onset rank**                  

  F1 transport-access Weak / late        3rd or 4th    UNLOCKED        UNLOCKED

  F2 return-capacity  Loading, early     1st or 2nd    UNLOCKED        UNLOCKED

  F3                  Insufficiency      1st or 2nd    UNLOCKED        UNLOCKED
  energy-generation   dominant early                                   

  F4                  TIGHTENING, then   3rd or 4th    Per-pair signed UNLOCKED
  coupling-fidelity   inverting ---                    off-diagonal,   
                      compensatory                     not the mean    
                      HR--MAP locking                  scalar          
                      before failure                                   
  ------------------- ------------------ ------------- --------------- ---------------

**IV.3 Why F4 must be per-pair and signed**

The two arms are predicted to move F4 in opposite directions. A shared
driver such as fever can raise the aggregate coordination scalar while
coupling fidelity is falling, so an aggregate magnitude cannot express,
and cannot falsify, the F4 claim. Each F4 prediction is therefore stated
per channel pair with a committed sign.

**UNLOCKED FIELD ---** Per-pair F4 predictions, Arm A --- six pairs,
each signed:
**\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_**

**UNLOCKED FIELD ---** Per-pair F4 predictions, Arm B --- six pairs,
each signed:
**\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_**

**PART V --- PRIMARY CLAIM**

**Claim.**

Under one locked parameter set, with no arm-conditional tuning, the
dominant force ordering in Arm A is the reverse of the dominant force
ordering in Arm B. Specifically: Arm A loads F1 + F4 in the first two
ranks; Arm B loads F2 + F3 in the first two ranks.

**What is adjudicated.**

Signed ordering, and nothing else. Not severity. Not dimensional
collapse. Not alarm performance. Not lead time as a primary endpoint.

**Test and effect size.**

**UNLOCKED FIELD ---** Statistic used to establish force ordering within
a patient:
**\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_**

**UNLOCKED FIELD ---** Statistic used to compare orderings across arms:
**\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_**

**UNLOCKED FIELD ---** Minimum effect size counted as a positive result:
**\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_**

**UNLOCKED FIELD ---** Handling of ties in rank:
**\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_**

**Pre-committed failure conditions.**

Any one of the following is recorded as falsification of the primary
claim and is reported as such:

--- The two arms produce the same dominant force pair.

--- The orderings differ but not in the predicted direction.

--- The observed effect is below the committed minimum in Part V.

--- Degradation is proportional across all four forces in both arms,
with no differential structure. This is the null and it is statable.

--- The result holds only after a parameter is changed from its Part III
value.

**PART VI --- SECONDARY AND ABLATION ANALYSES**

These are reported regardless of the primary result and are not
permitted to substitute for it.

  ------------------------------- ---------------------------------------
  **Analysis**                    **Purpose**

  Ablation ladder: V1 = Gate 1    Makes each gate's contribution
  only; V2 = Gates 1+2; V3 = all  separately reportable rather than the
  three                           cascade being a black box

  Charting-density-only baseline  Negative control. If density alone
  model                           reproduces the result, the geometry has
                                  added nothing.

  Ω suppression audit, per arm    Counts and characterises every case the
                                  veto suppressed (see VII.1)

  Matched effective-sample-count  Tests whether the arm difference
  sensitivity                     survives equalising
                                  points-per-unit-dynamics

  Per-pair F4 trajectory          Direction channel; distinct from the
  reporting                       detection scalar
  ------------------------------- ---------------------------------------

**PART VII --- PRE-REGISTERED THREATS**

**VII.1 The Ω gate may carry a condition-specific prior**

**This is the most serious threat in the document and it is new to this
version.**

Gate 3 vetoes the compensation pattern: rising HR against held SpO₂ and
held blood pressure. That template is drawn from immune-response
physiology. Arm B's own predicted early signature is compensatory
HR--MAP locking --- rising HR against a held pressure, with coupling
tightening. These are close enough that Gate 3 may suppress the
secondary arm's signal.

The consequence is not merely reduced sensitivity. A suppressed Arm B is
indistinguishable, in the results, from a genuine null --- the
architecture would appear falsified for a reason internal to its own
veto rather than for a reason about physiology.

Two pre-registered controls:

\(a\) The compensation template is defined with a coupling-sign
condition, so that septic compensation (coupling loosening) and
cardiogenic compensation (coupling tightening) are distinguishable by
the gate rather than collapsed by it. This is committed in Part III.3
before signature, not adjusted afterward.

\(b\) The Ω suppression audit is a reported output, not a diagnostic
afterthought: suppressed case counts per arm, with characterisation,
reported whether or not the primary claim survives.

**VII.2 Instrument mismatch between detection and F4 attribution**

The detection scalar is sign-blind and dilutes localised decoupling;
synthetic work showed detection AUC falling from roughly 0.74 to 0.54 at
small effective n when decoupling is localised rather than global. The
architecture predicts localised decoupling. The scalar is therefore
retained for detection only, and the six-vector carries every F4 claim.
This is a stated design constraint, not a finding.

**VII.3 Charting-density asymmetry between arms**

Arm B is expected to be charted more densely than Arm A. Estimation
noise scales with points per unit dynamics, so a density difference is
itself a candidate explanation for a force-loading difference. Addressed
by the matched effective-sample-count sensitivity analysis in Part VI,
which is pre-committed rather than conditional on the primary result.

**VII.4 Selection can manufacture a rank reversal**

Rank-based statistics are robust to measurement confounding but are not
robust to selection. Selection changes which patients are in the dataset
rather than distorting measurements on a fixed population, and can
therefore produce a reversal that no measurement artefact could. This is
why Part II.3 exclusions are pre-registered and reported with counts.

**VII.5 Confounding by indication**

Intervention timing tracks how sick the treating clinician believes the
patient to be. Anchors defined by intervention are therefore anchors
defined partly by clinician judgment. Stated as a limitation; not
correctable within this design.

**VII.6 Arterial-line sampling bias**

Invasive monitoring is allocated to sicker patients, so sampling density
correlates with severity in Arm B specifically. Reported as a covariate.

**VII.7 BRI cold-start overlap with collapse**

Where a patient deteriorates during the cold-start window, the baseline
is estimated on already-departing physiology. Exclusion or flagging rule
committed in Part II.4.

**VII.8 Multiple realisability of F4**

Pacing, controlled ventilation, beta blockade and atrial fibrillation
all produce a coupling-fidelity signal without the proposed mechanism.
Pacing and anticholinergics are excluded; the remainder are covariates.
The architecture detects the failure of compensation, never the thing
being compensated for.

**PART VIII --- FIREWALLS**

Each firewall below is a commitment made in advance about what evidence
is not admissible. They exist because the temptation they guard against
only becomes visible after the result is known.

**VIII.1 Waveform non-rescue firewall**

No Track B or waveform-resolution result is eligible to rescue, explain,
reinterpret, or soften a null in this confirmatory charted-data
analysis. If Track A returns the null, the null is the result. A
waveform finding may appear in discussion as forward-looking work and in
no other role.

**VIII.2 Exploratory testbed firewall**

The 198-patient MIMIC-IV Waveform v0.1.0 set is an engineering testbed
only. No parameter, threshold, window, or statistic in Part III may be
selected, tuned, or sanity-checked against it. Subject overlap with
either confirmatory cohort is checked by diffing subject_id lists before
any waveform work proceeds.

**VIII.3 Demo-set firewall**

The 100-patient open-access MIMIC-IV demo is used for pipeline
engineering only --- that the code runs, not what it finds.

**VIII.4 Calibration firewall**

Pre-analysis diagnostics under Part X return distributional properties
of the data (cadence, carry-forward, effective n, exposure prevalence,
baseline availability). They do not return outcomes, and no diagnostic
result may be used to select a value in Part III other than the
analyzability preconditions in Part II.4, which are themselves committed
before the diagnostics are run.

**PART IX --- WHAT IS NOT CLAIMED**

Stated in advance so that it cannot be quietly claimed later.

--- No false-positive-reduction figure is claimed. The 45% → 5% figure
originated in a comment block in a demo validation script, referred to
Gate 2 alone on twenty synthetic patients, and is not a confirmatory
result. It is not cited in any output from this study.

--- No lead-time superiority is claimed as a primary endpoint. Any
lead-time reporting is direction-only and secondary.

--- No claim that the architecture identifies the initiating axis. A
capability question is answered yes by construction and is therefore not
a result.

--- No claim of condition-agnosticism in general. The defensible
statement is transfer across two mechanistically opposite phenotypes
under one locked parameter set, within span{F1, F2, F3, F4} at charted
resolution.

--- No claim outside the competence envelope. Where the coupling
structure carries no information beyond the marginals, the geometry adds
nothing and the correct behaviour is to defer to univariate monitoring.
This boundary is reported, not hidden.

--- No claim about intervention efficacy.

--- No claim about F2b at charted resolution. It is not estimable with
this instrument; a condition dominated by adaptive-range collapse is
invisible to this study rather than nulled by it.

**PART X --- ANALYSIS ORDER LOCK**

Steps are executed in this order. No step may be revisited once a later
step has begun.

  -------- -------------------------------------------- ----------------------
  **\#**   **Step**                                     **Gate to proceed**

  1        Close blocking condition B1 --- pin the      Anchor set written
           cardiac anchor itemids                       into Part II.2

  2        Commit every unlocked field in Parts II--V   No UNLOCKED field
                                                        remains

  3        Sign Part 0                                  Signature and
                                                        timestamp recorded

  4        Run pre-analysis diagnostics (cadence,       Firewall VIII.4
           carry-forward, effective n, exposure,        respected --- no
           baseline availability)                       outcome fields touched

  5        Apply analyzability preconditions; report    Exclusion counts
           exclusion rates per arm                      recorded before
                                                        extraction of outcomes

  6        Extract confirmatory cohorts                 Cohorts frozen

  7        Run the locked engine, both arms, one        No parameter altered
           parameter set                                

  8        Compute force orderings and adjudicate Part  Result recorded,
           V                                            positive or null

  9        Run secondary and ablation analyses (Part    ---
           VI)                                          

  10       Report                                       Part IX honoured in
                                                        full
  -------- -------------------------------------------- ----------------------

*If step 8 returns the null, the null is written up. That is the
condition under which this document was worth writing.*
