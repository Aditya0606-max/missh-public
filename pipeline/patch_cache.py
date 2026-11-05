# patch_cache.py — memoise matched() in summarize scripts (identical results, faster).
import sys
ADD = '''
_CACHE = {}
def matched(row, meas, same_news=False):
    key = (row.tier, float(row.hour), meas, same_news, row.band if same_news else None)
    if key not in _CACHE:
        _CACHE[key] = _matched_raw(row, meas, same_news)
    return _CACHE[key]
'''
for f in sys.argv[1:]:
    s = open(f).read()
    if "_matched_raw" in s: print(f, "already patched"); continue
    s = s.replace("def matched(row, meas, same_news=False):", "def _matched_raw(row, meas, same_news=False):", 1)
    s = s.replace("\ndef per_row(", ADD + "\ndef per_row(", 1)
    open(f, "w").write(s); print(f, "patched")
