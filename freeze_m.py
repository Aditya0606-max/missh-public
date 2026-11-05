#!/usr/bin/env python3
"""
freeze_m.py  —  Class R. No data contact. Run BEFORE the feasibility gate.

m is a MECHANISM vector:
    m_i = +1  coupling tightens in this syndrome
    m_i = -1  coupling loosens in this syndrome

Mechanism delivers magnitude, not sign. The signed quantity was
sign(delta_rho_i) = m_i * sign(rho_base_i), and sign(rho_base_i) is not
estimable at ward cadence -- which is what the feasibility gate measures.

ELICITATION ORDER. Fill Arm A completely. Close the file. Then fill Arm B
from cardiogenic mechanism directly -- NOT as "how does Kamal differ from
Kranthi." Deriving B as the negation of A forces cos = -1 by construction
and makes the dissociation check vacuous.

THE QUESTION FOR EACH PAIR:
    As the patient moves from early syndrome toward deterioration, does the
    relationship between these two channels become MORE predictable (+1) or
    LESS predictable (-1)?
Not "does each channel worsen" -- that is the wind, not the coupling.

SENTENCE CRITERIA -- each must:
    1. name a physiological mechanism, not a statistical expectation
    2. state the direction without hedging ("becomes", not "can become")
    3. reference no run, dataset or prior result
    4. be capable of being wrong -- if it reads just as well with the
       opposite sign, it is not a mechanism
    5. operate in the PRE-event window, not only in established shock

Search for  <<<  to find the next empty slot.
"""

import hashlib
import json
import math
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# PRE-COMMITMENT. Six +/-1 entries means cos(1, m) = sum(m)/6, so attainable
# values are only 0, 1/3, 2/3, 1.
#   |cos| = 1.000  all six agree -> pure wind detector
#   |cos| = 0.667  5-1 split     -> dominated by common mode
#   |cos| = 0.333  4-2 split     -> some structure
#   |cos| = 0.000  3-3 split     -> orthogonal to "everything moved"
# Do not change these after seeing output.
# ---------------------------------------------------------------------------
DISQUALIFYING_ABS_COS = 0.667
MAX_ARM_AGREEMENT     = 0.333

PAIRS = ["HR-MAP", "HR-RR", "HR-SpO2", "MAP-RR", "MAP-SpO2", "RR-SpO2"]

# ---------------------------------------------------------------------------
# 1. THE TWELVE SIGNS.  +1 = tightens,  -1 = loosens.
# ---------------------------------------------------------------------------
M = {
    "A": {                      # sepsis-AKI (Kranthi) -- F1 + F4 predicted
        "HR-MAP":   -1,         # committed: baroreflex mediation degrades
        "HR-RR":    +1,         # committed: shared demand, residual tracking
        "HR-SpO2":  -1,         # committed: delivery-oxygenation propagation fails
        "MAP-RR":   -1,         # committed: MAP residual dominated by volume, tone, treatment
        "MAP-SpO2": -1,        # committed: see A7
        "RR-SpO2":  -1,         # committed: RR driven by CO2 acid-base while SpO2 buffered
    },
    "B": {                      # cardiogenic shock (Kamal) -- F3 (F2 withdrawn, A3)
        "HR-MAP":   None,       # <<< fill only after Arm A is complete
        "HR-RR":    None,       # <<<
        "HR-SpO2":  None,       # <<<
        "MAP-RR":   None,       # <<<
        "MAP-SpO2": None,       # <<<
        "RR-SpO2":  None,       # <<<
    },
}

