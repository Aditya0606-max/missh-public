# C15 part 1: lead II, 1 min every 15 min, 12 h before tip -> RMSSD per sample. Writes c15_samples.csv, c15_log.csv.
import pandas as pd, numpy as np, wfdb, warnings
from wfdb import processing
warnings.filterwarnings("ignore")
U = pd.read_csv("m3_usable.csv", parse_dates=["intime"])
N = pd.read_csv("m3_numerics.csv"); N["start"] = pd.to_datetime(N.start, format="ISO8601")
N["hours"] = pd.to_numeric(N.hours, errors="coerce"); N["end"] = N.start + pd.to_timedelta(N.hours, unit="h")
wpath = {l.strip().split("/")[-1]: "/".join(l.strip().split("/")[:-1]) for l in open("RECORDS-waveforms")}
base = (U.tip_h >= 6) & (U.cov_any >= 0.8)
S = pd.concat([U[base & (U.label == "escalated") & (U.route == "pressor")].assign(who="Kranthi"),
               U[base & (U.label == "escalated") & (U.route == "both")].assign(who="mixed"),
               U[base & (U.label == "stable")].sample(frac=1, random_state=7).head(100).assign(who="Ajay")])
print(S.who.value_counts().to_dict(), flush=True)
rows, log = [], []
for i, r in enumerate(S.itertuples(), 1):
    tip = r.intime + pd.Timedelta(hours=r.tip_h); t0 = tip - pd.Timedelta(hours=12)
    segs = []
    for rec in N[(N.subject_id == r.subject_id) & (N.start < tip) & (N.end > t0)].itertuples():
        w = rec.record[:-1] if rec.record.endswith("n") else rec.record
        if w not in wpath: continue
        try: h = wfdb.rdheader(w, pn_dir="mimic3wdb-matched/1.0/" + wpath[w], rd_segments=True)
        except Exception: log.append((r.icustay_id, r.who, f"header error {w}")); continue
        st, pos = pd.Timestamp(h.base_datetime), 0
        for name, seg, n in zip(h.seg_name, h.segments, h.seg_len):
            s0 = st + pd.Timedelta(seconds=pos / h.fs); pos += n
            if seg is not None and "II" in (seg.sig_name or []):
                segs.append((name, wpath[w], s0, s0 + pd.Timedelta(seconds=n / h.fs), h.fs))
    if not segs: log.append((r.icustay_id, r.who, "no lead II segment in window")); continue
    for k in range(1, 49):
        t2 = tip - pd.Timedelta(minutes=15 * (k - 1)); t1 = t2 - pd.Timedelta(minutes=1)
        hit = [s for s in segs if s[2] <= t1 and s[3] >= t2]
        if not hit: continue
        name, d, s0, s1, fs = hit[0]
        a = int((t1 - s0).total_seconds() * fs)
        try:
            x = wfdb.rdrecord(name, pn_dir="mimic3wdb-matched/1.0/" + d, sampfrom=a, sampto=a + int(60 * fs), channel_names=["II"])
            sig = x.p_signal[:, 0]; sig = sig[np.isfinite(sig)]
            if len(sig) < 30 * fs: continue
            pk = processing.gqrs_detect(sig=sig, fs=fs)
        except Exception: continue
        rr = np.diff(pk) / fs * 1000; rr = rr[(rr >= 300) & (rr <= 2000)]
        if len(rr) < 10: continue
        ok = np.r_[False, np.abs(np.diff(rr)) / rr[:-1] < 0.20]; clean = rr[ok]
        irregular = 1 - ok.mean() > 0.20
        rmssd = np.sqrt(np.mean(np.diff(clean) ** 2)) if len(clean) >= 40 else np.nan
        rows.append(dict(icustay_id=r.icustay_id, who=r.who, min_before_tip=15 * (k - 1),
                         hr_ecg=60000 / np.median(rr), n_clean=len(clean), irregular=irregular,
                         rmssd=rmssd, rmssd_norm=100 * rmssd / np.mean(clean) if len(clean) >= 40 else np.nan))
    if i % 5 == 0:
        pd.DataFrame(rows).to_csv("c15_samples.csv", index=False); print(f"{i}/{len(S)} done", flush=True)
pd.DataFrame(rows).to_csv("c15_samples.csv", index=False)
pd.DataFrame(log, columns=["icustay_id", "who", "reason"]).to_csv("c15_log.csv", index=False)
print("samples:", len(rows), "| patients:", len({r["icustay_id"] for r in rows}), "| log:", len(log))
