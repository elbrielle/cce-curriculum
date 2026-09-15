#!/usr/bin/env bash
# Build every deck for one week, full and public twin, then run the QA gate on each.
#   build/slides/build_week.sh 1sw-wk3
set -euo pipefail
WEEK="$1"; HERE="$(cd "$(dirname "$0")" && pwd)"; ROOT="$(cd "$HERE/../.." && pwd)"
cd "$HERE/$WEEK"
for f in day*.js; do
  node "$f"
  CCE_PUBLIC=1 node "$f"
done
cd "$ROOT"
for f in docs/resources/slides/${WEEK}-day*.pptx; do
  python3 build/slides/qa_deck.py "$f" | tail -1 | sed "s|^|$(basename "$f"): |"
done
for f in docs/resources/slides/public/${WEEK}-day*.pptx; do
  python3 build/slides/qa_deck.py "$f" --out ".tmp/deck-qa/public-$(basename "$f" .pptx)" | tail -1 | sed "s|^|public/$(basename "$f"): |"
done
