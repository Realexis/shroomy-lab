#!/bin/bash
# Publish the LAB copy BY HAND to the phone address https://realexis.github.io/shroomy-lab/
# Only ever pushes to Realexis/shroomy-lab (branch gh-pages). Never to the live site.
# No robot runs this. The map data is whatever is in site/web/public (copied from the live robot by hand).
set -euo pipefail
LAB="$(cd "$(dirname "$0")" && pwd)"
TARGET=https://github.com/Realexis/shroomy-lab.git
OUT="$LAB/.pages"            # local copy of the gh-pages branch (not in the source branch)

cd "$LAB/site/web"
VITE_NOINDEX=1 VITE_COUNTER=off VITE_PREVIEW_LABEL=Lab npm run build
DIST="$LAB/site/web/dist"
grep -q 'name="robots" content="noindex' "$DIST/index.html" || { echo "no noindex, stopping"; exit 1; }
if find "$DIST" -iname "*private*" -o -iname "static_key*" -o -name CNAME | grep -q .; then
  echo "private file or CNAME in the build, stopping"; exit 1; fi
# Past finds (Job 1) go to the public phone copy only when Real said yes: run with PUBLISH_FINDS=1.
if [ "${PUBLISH_FINDS:-0}" != "1" ] && [ -e "$DIST/data/finds.json" ]; then
  rm -f "$DIST/data/finds.json"; echo "finds left out of the phone copy (PUBLISH_FINDS=1 to include them)"; fi

if [ ! -d "$OUT/.git" ]; then
  if git ls-remote --exit-code --heads "$TARGET" gh-pages >/dev/null 2>&1; then
    git clone -q --branch gh-pages "$TARGET" "$OUT"
  else
    mkdir -p "$OUT"; git -C "$OUT" init -q -b gh-pages; git -C "$OUT" remote add origin "$TARGET"
  fi
fi
cd "$OUT"
[ "$(git remote get-url origin)" = "$TARGET" ] || { echo "wrong remote, stopping"; exit 1; }
rsync -a --delete --exclude=.git "$DIST/" ./
touch .nojekyll
git add -A
if git diff --cached --quiet; then echo "nothing new to publish"; exit 0; fi
git -c user.name=Realexis -c user.email=36285588+Realexis@users.noreply.github.com \
  commit -q -m "Lab: built copy $(date +%Y-%m-%d)

Co-Authored-By: Claude Fable 5.2 <noreply@anthropic.com>"
git push -q origin HEAD:gh-pages
echo "✓ published: https://realexis.github.io/shroomy-lab/"
