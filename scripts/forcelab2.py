"""
Miss H x VEVFM -- Track A force estimator testbed, revision 2.
SYNTHETIC ONLY. Fixes four failures found in rev 1:
  (1) F4 correlation contaminated by within-window trend -> detrend before corr
  (2) F1 non-specific (fired 100% in BOTH arms) -> redefine as delivered-output loss
  (3) z-null underestimated from overlapping windows -> non-overlapping baseline null
  (4) force ranking run without the cascade -> Gate1+Gate2 now gate attribution
"""
import numpy as np
RNG = np.random.default_rng(20260807)
CH = ["HR","MAP","RR","SPO2"]
PAIRS = [(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)]
PAIRNM = ["HR-MAP","HR-RR","HR-SpO2","MAP-RR","MAP-SpO2","RR-SpO2"]

P = dict(baseline_hours=24, window_hours=6, stride_hours=1, min_eff_n=5,
         onset_z=2.0, onset_persist=2, hold_eps=0.75,
         g1_ocri=1.0, g2_dp=0.50, g2_axes=2)

def _ou(n, tau, sd, rng):
    x=np.zeros(n); a=np.exp(-1.0/tau)
    for i in range(1,n): x[i]=a*x[i-1]+rng.normal(0,sd*np.sqrt(1-a**2))
    return x

def make_patient(kind, hours=60, anchor_h=54, rng=None):
    rng = rng or RNG; n=hours; t=np.arange(n)
    onset = anchor_h-18; ramp = np.clip((t-onset)/(anchor_h-onset),0,1)
    base=dict(HR=82.,MAP=78.,RR=16.,SPO2=97.); sd=dict(HR=4.,MAP=4.,RR=1.6,SPO2=.8)
    drive=_ou(n,4,1.,rng); tau=dict(HR=3.,MAP=3.,RR=3.,SPO2=3.)
    if kind=="sepsis":
        load=dict(HR=+14*ramp, MAP=-16*ramp, RR=+3*ramp**2.5, SPO2=-1.2*ramp**2.5)
        decouple=ramp; tighten=np.zeros(n); tau_gain=1+0.4*ramp**3
    elif kind=="cardiogenic":
        late=np.clip((t-anchor_h+6)/6,0,1)
        load=dict(HR=+18*ramp, MAP=-2*ramp-14*late, RR=+5*ramp, SPO2=-2.5*ramp)
        decouple=np.zeros(n); tighten=ramp; tau_gain=1+2.2*ramp
    else:
        load={c:np.zeros(n) for c in base}
        decouple=np.zeros(n); tighten=np.zeros(n); tau_gain=np.ones(n)
    X=np.zeros((n,4))
    for k,c in enumerate(CH):
        idio=np.zeros(n)
        for i in range(1,n):
            a=np.exp(-1.0/(tau[c]*tau_gain[i]))
            idio[i]=a*idio[i-1]+rng.normal(0,sd[c]*np.sqrt(max(1-a**2,1e-6)))
        w=0.65*(1-0.9*decouple)
        if c in ("HR","MAP"): w=w+0.30*tighten
        X[:,k]=base[c]+load[c]+w*sd[c]*drive+0.8*idio
    return dict(kind=kind,X=X,anchor=anchor_h,hours=hours)

def bri(X,b):
    mu=X[:b].mean(0); sg=X[:b].std(0,ddof=1); sg=np.where(sg<1e-6,1e-6,sg)
    return (X-mu)/sg

def _detrend(W):
    """FIX 1: remove within-window linear trend before correlation."""
    n=len(W); t=np.arange(n)-np.mean(np.arange(n))
    D=np.empty_like(W)
    for k in range(W.shape[1]):
        b=np.dot(t,W[:,k])/np.dot(t,t) if np.dot(t,t)>0 else 0.
        D[:,k]=W[:,k]-b*t
    return D

def ar1(v):
    if len(v)<3: return np.nan
    a,b=v[:-1],v[1:]
    if np.std(a)<1e-9 or np.std(b)<1e-9: return np.nan
    return float(np.corrcoef(a,b)[0,1])

def dp(W):
    """Directional persistence per axis: |mean sign of successive deltas|."""
    d=np.diff(W,axis=0)
    return np.abs(np.mean(np.sign(d),axis=0))

def forces_window(V,i0,i1,base_rho,base_ar):
    W=V[i0:i1]
    if len(W)<P["min_eff_n"]: return None
    vHR,vMAP,vRR,vSP=W.mean(0)
    # FIX 2: F1 = loss of DELIVERED output (pressure/saturation), not demand divergence
    F1 = 0.5*((-vMAP) + (-vSP))
    ar_now=np.array([ar1(W[:,k]) for k in range(4)])
    F2 = 2.0*np.nanmean(ar_now-base_ar) + 0.25*np.abs(W.mean(0)).mean()
    # F3 = drive raised while output HELD (effort per unit output)
    # smooth "output held" weight -- indicator version is identically 0 in baseline
    # (median=0, MAD=0) and therefore has no null scale
    w_map = np.exp(-abs(vMAP)/P["hold_eps"]); w_sp = np.exp(-abs(vSP)/P["hold_eps"])
    F3 = 0.5*(vHR*w_map + vRR*w_sp)
    Wd=_detrend(W); R=np.corrcoef(Wd.T)
    six=np.array([R[i,j]-base_rho[i,j] for i,j in PAIRS])
    return dict(F1=F1,F2=F2,F3=F3,F4=float(np.mean(np.abs(six))),six=six,
                ocri=float(np.abs(W.mean(0)).mean()), dp=dp(W))

