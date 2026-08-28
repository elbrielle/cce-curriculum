# Week 1 agentic deck pipeline

This folder is the production experiment selected for the Week 1 rebuild. It uses a local semantic deck specification, editable native PowerPoint objects, and a small rendered background layer for polish. It does not require a paid slide-generation service.

## Build contract

- `build.mjs` owns the five day-level narrative and layout maps.
- All instructional text, screenshots, timers, checklists, and speaker notes remain editable PowerPoint objects.
- `backgrounds.html` and `render_backgrounds.mjs` create decorative PNG backgrounds only.
- `quality-config.json` drives the fail-closed OOXML/layout audit.
- Final files are promoted only after the structural gate, overflow test, and full-size render review all pass.

## Runtime setup

Load the Codex workspace dependencies first. The bundled presentation helpers require all four variables below; omitting them causes the renderer and overflow test to stop before QA.

```bash
export CODEX_PRESENTATIONS_RUNTIME_HELPER="<presentations-skill>/container_tools/runtime_helpers.mjs"
export RUNTIME_NODE="<workspace-dependencies>/node/bin/node"
export RUNTIME_NODE_MODULES="<workspace-dependencies>/node/node_modules"
export RUNTIME_BIN_DIR="<workspace-dependencies>/bin/override"
```

## Rebuild and gate

```bash
"$RUNTIME_NODE" build/decks/1sw-wk1-agentic/build.mjs

for day in 1 2 3 4 5; do
  "$RUNTIME_NODE" build/decks/lib/deck_quality_gate.mjs \
    --layout-dir "tmp/1sw-wk1-agentic-preview/day${day}/layout" \
    --pptx "tmp/1sw-wk1-agentic-preview/day${day}/cce-1sw-wk1-day${day}-manufacturing-agentic.pptx" \
    --config build/decks/1sw-wk1-agentic/quality-config.json \
    --json "tmp/1sw-wk1-agentic-preview/day${day}/quality.json"
done
```

Then run `render_slides.py`, inspect every slide at full size, and run `slides_test.py` from the same presentation skill. Both inherit `RUNTIME_NODE`, `RUNTIME_NODE_MODULES`, and `RUNTIME_BIN_DIR`.

## Distribution boundary

Canvas and the raw Drive PowerPoint releases may be updated from the gated PPTX. Replacing a native Google Slides master from PPTX while preserving its existing ID requires an import-first browser workflow: back up the native deck, import all new slides, verify the new range, then remove the old range. The current Drive connector cannot perform that conversion in place.
