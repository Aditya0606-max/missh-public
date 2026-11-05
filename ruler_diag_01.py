# ruler_diag_01.py — why C-direction patients lack an HR/MAP ruler. No outcomes.
import pandas as pd

df = pd.read_csv("../missh_data/vitals_hourly_cal.csv")
for c in ["blocked", "sedated"]:
    df[c] = df[c].astype(str).str.lower().eq("true")
pt = pd.read_csv("../missh_data/patient_tiers_cal.csv")
cdir = set(pt.stay_id[pt.ptier == "Cdirection"])

w = df[df.hour_idx <= 11].copy()
w["map_ok"] = w["map"].notna()
w["clean"] = w.map_ok & ~w.blocked & ~w.sedated
w["clean_no_sed_rule"] = w.map_ok & ~w.blocked
w["clean_no_block_rule"] = w.map_ok & ~w.sedated
w["sed_only"] = w.sedated & ~w.blocked
w["block_only"] = w.blocked & ~w.sedated
w["both"] = w.blocked & w.sedated

g = w.groupby("stay_id").agg(
    hours=("hour_idx", "count"), map_present=("map_ok", "sum"),
    clean=("clean", "sum"), sed_only=("sed_only", "sum"),
    block_only=("block_only", "sum"), both=("both", "sum"),
    clean_no_sed=("clean_no_sed_rule", "sum"),
    clean_no_block=("clean_no_block_rule", "sum"))
g["cdir"] = g.index.isin(cdir)

L = ["RULER_DIAG — MAP, hours 0-11, no outcomes", ""]
for name, s in [("C-direction", g[g.cdir]), ("all others", g[~g.cdir])]:
    L.append(f"[{name}] patients={len(s)}")
    L.append(f"   stay shorter than 12 h: {(s.hours < 12).mean():.3f} "
             f"(median hours observed {s.hours.median():.0f})")
    for c in ["map_present", "clean", "sed_only", "block_only", "both"]:
        L.append(f"   {c:12s} median {s[c].median():4.1f}  mean {s[c].mean():5.2f}")
    L.append(f"   >=5 clean MAP hours if sedation NOT excluded: {(s.clean_no_sed >= 5).mean():.3f}")
    L.append(f"   >=5 clean MAP hours if blocks NOT excluded:   {(s.clean_no_block >= 5).mean():.3f}")
    L.append("")
text = "\n".join(L)
print(text)
open("RULER_DIAG.txt", "w").write(text + "\n")
