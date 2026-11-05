"""
Within-Arm A separability test.

Hypothesis under test (instrument-level, not physiological):
  ESCAPE SIGNATURE = Gate1 open AND Gate2 (DP) open, AND F1 not in top-2,
  AND F4 not in top-2.  i.e. committed directional motion is present, the
  cascade agrees something is happening, but the Arm A predicted forces
  are not the ones loading.

Question: does that signature isolate a myocardial-component subgroup
within Arm A, at hourly charting cadence, under ONE locked parameter set?

SYNTHETIC ONLY. Firewalls VIII.2/VIII.3 not engaged.
"""
import numpy as np
import forcelab2 as FL
from scipy.stats import rankdata

np.seterr(all="ignore")
RNG = np.random.default_rng(20260807)
P = FL.P

def _ou(n, tau, sd, rng):
    x=np.zeros(n); a=np.exp(-1.0/tau)
    for i in range(1,n): x[i]=a*x[i-1]+rng.normal(0,sd*np.sqrt(1-a**2))
    return x

def make_patient(kind, hours=60, anchor_h=54, rng=None):
    """Extends forcelab2 generator with a septic-cardiomyopathy archetype."""
    rng = rng or RNG; n=hours; t=np.arange(n)
    onset = anchor_h-18; ramp = np.clip((t-onset)/(anchor_h-onset),0,1)
    base=dict(HR=82.,MAP=78.,RR=16.,SPO2=97.); sd=dict(HR=4.,MAP=4.,RR=1.6,SPO2=.8)
    drive=_ou(n,4,1.,rng); tau=dict(HR=3.,MAP=3.,RR=3.,SPO2=3.)

    if kind=="sepsis_pure":
        load=dict(HR=+14*ramp, MAP=-16*ramp, RR=+3*ramp**2.5, SPO2=-1.2*ramp**2.5)
        decouple=ramp; tighten=np.zeros(n); tau_gain=1+0.4*ramp**3

    elif kind=="sepsis_scm":
        # distributive insult PLUS myocardial depression.
        # blunted chronotropic reserve -> HR rises less; MAP falls similarly;
        # return capacity degrades EARLY (the F2 signature); effort raised.
        load=dict(HR=+9*ramp, MAP=-15*ramp, RR=+5*ramp, SPO2=-2.0*ramp)
        decouple=0.5*ramp          # septic loosening, partial
        tighten =0.5*ramp          # myocardial locking, partial -- these COMPETE
        tau_gain=1+2.0*ramp        # early return-capacity failure

    elif kind=="cardiogenic":
        late=np.clip((t-anchor_h+6)/6,0,1)
        load=dict(HR=+18*ramp, MAP=-2*ramp-14*late, RR=+5*ramp, SPO2=-2.5*ramp)
        decouple=np.zeros(n); tighten=ramp; tau_gain=1+2.2*ramp

    else:
        load={c:np.zeros(n) for c in base}
        decouple=np.zeros(n); tighten=np.zeros(n); tau_gain=np.ones(n)

    X=np.zeros((n,4))
    for k,c in enumerate(FL.CH):
        idio=np.zeros(n)
        for i in range(1,n):
            a=np.exp(-1.0/(tau[c]*tau_gain[i]))
            idio[i]=a*idio[i-1]+rng.normal(0,sd[c]*np.sqrt(max(1-a**2,1e-6)))
        w=0.65*(1-0.9*decouple)
        if c in ("HR","MAP"): w=w+0.30*tighten
        X[:,k]=base[c]+load[c]+w*sd[c]*drive+0.8*idio
    return dict(kind=kind,X=X,anchor=anchor_h,hours=hours)

def analyse(pt):
    ts,Z,six,rows = FL.run_patient(pt)
    anchor = pt["anchor"]; pre = ts<=anchor
    esc_windows = 0; open_windows = 0
    for i,tt in enumerate(ts):
        if tt>anchor: break
        if not FL.gates_open(rows,i): continue
        open_windows += 1
        zs = {k:Z[k][i] for k in ["F1","F2","F3","F4"]}
        top2 = set(sorted(zs, key=lambda k:-zs[k])[:2])
        if ("F1" not in top2) and ("F4" not in top2):
            esc_windows += 1
    peak = {k: np.nanmax(Z[k][pre]) for k in ["F1","F2","F3","F4"]}
    idx6 = np.argmin(np.abs(ts-(anchor-6)))
    return dict(escape=esc_windows, open=open_windows,
                esc_frac = esc_windows/open_windows if open_windows else np.nan,
                peak=peak, six=six[idx6], ts=ts, Z=Z, anchor=anchor)

