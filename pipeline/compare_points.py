# compare_points.py — compare result files: identical text and numbers (within one rounding step),
# ignoring bootstrap interval bounds, which depend on row order.
import re
FILES = ["SUMMARY_P1.txt", "SUMMARY_P1_K0.txt", "SUMMARY_P2.txt", "SUMMARY_P3.txt",
         "SUMMARY_PP.txt", "SUMMARY_E13.txt", "P7_REHEARSAL.txt", "MOVERS.txt"]
NUM = re.compile(r"[-+]?\d+\.\d+|[-+]?\d+")
def strip(line):
    line = re.sub(r"\([^()]*\)", "(CI)", line)
    return re.sub(r"CI [-+0-9.]+ to [-+0-9.]+", "CI", line).rstrip()
def same(x, y):
    if NUM.sub("#", x) != NUM.sub("#", y): return False
    return all(abs(float(a) - float(b)) <= 0.0015 for a, b in zip(NUM.findall(x), NUM.findall(y)))
ok = True
for f in FILES:
    a = [strip(l) for l in open(f"/home/muppidiaditya/missh/{f}")]
    b = [strip(l) for l in open(f"/home/muppidiaditya/run_prac/repo/{f}")]
    bad = [(x, y) for x, y in zip(a, b) if not same(x, y)] + ([("lines", "count")] if len(a) != len(b) else [])
    print(f"{f:22s} {'POINTS SAME' if not bad else f'{len(bad)} line(s) differ'}")
    for x, y in bad[:3]: print(f"    orig: {x}\n    prac: {y}")
    ok &= not bad
print("\nONLY INTERVALS DIFFER" if ok else "\nPOINT VALUES DIFFER — investigate before signing")
