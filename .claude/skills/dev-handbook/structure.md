# Structure

Full tree with line counts. CLAUDE.md keeps only the top-level map and points here,
so this file is what makes that pointer real.

_Generated [2026-08-24 11:31 PDT]. Regenerate with the recipe at the bottom._

```
 lines  path
------  ----------------------------------------------------------

    83  .claude/skills/dev-handbook/SKILL.md
    96  .claude/skills/dev-handbook/conventions.md
   127  .claude/skills/dev-handbook/design-rationale.md
    63  .claude/skills/dev-handbook/dev-setup.md
    93  .claude/skills/dev-handbook/flows/add-a-paper.md
    64  .claude/skills/dev-handbook/flows/build-pipeline.md
    50  .claude/skills/dev-handbook/mission.md
    96  .claude/skills/dev-handbook/structure.md
    72  .claude/skills/dev-journal/SKILL.md
    14  .claude/skills/dev-journal/future/long.md
    15  .claude/skills/dev-journal/future/mid.md
    12  .claude/skills/dev-journal/future/short.md
    92  .claude/skills/dev-journal/past/changelog.md
    33  .claude/skills/dev-journal/present/narrative.md
    74  .claude/skills/dev-test/SKILL.md
   377  .claude/skills/dev-test/tests/test_database.py

    70  CLAUDE.md
   129  README.md
   135  build.py

  1727  data/papers/01-world-models.json
  1656  data/papers/02-objects-scenes-physics.json
  1165  data/papers/03-egocentric-procedural-data.json
  1114  data/papers/04-procedure-structure.json
  1600  data/papers/05-human-embodiment.json
   801  data/papers/06-verify-mistakes.json
  1969  data/papers/07-robot-embodiment.json
  1704  data/papers/08-human-to-robot-and-together.json
   473  data/papers/09-scenes-4d-physics-checks.json
   685  data/papers/10-guidance-skill-fabrication.json
   879  data/schema.json

   909  index.html
  2056  review.html
    84  serve.py

   107  src/comment-bridge.js
   192  src/comment-layer.css
   839  src/comment-layer.js
   909  src/template.html

 20564  TOTAL across 37 files
```

## What each thing is

| Path | Role |
|---|---|
| `index.html` | The deliverable. Self-contained, no review scaffolding. Generated. |
| `review.html` | The same page plus the comment layer, for marking the draft up. Generated. |
| `build.py` | Reads `data/` and `src/`, validates, emits both pages. |
| `serve.py` | Localhost static server plus a comment write-back API for `review.html`. |
| `README.md` | User-facing: what the list is, how to add a paper. |
| `CLAUDE.md` | Loaded every session. Overview, entry point, universal gotchas, map. |
| `data/schema.json` | The taxonomy. Columns, vocabularies, views, reading protocol. |
| `data/papers/NN-*.json` | The database. Split by topic; the prefix orders nothing at runtime. |
| `src/template.html` | The whole client: CSS, markup shell, one IIFE, four placeholders. |
| `src/comment-layer.{css,js}` | Vendored from the `commentable-html` skill. Upgrade by re-copying. |
| `src/comment-bridge.js` | Ours. Reconciles the comment layer with this page's tab switching. |
| `.claude/skills/dev-handbook/` | Logical: what it is and why. |
| `.claude/skills/dev-journal/` | Chronological: shipped, current, planned. |
| `.claude/skills/dev-test/` | The validation surface. |

## What is elided

`.git`, `__pycache__`, `.pytest_cache`, `.venv`, `node_modules`, `.DS_Store`, `*.pyc`,
`*.bak`, and `*.comments.json` (review comments, written by `serve.py` at runtime).
Nothing else. There are no build caches, lockfiles or dependency stores, because the
project has no dependencies.

Two counts here mislead and are worth naming. Line counts for the JSON data files are a
formatting artifact rather than a content measure; the useful count is papers, from
`python3 build.py --check`. And `index.html` and `review.html` report small line counts
for large files because the inlined database is one very long line.

## Regenerate

The generator lives in git history for the commit that created this file. It walks the
tree, skips the elided set above, counts lines per file, and groups by top-level
directory. Refresh whenever a directory is added, renamed or removed.

```sh
git log --diff-filter=A --format=%H -1 -- .claude/skills/dev-handbook/structure.md
```
