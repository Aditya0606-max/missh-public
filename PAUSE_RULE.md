# Unified pause rule for the persistence counter
Class R. No data contact.

## 1. Why one rule and not three
Three situations arise where DP's counter meets a window in which a pair does
not update:

    (a) TREATMENT      -- a window overlaps a registered intervention
    (b) ADMISSIBILITY  -- a pair falls below its observation floor
    (c) MIXED SPEED    -- MAP pairs close every 2h, oximeter pairs every 1h,
                          so MAP pairs have no value in odd windows

All three are the same event: the counter reaches a window where a pair carries
no information. Writing three separate rules would require defending why the
same situation has three answers. One specification governs all three.

## 2. The rule
A pair's persistence is evaluated ONLY across windows in which that pair
updates. A non-updating window neither confirms nor breaks persistence.

    - the counter SUSPENDS; it does not reset
    - it does not increment either -- absence is not evidence of persistence
    - when the pair next updates, the counter compares across the gap

## 3. Comparison across the gap
On resumption, compare the pair's state to its last updating window.

    INTACT      -> the counter continues from where it paused
    DISCONTINUOUS -> [FILL: restart, or continue with the jump flagged]

Tolerance for "intact": [FILL -- denominated in the standardisation null;
waits on that derivation]

Rationale for continuing rather than restarting on intact: if the trajectory
is unchanged across the gap, restarting would discard evidence already
confirmed. A treatment that leaves the trajectory intact is arguably STRONGER
evidence than the drift alone.

## 4. Maximum suspension
A suspension may not run indefinitely.

    maximum consecutive non-updating windows: [FILL]
    exceeded -> the episode is abandoned and the counter resets

Without this, a pair that goes dark for a day could resume and continue a count
begun before the gap, which is not defensible.

Per-treatment-class suspension lengths: [FILL -- a fluid bolus and a
vasopressor infusion have different durations]

## 5. What is recorded
Every suspension is recorded with its cause (treatment / admissibility /
mixed-speed), its length, and whether the resumption was intact.

Discontinuities are REPORTED, never GATED. A treatment jump does not suppress
an episode. This follows the same rule applied to v_r and to the variability
track: descriptive quantities never feed back into a gating decision.

## 6. Consequence
S0 must characterise the cascade under this rule. Gaps were previously shown to
manufacture persistence; that this rule prevents it is empirical, not
established here.

## 7. Standing conditions
Fixed before data contact. No interpolation to avoid a suspension. Suspension
counts are reported per patient, never silently absorbed.