def cohort(kind, n=120):
    return [analyse(make_patient(kind, rng=RNG)) for _ in range(n)]

def auc(x,y):
    x=np.asarray(x,float); y=np.asarray(y,float)
    m=np.isfinite(x); x=x[m]; m=np.isfinite(y); y=y[m]
    if len(x)==0 or len(y)==0: return np.nan
    z=rankdata(np.r_[x,y]); n1=len(x)
    return (z[:n1].sum()-n1*(n1+1)/2)/(n1*len(y))

if __name__=="__main__":
    PURE = cohort("sepsis_pure"); SCM = cohort("sepsis_scm")
    CARD = cohort("cardiogenic");  CTRL = cohort("control")

    print("="*68)
    print("1. ESCAPE SIGNATURE RATE  (Gate1+Gate2 open, F1 and F4 both absent)")
    print("="*68)
    print(f"{'cohort':16s} {'cascade-open':>13s} {'escape frac':>13s} {'pts w/ >=1 esc':>15s}")
    for nm,co in [("sepsis_pure",PURE),("sepsis_SCM",SCM),
                  ("cardiogenic",CARD),("control",CTRL)]:
        ow=np.mean([c["open"] for c in co])
        ef=np.nanmean([c["esc_frac"] for c in co])
        any_e=np.mean([c["escape"]>0 for c in co])
        print(f"{nm:16s} {ow:13.1f} {ef:13.2f} {any_e:15.0%}")

    print()
    print("="*68)
    print("2. IS THE SIGNATURE SPECIFIC?  (SCM vs pure sepsis, within Arm A)")
    print("="*68)
    a=[c["esc_frac"] for c in SCM]; b=[c["esc_frac"] for c in PURE]
    print(f"  escape-fraction        AUC(SCM>pure) = {auc(a,b):.3f}")
    a=[c['peak']['F2'] for c in SCM]; b=[c['peak']['F2'] for c in PURE]
    print(f"  peak F2 z              AUC(SCM>pure) = {auc(a,b):.3f}")
    a=[c['peak']['F3'] for c in SCM]; b=[c['peak']['F3'] for c in PURE]
    print(f"  peak F3 z              AUC(SCM>pure) = {auc(a,b):.3f}")
    a=[c['peak']['F2']-c['peak']['F1'] for c in SCM]
    b=[c['peak']['F2']-c['peak']['F1'] for c in PURE]
    print(f"  F2z - F1z contrast     AUC(SCM>pure) = {auc(a,b):.3f}")

    print()
    print("="*68)
    print("3. F4 SUPPRESSION IN MIXED PHYSIOLOGY  (dRho HR-MAP at anchor-6h)")
    print("="*68)
    for nm,co in [("sepsis_pure",PURE),("sepsis_SCM",SCM),
                  ("cardiogenic",CARD),("control",CTRL)]:
        v=np.array([c["six"][0] for c in co])
        mag=np.array([np.mean(np.abs(c["six"])) for c in co])
        print(f"  {nm:14s} dRho(HR,MAP) = {v.mean():+.3f}   mean|six| = {mag.mean():.3f}")

    print()
    print("="*68)
    print("4. DOES ARM-LEVEL DISSOCIATION SURVIVE SCM CONTAMINATION?")
    print("   (mean signed six-vector, Arm B vs Arm A, at varying SCM prevalence)")
    print("="*68)
    b_vals=[np.mean(c["six"]) for c in CARD]
    for prev in [0.0,0.2,0.4,0.6]:
        k=int(prev*120)
        mixed=[np.mean(c["six"]) for c in PURE[:120-k]] + \
              [np.mean(c["six"]) for c in SCM[:k]]
        print(f"  SCM prevalence {prev:4.0%}   AUC(ArmB>ArmA) = {auc(b_vals,mixed):.3f}")
