"""
Redesigned reserve test.

Design: same perturbation, different baseline reserve. Baseline coupling
w_base is swept; the perturbation is held identical as a PROPORTIONAL change
in coupling weight, so "the same underlying physiological change" is well
defined independent of starting point.

Measured per patient:
  (1) raw d-rho
  (2) baseline rho
  (3) available directional headroom  H = 1 +/- rho_base
  (4) headroom-normalised  RC = d-rho / H
  (5) Fisher-z delta        dz = atanh(rho_now) - atanh(rho_base)
  (6) estimator uncertainty on rho_base, propagated into H

Success criterion (stated before the run): an estimator succeeds if the SAME
proportional perturbation yields a signal whose coefficient of variation
ACROSS baseline states is materially smaller than that of raw d-rho.

Plus: F2 identifiability -- can dAR(1) on a short window distinguish a known
recovery-rate change from finite-window estimation error at all?

SYNTHETIC ONLY.
"""
import numpy as np
from scipy.stats import rankdata
np.seterr(all="ignore")
RNG = np.random.default_rng(20260807)
CH = ["HR","MAP","RR","SPO2"]
BASE_H, WIN_H = 24, 6

def detrend(W):
    t = np.arange(len(W)) - (len(W)-1)/2
    D = np.empty_like(W)
    for k in range(W.shape[1]):
        D[:,k] = W[:,k] - (np.dot(t,W[:,k])/np.dot(t,t))*t
    return D

def ar1(v):
    if len(v) < 3 or np.std(v[:-1]) < 1e-9 or np.std(v[1:]) < 1e-9: return np.nan
    return float(np.corrcoef(v[:-1], v[1:])[0,1])

def simulate(w_base, pert, tau=3.0, tau_ratio=1.0, hours=60, eval_h=48, rng=None):
    """pert: proportional change in coupling weight. +ve = tighten, -ve = loosen.
       Applied ONLY after the baseline period, ramped to full by eval_h."""
    rng = rng or RNG; n = hours; t = np.arange(n)
    ramp = np.clip((t - BASE_H)/(eval_h - BASE_H), 0, 1)
    sd = dict(HR=4., MAP=4., RR=1.6, SPO2=.8)
    a = np.exp(-1/4.); drive = np.zeros(n)
    for i in range(1,n): drive[i] = a*drive[i-1] + rng.normal(0, np.sqrt(1-a**2))
    tg = 1 + (tau_ratio-1)*ramp
    X = np.zeros((n,4))
    for k,c in enumerate(CH):
        idio = np.zeros(n)
        for i in range(1,n):
            aa = np.exp(-1.0/(tau*tg[i]))
            idio[i] = aa*idio[i-1] + rng.normal(0, sd[c]*np.sqrt(max(1-aa**2,1e-6)))
        w = w_base*(1 + pert*ramp)          # PROPORTIONAL perturbation
        X[:,k] = w*sd[c]*drive + 0.8*idio
    return X

def measure(X, eval_h=48):
    B = detrend(X[:BASE_H])
    rho_b = np.corrcoef(B.T)[0,1]
    W = detrend(X[eval_h-WIN_H:eval_h])
    rho_n = np.corrcoef(W.T)[0,1]
    d = rho_n - rho_b
    H = (1 - rho_b) if d >= 0 else (1 + rho_b)
    # estimator uncertainty on rho_base via Fisher z
    se_z = 1/np.sqrt(max(BASE_H-3,1))
    zb = np.arctanh(np.clip(rho_b,-.999,.999))
    lo, hi = np.tanh(zb-se_z), np.tanh(zb+se_z)
    H_lo = (1-hi) if d>=0 else (1+lo)      # conservative (smallest) headroom
    H_hi = (1-lo) if d>=0 else (1+hi)
    dz = np.arctanh(np.clip(rho_n,-.999,.999)) - zb
    return dict(rho_b=rho_b, rho_n=rho_n, draw=d, H=H, RC=d/H if H>1e-3 else np.nan,
                RC_lo=d/H_hi if H_hi>1e-3 else np.nan,
                RC_hi=d/H_lo if H_lo>1e-3 else np.nan, dz=dz)

def cv(x):
    x = np.asarray(x, float); x = x[np.isfinite(x)]
    return np.abs(np.std(x)/np.mean(x)) if len(x) and abs(np.mean(x))>1e-9 else np.nan

