# Are the monitor's 'HR Variability' / 'pNN50 Percent' numerics usable? Last 6 h before tip, 20 Kranthis + 20 Ajays.
import pandas as pd, numpy as np, wfdb, warnings
warnings.filterwarnings("ignore")
U = pd.read_csv("m3_usable.csv", parse_dates=["intime"])
N = pd.read_csv("m3_numerics.csv"); N["start"] = pd.to_datetime(N.start, format="ISO8601")
N["hours"] = pd.to_numeric(N.hours, errors="coerce"); N["end"] = N.start + pd.to_timedelta(N.hours, unit="h")
npath = {l.strip().split("/")[-1]: "/".join(l.strip().split("/")[:-1]) for l in open("RECORDS-numerics")}
base = (U.tip_h >= 6) & (U.cov_any >= 0.8)
S = pd.concat([U[base & (U.route == "pressor") & (U.label == "escalated")].head(20).assign(who="Kranthi"),
               U[base & (U.label == "stable")].sample(frac=1, random_state=7).head(20).assign(who="Ajay")])
rows = []
for r in S.itertuples():
    tip = r.intime + pd.Timedelta(hours=r.tip_h); t0 = tip - pd.Timedelta(hours=6)
    for rec in N[(N.subject_id == r.subject_id) & (N.start < tip) & (N.end > t0)].itertuples():
        if not isinstance(rec.signals, str) or "HR Variability" not in rec.signals: continue
        fs = float(rec.fs); a = max(0, int((t0 - rec.start).total_seconds() * fs))
        b = min(int(rec.hours * 3600 * fs), int((tip - rec.start).total_seconds() * fs))
        try: x = wfdb.rdrecord(rec.record, pn_dir="mimic3wdb-matched/1.0/" + npath[rec.record], sampfrom=a, sampto=b)
        except Exception: continue
        for nm in ["HR Variability", "pNN50 Percent"]:
            if nm in x.sig_name:
                v = x.p_signal[:, x.sig_name.index(nm)]
                rows.append(dict(who=r.who, sig=nm, filled=np.isfinite(v).mean(),
                                 nonzero=(np.nan_to_num(v) != 0).mean(), median=np.nanmedian(v)))
R = pd.DataFrame(rows)
print("Records with these signals:", len(R) // 2 if len(R) else 0)
print(R.groupby(["sig", "who"])[["filled", "nonzero", "median"]].median().round(2).to_string() if len(R) else "none found")