# ---------------------------------------------------------------------------
# 2. THE TWELVE MECHANISM SENTENCES.
#
# Adjacent string literals concatenate automatically. Keep a trailing space
# inside each line's closing quote or the words will run together.
# ---------------------------------------------------------------------------
MECHANISM = {
    # ---- ARM A: sepsis-AKI (Kranthi) ----
    ("A", "HR-MAP"):
        "As sepsis-associated autonomic dysregulation progresses, baroreflex "
        "mediation between arterial pressure and chronotropic response "
        "degrades, so HR tracks MAP less consistently across the "
        "deterioration window.",
    ("A", "HR-RR"):
        "In the pre-event ward-stage sepsis-AKI window, residual heart-rate and respiratory-rate fluctuations are predicted to become more tightly coupled because both respond rapidly to the same changing physiological demand through autonomic and metabolic control. The relevant prediction is not that sympathetic activation raises both variables, but that short-timescale departures in cardiac and respiratory rate increasingly track the same changing demand, producing a stronger residual HR-RR association.",
    ("A", "HR-SpO2"):
        "In the pre-event ward-stage sepsis-AKI window, residual heart-rate and arterial-oxygen-saturation fluctuations are predicted to become less tightly coupled because short-timescale changes in cardiac/autonomic activity increasingly fail to produce corresponding changes in arterial saturation. Although cardiac output provides a pathway linking circulation to oxygenation, SpO2 remains tightly constrained near the upper portion of the oxygen-haemoglobin dissociation curve while heart rate continues to fluctuate. The prediction would be falsified if pulmonary involvement in the pre-event window pushes patients sufficiently off this flat portion of the dissociation curve that SpO2 acquires substantial delivery-sensitive variance and HR-SpO2 coupling instead strengthens. The limited saturation variance therefore constrains observable headroom but does not determine the predicted sign.",
    ("A", "MAP-RR"):
        "",                     # <<< perfusion and ventilatory drive
    ("A", "MAP-SpO2"):
        "In the pre-event ward-stage sepsis-AKI window, residual mean-arterial-pressure and arterial-oxygen-saturation fluctuations are predicted to become less tightly coupled because changes in systemic delivery pressure increasingly fail to produce corresponding changes in arterial saturation. The prediction is that short-timescale departures in MAP increasingly track factors governing systemic perfusion rather than fluctuations in SpO2, whose variation is constrained by pulmonary gas exchange and the upper portion of the oxygen-haemoglobin dissociation curve. The limited variance of SpO2 reduces the observable headroom for detecting further loosening when baseline saturation is already compressed; that is an information limitation, not the basis for the predicted sign.",
    ("A", "RR-SpO2"):
        "",                     # <<< respiratory compensation vs saturation

    # ---- ARM B: cardiogenic shock (Kamal) ----
    ("B", "HR-MAP"):
        "",                     # <<<
    ("B", "HR-RR"):
        "",                     # <<<
    ("B", "HR-SpO2"):
        "",                     # <<<
    ("B", "MAP-RR"):
        "",                     # <<<
    ("B", "MAP-SpO2"):
        "",                     # <<<
    ("B", "RR-SpO2"):
        "",                     # <<<
}

# ===========================================================================
# Nothing below this line needs editing.
# ===========================================================================


def refuse_if_incomplete():
    problems = []
    if DISQUALIFYING_ABS_COS is None:
        problems.append("DISQUALIFYING_ABS_COS not pre-committed")
    if MAX_ARM_AGREEMENT is None:
        problems.append("MAX_ARM_AGREEMENT not pre-committed")
    for a in ("A", "B"):
        for p in PAIRS:
            if M[a][p] not in (+1, -1):
                problems.append(f"sign      {a}/{p}")
            if not MECHANISM[(a, p)].strip():
                problems.append(f"mechanism {a}/{p}")
    if problems:
        print(f"REFUSED -- {24 - len(problems)}/24 slots filled. Remaining:\n")
        for x in problems:
            print("   -", x)
        print("\nA refusal here means the file is unfinished. A refusal you cannot")
        print("resolve -- a sign you cannot justify from mechanism -- is a finding.")
        raise SystemExit(1)


def cos(u, v):
    n = sum(a * b for a, b in zip(u, v))
    d = math.sqrt(sum(a * a for a in u)) * math.sqrt(sum(b * b for b in v))
    return n / d


