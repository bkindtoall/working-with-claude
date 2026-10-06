#!/bin/bash
# Rebuild both copies from index.html, commit, push. GitHub Pages and the
# craftingmetrics.com embed pick up the change within a few minutes.
#   ./publish.sh "What changed"
set -euo pipefail
cd "$(dirname "$0")"
python3 build.py
git add -A
if git diff --cached --quiet; then echo "Nothing changed."; exit 0; fi
git commit -q -m "${1:-Update logbook}" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
git push -q
git log -1 --format='Pushed %h: %s'
