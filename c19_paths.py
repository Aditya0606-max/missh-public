import pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
src = open("c16e_wardpace.py").read(); exec(src.split('\nA = L[L.who == "Ajay"]; W')[0])
L = L.sort_values(["icustay_id", "hour"]); L["sf"] = -L.negsf
T14 = pd.read_csv("c14g_kranthi.csv", index_col=0); R14 = pd.read_csv("c14_replay.csv").set_index("icustay_id")
rng = np.random.default_rng(7); pick = lambda ids: int(rng.choice(sorted(ids)))
cases = {"Kranthi caught early": pick(T14.index[T14.road_cls == "early"]), "Kranthi sudden slipper": pick(T14.index[T14.slip]),
         "Sundar": pick(L[L.who == "Sundar"].icustay_id.unique()), "Near-miss Ajay": pick(R14.index[(R14.who == "Ajay") & (R14.furthest >= 0.8)])}
NK = pd.read_csv("naveen_kind.csv"); NK = NK[(NK.kind == "medical emergency") & NK.esc_h.between(1, 3)]
N = pd.read_csv("naveen_hourly.csv").merge(NK[["icustay_id", "esc_h"]], on="icustay_id")
N["si"] = np.where(N.hr.between(20, 250) & N.sbp.between(40, 260), N.hr / N.sbp, np.nan); N["pp"] = N.sbp - N.dbp; N["mp"] = N.mbp
FN = ((N[CH] - rec) / (sh - rec)).clip(-0.5, 1.5); FN.columns = FC; N = pd.concat([N, FN], axis=1)
PN = pd.DataFrame({"a": N.rr.map(lambda v: pts(v, RRc)), "b": N.spo2.map(lambda v: pts(v, SPc)), "c": N.sbp.map(lambda v: pts(v, SBc)),
                   "d": N.hr.map(lambda v: pts(v, HRc)), "e": N.temp.map(lambda v: pts(v, TPc))})
N["news"] = np.where(PN.notna().sum(axis=1) >= 3, PN.sum(axis=1), np.nan)
nid = pick(N.groupby("icustay_id").mp.count().pipe(lambda s: s[s >= 2]).index)
def draw(name, D, tip, naveen=False):
    fig, ax = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    for c, lab in zip(FC, ["MAP", "shock index", "pulse pressure"]): ax[0].plot(D.hour, D[c], marker=".", alpha=0.6, label=lab)
    lead3 = D[FC].max(axis=1).rolling(3, min_periods=1).mean()
    ax[0].plot(D.hour, lead3, lw=2.5, color="k", label="leading channel (3-h)"); ax[0].axhline(1.5, ls="--", color="r")
    ax[0].set_ylabel("pressure road\n0 = Ajay, 1 = shock"); ax[0].legend(fontsize=7, loc="upper left")
    sf = D["sf"] if ("sf" in D and not naveen) else pd.Series(np.nan, index=D.index)
    if not naveen: ax[1].plot(D.hour, sf, marker=".", color="tab:blue"); ax[1].axhline(247.5, ls="--", color="r")
    ax[1].set_ylabel("S/F" + (" (not available)" if naveen else ""))
    ax[2].plot(D.hour, D.news, marker=".", color="tab:purple")
    for y in (5, 7): ax[2].axhline(y, ls=":", color="gray")
    ax[2].set_ylabel("NEWS-lite"); ax[2].set_xlabel("hours since ICU arrival")
    amb = D.hour[(lead3.values >= 1.5) | (sf.fillna(np.inf).values <= 247.5)]
    for a in ax:
        a.axvline(tip, color="r", lw=2)
        if len(amb): a.axvline(amb.iloc[0], color="orange", lw=2)
    fig.suptitle(f"{name} (stay {int(D.icustay_id.iloc[0])}): orange = first amber, red = tip"); fig.tight_layout()
    fn = "path_" + name.lower().replace(" ", "_") + ".png"; fig.savefig(fn, dpi=110); plt.close(fig)
    print(f"saved {fn} | tip {tip:.1f} h | first amber {amb.iloc[0] if len(amb) else 'none'}")
for name, sid in cases.items():
    D = L[L.icustay_id == sid]; draw(name, D, D.tip.iloc[0])
D = N[N.icustay_id == nid].groupby("hour").first().reset_index(); draw("Naveen", D, D.esc_h.iloc[0], naveen=True)