if __name__=="__main__":
    WB = [0.25, 0.40, 0.55, 0.70, 0.85]
    N  = 400

    for pertname, pert in [("LOOSENING (sepsis-like, -60% coupling)", -0.60),
                           ("TIGHTENING (cardiogenic-like, +45% coupling)", +0.45)]:
        print("="*78)
        print(f"SAME PROPORTIONAL PERTURBATION, VARYING BASELINE RESERVE — {pertname}")
        print("="*78)
        print(f"{'w_base':>7s} {'rho_base':>9s} {'headroom H':>11s} {'raw drho':>10s} "
              f"{'RC=drho/H':>11s} {'Fisher dz':>10s}")
        agg = {k:[] for k in ["draw","RC","dz"]}
        rows = []
        for wb in WB:
            m = [measure(simulate(wb, pert, rng=RNG)) for _ in range(N)]
            r = {k: np.nanmean([x[k] for x in m]) for k in ["rho_b","H","draw","RC","dz"]}
            rows.append(r)
            for k in agg: agg[k].append(r[k])
            print(f"{wb:7.2f} {r['rho_b']:9.3f} {r['H']:11.3f} {r['draw']:10.3f} "
                  f"{r['RC']:11.3f} {r['dz']:10.3f}")
        print(f"\n  CV across baseline states (lower = more comparable):")
        print(f"    raw d-rho        CV = {cv(agg['draw']):.3f}")
        print(f"    RC = d-rho / H   CV = {cv(agg['RC']):.3f}")
        print(f"    Fisher dz        CV = {cv(agg['dz']):.3f}")
        print()

    print("="*78)
    print("DENOMINATOR UNCERTAINTY — how much does H move over its own CI?")
    print("="*78)
    print(f"{'w_base':>7s} {'rho_base':>9s} {'RC point':>10s} {'RC lo':>9s} {'RC hi':>9s} {'width/point':>12s}")
    for wb in WB:
        m = [measure(simulate(wb, -0.60, rng=RNG)) for _ in range(N)]
        p  = np.nanmean([x['RC'] for x in m])
        lo = np.nanmean([x['RC_lo'] for x in m]); hi = np.nanmean([x['RC_hi'] for x in m])
        print(f"{wb:7.2f} {np.nanmean([x['rho_b'] for x in m]):9.3f} "
              f"{p:10.3f} {lo:9.3f} {hi:9.3f} {abs(hi-lo)/abs(p):12.2f}")

    print()
    print("="*78)
    print("PER-PATIENT NOISE — is any of this usable at the single-patient level?")
    print("="*78)
    m = [measure(simulate(0.55, -0.60, rng=RNG)) for _ in range(N)]
    for k,nm in [("draw","raw d-rho"),("RC","RC = d-rho/H"),("dz","Fisher dz")]:
        v = np.array([x[k] for x in m], float); v = v[np.isfinite(v)]
        print(f"  {nm:16s} mean {v.mean():+.3f}  sd {v.std():.3f}  |mean|/sd = {abs(v.mean())/v.std():.2f}")
    print(f"  (analytic SE of a correlation on a {WIN_H}-point window: "
          f"Fisher SE(z) = {1/np.sqrt(WIN_H-3):.3f})")

    print()
    print("="*78)
    print("F2 IDENTIFIABILITY — can dAR(1) detect a KNOWN recovery-rate change?")
    print("="*78)
    print(f"{'tau ratio':>10s} {'dAR1 mean':>11s} {'dAR1 sd':>9s} {'AUC vs ratio=1':>16s}")
    ref = None
    for tr in [1.0, 1.5, 2.0, 3.0, 4.0]:
        vals = []
        for _ in range(N):
            X = simulate(0.55, 0.0, tau_ratio=tr, rng=RNG)
            B = X[:BASE_H]; W = X[48-WIN_H:48]
            ab = np.nanmean([ar1(B[:,k]) for k in range(4)])
            an = np.nanmean([ar1(W[:,k]) for k in range(4)])
            vals.append(an-ab)
        v = np.array(vals); v = v[np.isfinite(v)]
        if ref is None: ref = v; auc = 0.5
        else:
            z = rankdata(np.r_[v, ref]); auc = (z[:len(v)].sum()-len(v)*(len(v)+1)/2)/(len(v)*len(ref))
        print(f"{tr:10.1f} {v.mean():+11.3f} {v.std():9.3f} {auc:16.3f}")
