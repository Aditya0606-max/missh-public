# Wind-detector threshold rule
Class R. No data contact.
Written while A/RR-SpO2 and A/MAP-RR are both open and unargued.

## 1. Defect in the original pre-commitment
freeze_m.py sets DISQUALIFYING_ABS_COS = 0.667 and tests abs(cos) >= 0.667.
Its own comment classifies a 5-1 split as disqualifying, but a 5-1 split
scores 4/6 = 0.6667 < 0.667 and therefore passes.
Intended rejection region: 14/64 vectors (21.9%). As coded: 2/64 (3.1%).
Resolution direction: toward the stated intent (tightening the check).

## 2. Rule at n=6
Decision is made on the integer sum, not on a float.
    |sum(m)| >= 4  disqualifies
No rounding surface. Equivalent to the 5-1 rule the comment states.
The cosine remains a REPORTED quantity.

## 3. Rule at n<6
Attainable |cos| lattices:
    n=6: {0, 1/3, 2/3, 1}
    n=5: {0.2, 0.6, 1.0}
    n=4: {0, 0.5, 1.0}

No n=5 threshold reproduces the n=6 rejection region exactly.
    n=5: |sum(m)| >= 3 disqualifies 4-1 and 5-0
         |sum(m)| >= 5 disqualifies only 5-0
    n=4: |sum(m)| >= 2 disqualifies 3-1 and 4-0
         |sum(m)| >= 4 disqualifies only 4-0

Rationale. The purpose of the check is to reject a coupling-domain
prediction when its sign vector is sufficiently one-sided that it can be
explained by generic decoupling rather than by pair-specific structure.
The check also limits exposure to baseline-coupling heterogeneity: the
downstream F4 quantity changes with the alignment between the baseline-
coupling direction and the mechanism vector, so a highly aligned vector
has greater sensitivity to that baseline direction.

When fewer than six signs are available the lattice becomes coarser. The
rule retains the same qualitative rejection principle -- reject strongly
one-sided patterns rather than weakening the check to unanimity only.
Where the lattice prevents exact equivalence with n=6, the more
conservative available boundary is selected prospectively rather than
chosen from the realized vector.

DECISION:
    n=5: |sum(m)| >= 3 disqualifies.
    n=4: |sum(m)| >= 2 disqualifies.

Consequence, stated explicitly: these boundaries make the check STRICTER
as pairs are dropped, not equivalent. Rejection regions are 21.9% (n=6),
37.5% (n=5), 62.5% (n=4). At n=4 only a 2-2 split survives. This
tightening is intended: a smaller vector carries less evidence, so
one-sidedness in it is penalised harder.

## 4. Standing conditions
- The check depends only on the count of -1 entries, never on which pairs.
  It tests balance, not structure.
- With five signs fixed, the sixth moves |cos| by at most 2/6.
- This rule is fixed before the remaining Arm A signs are argued and is
  not revisable after any m vector is complete.