def main():
    refuse_if_incomplete()
    ones = [1] * 6
    mA = [M["A"][p] for p in PAIRS]
    mB = [M["B"][p] for p in PAIRS]
    cA, cB, cAB = cos(ones, mA), cos(ones, mB), cos(mA, mB)

    print("=" * 60)
    print("MECHANISM VECTOR GEOMETRY   (Class R, no data contact)")
    print("=" * 60)
    print(f"  pairs {PAIRS}")
    print(f"  m_A   {mA}")
    print(f"  m_B   {mB}\n")
    print(f"  |cos(1, m_A)| = {abs(cA):.3f}   disqualifying at {DISQUALIFYING_ABS_COS}")
    print(f"  |cos(1, m_B)| = {abs(cB):.3f}   disqualifying at {DISQUALIFYING_ABS_COS}")
    print(f"   cos(m_A,m_B) = {cAB:+.3f}   ceiling {MAX_ARM_AGREEMENT}\n")

    # Decision is on the INTEGER sum, per THRESHOLD_RULE.md (commit c83312c).
    # The float threshold did not implement its own stated 5-1 rule:
    # a 5-1 split scores 4/6 = 0.6667 < 0.667 and passed. Cosines below
    # are REPORTED, not decisive.
    def disqualifies(v):
        n = len(v)
        bound = {6: 4, 5: 3, 4: 2}.get(n)
        if bound is None:
            raise SystemExit(f"No pre-committed rule for n={n}. See THRESHOLD_RULE.md.")
        return abs(sum(v)) >= bound

    sA, sB = sum(mA), sum(mB)
    print(f"  sum(m_A) = {sA:+d}   sum(m_B) = {sB:+d}   (n={len(mA)}, decision rule)\n")

    fail = []
    if disqualifies(mA):
        fail.append(f"Arm A is a wind detector in the coupling domain (|sum|={abs(sA)}).")
    if disqualifies(mB):
        fail.append(f"Arm B is a wind detector in the coupling domain (|sum|={abs(sB)}).")
    if abs(cAB) > MAX_ARM_AGREEMENT:
        fail.append("Arms not dissociable: mechanism vectors too aligned.")

    print("  VERDICT: " + ("DISQUALIFYING" if fail else "PASS"))
    for x in fail:
        print("   -", x)
    if not fail:
        print("   Dissociation is geometrically available. Proceed to gate spec.")

    rec = {
        "computed_utc": datetime.now(timezone.utc).isoformat(),
        "formulation": "magnitude (m), supersedes signed delta-rho",
        "pairs": PAIRS, "m_A": mA, "m_B": mB,
        "mechanism": {f"{a}/{p}": MECHANISM[(a, p)] for a in ("A", "B") for p in PAIRS},
        "abs_cos_ones_mA": round(abs(cA), 6),
        "abs_cos_ones_mB": round(abs(cB), 6),
        "cos_mA_mB": round(cAB, 6),
        "disqualifying_abs_cos": DISQUALIFYING_ABS_COS,
        "decision_rule": "integer |sum(m)|; n=6:>=4, n=5:>=3, n=4:>=2 (THRESHOLD_RULE.md)",
        "sum_mA": sum(mA), "sum_mB": sum(mB),
        "max_arm_agreement": MAX_ARM_AGREEMENT,
        "verdict": "DISQUALIFYING" if fail else "PASS",
        "verdict_detail": fail,
        "class": "R",
    }
    rec["sha256"] = hashlib.sha256(
        json.dumps(rec, indent=2, sort_keys=True).encode()).hexdigest()[:16]
    with open("m_frozen.json", "w") as f:
        json.dump(rec, f, indent=2, sort_keys=True)
    print(f"\n  Written m_frozen.json  sha256 {rec['sha256']}")
    print("  Commit this BEFORE writing the gate spec.")


if __name__ == "__main__":
    main()
