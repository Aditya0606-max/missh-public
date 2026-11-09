# C12v2 part 1: minute numerics, 12 h before tip -> one value per 5-min block. Writes c12v2_blocks.csv and c12v2_log.csv.
import pandas as pd, numpy as np, wfdb, warnings
warnings.filterwarnings("ignore")
U = pd.read_csv("m3_usable.csv", parse_dates=["intime"])
N = pd.read_csv("m3_numerics.csv"); N["start"] = pd.to_datetime(N.start, format="ISO8601")
N["hours"] = pd.to_numeric(N.hours, errors="coerce"); N["end"] = N.start + pd.to_timedelta(N.hours, unit="h")
npath = {l.strip().split("/")[-1]: "/".join(l.strip().split("/")[:-1]) for l in open("RECORDS-numerics")}
base = (U.tip_h >= 6) & (U.cov_any >= 0.8)
S = pd.concat([U[base & (U.label == "escalated") & (U.route == "pressor")].assign(who="Kranthi"),
               U[base & (U.label == "escalated") & (U.route == "both")].assign(who="mixed"),
               U[base & (U.label == "stable")].sample(frac=1, random_state=7).head(300).assign(who="Ajay")])
print(S.who.value_counts().to_dict(), flush=True)
VAL = {"HR": (20, 250), "RESP": (3, 60), "SpO2": (50, 100), "ABPMean": (20, 200), "ABPSys": (40, 260),
       "ABPDias": (15, 150), "NBPMean": (20, 200), "NBPSys": (40, 260), "NBPDias": (15, 150)}
ALIAS = {"%SpO2": "SpO2", "NBP SYS": "NBPSys", "NBP DIAS": "NBPDias", "NBP MEAN": "NBPMean",
         "ABP SYS": "ABPSys", "ABP DIAS": "ABPDias", "ABP MEAN": "ABPMean",
         "ART SYS": "ABPSys", "ART DIAS": "ABPDias", "ART MEAN": "ABPMean"}
rows, log = [], []
for i, r in enumerate(S.itertuples(), 1):
    tip = r.intime + pd.Timedelta(hours=r.tip_h); t0 = tip - pd.Timedelta(hours=12)
    q = N[(N.subject_id == r.subject_id) & (N.start < tip) & (N.end > t0)]
    parts = []
    for rec in q.itertuples():
        if rec.record not in npath: continue
        fs = float(rec.fs)
        a = max(0, int(np.floor((t0 - rec.start).total_seconds() * fs)))
        b = min(int(rec.hours * 3600 * fs), int(np.ceil((tip - rec.start).total_seconds() * fs)))
        if b - a < 2: continue
        try:
            x = wfdb.rdrecord(rec.record, pn_dir="mimic3wdb-matched/1.0/" + npath[rec.record], sampfrom=a, sampto=b)
        except Exception as ex:
            log.append((r.icustay_id, r.who, f"read error {rec.record}: {type(ex).__name__}")); continue
        t = rec.start + pd.to_timedelta(np.arange(a, a + x.p_signal.shape[0]) / fs, unit="s")
        m = np.asarray(((t - t0).total_seconds() // 60), int); ok = (m >= 0) & (m < 720)
        cols = {}
        for j, nm in enumerate(x.sig_name):
            k = ALIAS.get(nm.strip(), nm.strip())
            if k not in VAL: continue
            v = x.p_signal[ok, j]
            cols[k] = np.where(np.isfinite(cols[k]), cols[k], v) if k in cols else v
        if cols: parts.append(pd.DataFrame(cols, index=m[ok]))
    if not parts:
        log.append((r.icustay_id, r.who, "no numerics overlapping window")); continue
    D = pd.concat(parts).groupby(level=0).mean().reindex(range(720))
    for nm, (lo, hi) in VAL.items():
        if nm in D: D.loc[~D[nm].between(lo, hi), nm] = np.nan
        else: D[nm] = np.nan
    D[["NBPMean", "NBPSys", "NBPDias"]] = D[["NBPMean", "NBPSys", "NBPDias"]].ffill(limit=60)
    D["blk"] = (719 - D.index) // 5                                  # 0 = last 5 min before tip
    for blk, g in D.groupby("blk"):
        art = g.ABPMean.notna().sum() >= 3
        rows.append(dict(icustay_id=r.icustay_id, who=r.who, blk=blk,
            hr=g.HR.median(), rr=g.RESP.median(), spo2=g.SpO2.median(),
            map=g.ABPMean.median() if art else g.NBPMean.dropna().iloc[-1] if g.NBPMean.notna().any() else np.nan,
            sbp=g.ABPSys.median() if art else g.NBPSys.dropna().iloc[-1] if g.NBPSys.notna().any() else np.nan,
            dbp=g.ABPDias.median() if art else g.NBPDias.dropna().iloc[-1] if g.NBPDias.notna().any() else np.nan,
            src="art" if art else ("cuff" if g.NBPMean.notna().any() else "none")))
    hr_cov = D.groupby("blk").HR.apply(lambda s: s.notna().any()).mean()
    if hr_cov < 0.5: log.append((r.icustay_id, r.who, f"HR in only {hr_cov:.0%} of blocks"))
    if i % 20 == 0:
        pd.DataFrame(rows).to_csv("c12v2_blocks.csv", index=False); print(f"{i}/{len(S)} done", flush=True)
B = pd.DataFrame(rows); B.to_csv("c12v2_blocks.csv", index=False)
pd.DataFrame(log, columns=["icustay_id", "who", "reason"]).to_csv("c12v2_log.csv", index=False)
print("blocks:", len(B), "| patients:", B.icustay_id.nunique(), "| log entries:", len(log))