def run_patient(pt):
    b,w,s=P["baseline_hours"],P["window_hours"],P["stride_hours"]
    V=bri(pt["X"],b); B=V[:b]
    base_rho=np.corrcoef(_detrend(B).T)
    base_ar=np.array([ar1(B[:,k]) for k in range(4)])
    ts,rows=[],[]
    for i0 in range(0,len(V)-w+1,s):
        f=forces_window(V,i0,i0+w,base_rho,base_ar)
        if f is None: continue
        ts.append(i0+w-1); rows.append(f)
    ts=np.array(ts)
    # FIX 3: null from NON-OVERLAPPING baseline windows only
    null_idx=[i for i,tt in enumerate(ts) if tt<b]
    Z={}
    for k in ["F1","F2","F3","F4"]:
        v=np.array([r[k] for r in rows],float)
        nv=v[null_idx]; mu=np.nanmedian(nv)
        sd=1.4826*np.nanmedian(np.abs(nv-mu))   # robust scale; overlap-tolerant
        Z[k]=(v-mu)/(sd if sd>1e-6 else 1e-6)
    return ts,Z,np.array([r["six"] for r in rows]),rows

def gates_open(rows,i):
    """FIX 4: attribution only where the cascade is open."""
    g1 = rows[i]["ocri"] > P["g1_ocri"]
    g2 = int(np.sum(rows[i]["dp"] > P["g2_dp"])) >= P["g2_axes"]
    return g1 and g2

def onset_rank(ts,Z,rows,anchor):
    on={}
    for k,z in Z.items():
        hit=np.inf
        for i in range(len(z)-P["onset_persist"]+1):
            if ts[i]>anchor: break
            if np.all(z[i:i+P["onset_persist"]]>P["onset_z"]) and \
               all(gates_open(rows,j) for j in range(i,i+P["onset_persist"])):
                hit=ts[i]; break
        on[k]=hit
    return on, sorted(on,key=lambda k:(on[k],k))

def cohort(kind,n=80):
    out=[]
    for _ in range(n):
        pt=make_patient(kind,rng=RNG)
        ts,Z,six,rows=run_patient(pt)
        on,order=onset_rank(ts,Z,rows,pt["anchor"])
        out.append(dict(on=on,order=order,six=six,ts=ts,anchor=pt["anchor"]))
    return out

def top2(res,want):
    want=set(want); h=f=0
    for r in res:
        first=[k for k in r["order"] if np.isfinite(r["on"][k])][:2]
        if len(first)==2:
            f+=1
            if set(first)==want: h+=1
    return h,f

if __name__=="__main__":
    np.seterr(all="ignore")
    A=cohort("sepsis"); B=cohort("cardiogenic"); C=cohort("control")
    print("=== ONSET RANK RECOVERY (one locked parameter set, cascade-gated) ===")
    for nm,res,want in [("Arm A sepsis-AKI",A,("F1","F4")),("Arm B cardiogenic",B,("F2","F3"))]:
        h,f=top2(res,want); print(f"{nm:20s} top-2 {want}: {h}/{f} adjudicable ({len(res)} pts)")
    print("\n=== MEAN ONSET (h; anchor=54) / FIRE RATE ===")
    for nm,res in [("sepsis",A),("cardiogenic",B),("control",C)]:
        line=[]
        for k in ["F1","F2","F3","F4"]:
            v=[r["on"][k] for r in res if np.isfinite(r["on"][k])]
            fr=len(v)/len(res)
            line.append(f"{k}={np.mean(v):5.1f}(#{fr:.0%})" if v else f"{k}=  -- (#0%)")
        print(f"{nm:12s} "+"  ".join(line))
    print("\n=== F4 SIX-VECTOR, detrended, at anchor-6h (Arm A vs Arm B) ===")
    print(f"{'pair':10s} {'sepsis':>16s} {'cardiogenic':>16s} {'control':>16s}")
    for p in range(6):
        cells=[]
        for res in (A,B,C):
            vals=[r["six"][np.argmin(np.abs(r["ts"]-(r["anchor"]-6))),p] for r in res]
            cells.append(f"{np.mean(vals):+.3f}+/-{np.std(vals):.2f}")
        print(f"{PAIRNM[p]:10s} "+" ".join(f"{c:>16s}" for c in cells))
    ff=np.mean([any(np.isfinite(r["on"][k]) for k in r["on"]) for r in C])
    print(f"\ncontrol false-fire (>=1 force): {ff:.0%}")
