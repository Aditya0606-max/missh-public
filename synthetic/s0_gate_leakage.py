"""
S0 — gate leakage under stable and benign-movement nulls.
All parameters frozen in docs/FROZEN_PARAMS.md and docs/S0_PROTOCOL.md
BEFORE this ran. Nothing here may be retuned after seeing output.
EVALUATION SEED 20260819. Selection used 20260807.
"""
import sys, numpy as np
from scipy import stats
sys.path.insert(0, "scripts")
from forcelab2 import P, PAIRS, _detrend, bri, make_patient

EVAL_SEED, N_PAT, HOURS = 20260819, 2000, 168
TAU, G_MAX, PERSIST, MIN_BASE_N = 0.745289, 3, 3, 8
P_MISS_GIVEN_CHARTED, P_MISS_GIVEN_MISSED = 0.2667, 0.6000
NOMINAL_WINDOWS = 144   # hours 24-167, 6h window, 1h stride

def make_benign(hours, rng):
    """Null B: smooth excursion and return. No decouple, no tighten."""
    pt = make_patient("stable", hours=hours, anchor_h=hours-1, rng=rng)
    t = np.arange(hours); arc = 8*np.sin(np.pi*t/hours)
    sd = np.array([4., 4., 1.6, .8])
    pt["X"] = pt["X"] + arc[:, None]*sd[None, :]*0.25
    return pt

def charted_mask(n, rng):
    """Two-state Markov missingness. True = charted."""
    m = np.ones(n, bool); missing = False
    for i in range(n):
        p = P_MISS_GIVEN_MISSED if missing else P_MISS_GIVEN_CHARTED
        missing = rng.random() < p
        m[i] = not missing
    return m

def run_arm(kind, inject_missing, rng):
    episodes_clean = episodes_gap = 0
    analyzable = unanalyzable = 0
    for _ in range(N_PAT):
        pt = make_benign(HOURS, rng) if kind == "benign" else \
             make_patient("stable", hours=HOURS, anchor_h=HOURS-1, rng=rng)
        mask = charted_mask(HOURS, rng) if inject_missing else np.ones(HOURS, bool)
        b = P["baseline_hours"]
        if mask[:b].sum() < MIN_BASE_N:
            unanalyzable += 1; continue
        idx = np.where(mask)[0]
        V = bri(pt["X"], b)
        base = V[idx[idx < b]]
        base_rho = np.corrcoef(_detrend(base).T)
        pos, flags = [], []
        for i0 in range(b, HOURS - P["window_hours"] + 1, P["stride_hours"]):
            sel = idx[(idx >= i0) & (idx < i0 + P["window_hours"])]
            if len(sel) < P["min_eff_n"]: continue
            analyzable += 1
            W = V[sel]
            g1 = float(np.abs(W.mean(0)).mean()) > P["g1_ocri"]
            d = np.diff(W, axis=0)
            g2 = int(np.sum(np.abs(np.mean(np.sign(d), 0)) >= P["g2_dp"])) >= P["g2_axes"]
            R = np.corrcoef(_detrend(W).T)
            six = np.array([R[a,c]-base_rho[a,c] for a,c in PAIRS])
            if np.any(~np.isfinite(six)): continue
            g3 = float(np.mean(np.abs(six))) > TAU
            if g1 and g2 and g3:
                pos.append(i0); flags.append(np.max(np.diff(sel)) > 1 if len(sel)>1 else False)
        run, run_gap = [], False
        for j, a in enumerate(pos):
            if run and a - run[-1] > G_MAX:
                if len(run) >= PERSIST:
                    episodes_gap += run_gap; episodes_clean += not run_gap
                run, run_gap = [], False
            run.append(a); run_gap |= flags[j]
        if len(run) >= PERSIST:
            episodes_gap += run_gap; episodes_clean += not run_gap
    return episodes_clean, episodes_gap, analyzable, unanalyzable

def ucb95(events, exposure):
    if events == 0: return 3.0 / exposure
    return stats.chi2.ppf(0.95, 2*(events+1)) / (2*exposure)

for null in ("stable", "benign"):
    for miss in (False, True):
        rng = np.random.default_rng(EVAL_SEED)
        ec, eg, an, un = run_arm(null, miss, rng)
        pw = N_PAT - un
        cov = an / (NOMINAL_WINDOWS * pw) if pw else 0
        tag = "40% CLUSTERED MISSING" if miss else "COMPLETE CADENCE"
        print(f"\n=== NULL {null.upper()} / {tag} ===")
        print(f"patient-weeks analyzable : {pw}  (excluded {un})")
        print(f"coverage                 : {cov:.3f}")
        for name, e in (("CLEAN", ec), ("GAP-SPANNING", eg)):
            u = ucb95(e, pw) if pw else float('nan')
            print(f"{name:14s} episodes {e:5d}  rate {e/pw:.4f}  "
                  f"UCB95 {u:.4f}  {'PASS' if u <= 1 else 'FAIL'}")
