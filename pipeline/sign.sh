#!/bin/bash
# sign.sh — verify, hash everything, commit MANIFEST, tag reg1-signed.
set -e
cd ~/missh
if [ -n "$(git status --porcelain)" ]; then echo "REFUSED: uncommitted changes"; git status --short; exit 1; fi
MISS=$(pipeline/compare_results.sh prac | grep -E "^MISSING" || true)
if [ -n "$MISS" ]; then echo "REFUSED: missing practice results:"; echo "$MISS"; exit 1; fi
if ! python3 pipeline/compare_points.py | grep -q "ONLY INTERVALS DIFFER"; then
  echo "REFUSED: point estimates differ from calibration"; python3 pipeline/compare_points.py; exit 1; fi
if git rev-parse -q --verify refs/tags/reg1-signed > /dev/null; then echo "REFUSED: already signed"; exit 1; fi
{ echo "# MANIFEST — registration 1, signed $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "# commit before signing: $(git rev-parse HEAD)"
  git ls-files | grep -E '\.(md|py|sql|sh|json|txt)$' | sort | xargs sha256sum
} > MANIFEST.txt
git add MANIFEST.txt
git commit -m "SIGNED: registration 1 manifest (all rules, scripts, SQL, frozen files hashed)"
git tag -a reg1-signed -m "Registration 1 signed; 80% not yet run"
echo "Signed: $(git rev-parse --short HEAD), tag reg1-signed"
sha256sum MANIFEST.txt
