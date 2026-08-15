# CCE public curriculum mirror

This is the generated, public-safe planning mirror for Career and College Explorations. It replaces the legacy MkDocs presentation without creating a second hand-maintained curriculum.

## Product boundary

- **Canvas remains the classroom.** Teacher and Student Guides, assignments, authenticated links, and licensed files stay there.
- **GitHub Pages is the planning mirror.** It exposes the 36-week sequence, public lesson plans, and only the public resources those pages actually link.
- **The build fails closed.** A missing local link, an outside-`docs/resources` binary, or a protected path stops generation.
- **Module IDs are recorded, lesson item IDs are not invented.** `data/module-identities.json` contains the verified 36 Canvas module IDs. A future secure read-only Canvas export can add immutable lesson-item identities without changing the public content model.

## Design direction

The visual system applies Material 3 Expressive principles from the owner's IDK Can You?/HalllDay specification:

- role-based tonal color instead of gradients or decorative color noise;
- Nunito display type with Inter body text;
- purposeful asymmetry and varied corner shapes;
- stillness at rest, restrained state-driven motion, and reduced-motion support;
- a guided curriculum-book structure instead of a dashboard or repetitive card grid.

## Build and verify

```bash
UV_CACHE_DIR=/tmp/cce-site-uv uv run --with markdown --with beautifulsoup4 \
  python public-site/build_site.py

UV_CACHE_DIR=/tmp/cce-site-uv uv run --with beautifulsoup4 \
  python public-site/verify_site.py
```

The build writes `public-site/dist/`, which is ignored locally and uploaded as the GitHub Pages artifact by Actions.

## Publication policy

`publication-policy.json` is part of the build contract. Public pages come only from tracked Markdown under `docs/`. Linked files can be copied only from `docs/resources/`. H&L, FYF, Xello, Climber Notes, private AVID materials, and other authenticated sources remain outside the public artifact.
