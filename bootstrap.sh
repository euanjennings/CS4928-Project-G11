#!/usr/bin/env bash
# ONE-TIME setup, run by ONE team member from the root of the team repo,
# after the scaffold commit (so .gitattributes is already in place).
# Creates:  commit "Import upstream"  ->  tag UPSTREAM_IMPORT  ->  commit "D1 fix"
# so every change you ever make to upstream code shows up in:
#     git diff UPSTREAM_IMPORT -- upstream/
set -euo pipefail

UPSTREAM_URL="https://github.com/ClassSplitter/ClassSplitter"
UPSTREAM_SHA="459d796d3256de428330bff693f14cf442097338"   # latest commit, 23 Aug 2024

if [ -e upstream ]; then echo "upstream/ already exists - aborting"; exit 1; fi
git diff --quiet && git diff --cached --quiet || { echo "Commit or stash your changes first"; exit 1; }

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
git clone --quiet "$UPSTREAM_URL" "$tmp/cs"
mkdir upstream
git -C "$tmp/cs" archive "$UPSTREAM_SHA" | tar -x -C upstream
printf '%s\n%s\n' "$UPSTREAM_URL" "$UPSTREAM_SHA" > upstream/UPSTREAM_VERSION.txt

git add upstream
git commit --quiet -m "Import ClassSplitter upstream verbatim @ ${UPSTREAM_SHA:0:7}"
git tag -a UPSTREAM_IMPORT -m "Verbatim import of $UPSTREAM_URL @ $UPSTREAM_SHA"

# Deviation D1 (see docs/DEVIATIONS.md): baseline1.py uses Group.members,
# but Group in the published cluster.py only has .units, so the baseline crashes.
f="upstream/Implementation/experienments/baseline1.py"
sed -i.bak -e 's/group1\.members\[i\]/group1.units[i]/' \
           -e 's/group2\.members\[j\]/group2.units[j]/' "$f"
rm -f "$f.bak"
git add "$f"
git commit --quiet -m "D1: baseline1.py uses Group.units (stale Group.members crashed the baseline)"

echo "Done. Now:  git push origin HEAD --tags"
git log --oneline -3
