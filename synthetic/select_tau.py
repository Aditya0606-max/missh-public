"""
tau selection — Gate 3 threshold on F4_scalar.
Procedure frozen in docs/S0_PROTOCOL.md before this ran.
DEVELOPMENT SEED 20260807 ONLY. Never touches evaluation seed 20260819.
Run once. Record output in docs/FROZEN_PARAMS.md. Do not rerun after S0.
"""
import sys, numpy as np
sys.path.insert(0, "scripts")
from forcelab2 import P, PAIRS, _detrend, bri, make_patient

DEV_SEED = 20260807
N_PATIENT_WEEKS = 2000
HOURS = 24 * 7          # one patient-week, hourly cadence

rng = np.random.default_rng(DEV_SEED)
vals = []

for i in range(N_PATIENT_WEEKS):
    pt = make_patient("stable", hours=HOURS, anchor_h=HOURS - 1, rng=rng)
    b, w, s = P["baseline_hours"], P["window_hours"], P["stride_hours"]
    V = bri(pt["X"], b)
    base_rho = np.corrcoef(_detrend(V[:b]).T)
    for i0 in range(b, len(V) - w + 1, s):
        W = V[i0:i0 + w]
        if len(W) < P["min_eff_n"]:
            continue
        R = np.corrcoef(_detrend(W).T)
        six = np.array([R[a, c] - base_rho[a, c] for a, c in PAIRS])
        if np.any(~np.isfinite(six)):
            continue
        vals.append(float(np.mean(np.abs(six))))

vals = np.array(vals)
print(f"development seed:      {DEV_SEED}")
print(f"patient-weeks:         {N_PATIENT_WEEKS}")
print(f"analyzable windows:    {len(vals)}")
print(f"F4_scalar mean/median: {vals.mean():.4f} / {np.median(vals):.4f}")
print(f"p90 / p95 / p99:       {np.percentile(vals,90):.4f} / "
      f"{np.percentile(vals,95):.4f} / {np.percentile(vals,99):.4f}")
print(f"\nTAU = {np.percentile(vals, 95):.6f}")
