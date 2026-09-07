# Structure

Full tree with line counts. CLAUDE.md keeps only the top-level map and points here,
so this file is what makes that pointer real.

_Generated [2026-09-07 14:19 PDT]. Regenerate with the recipe at the bottom._

```
 lines  path
------  ----------------------------------------------------------

    83  .claude/skills/dev-handbook/SKILL.md
    98  .claude/skills/dev-handbook/conventions.md
   127  .claude/skills/dev-handbook/design-rationale.md
    63  .claude/skills/dev-handbook/dev-setup.md
    93  .claude/skills/dev-handbook/flows/add-a-paper.md
   109  .claude/skills/dev-handbook/flows/build-pipeline.md
    50  .claude/skills/dev-handbook/mission.md
    95  .claude/skills/dev-handbook/structure.md
    72  .claude/skills/dev-journal/SKILL.md
    14  .claude/skills/dev-journal/future/long.md
    22  .claude/skills/dev-journal/future/mid.md
    13  .claude/skills/dev-journal/future/short.md
   154  .claude/skills/dev-journal/past/changelog.md
    37  .claude/skills/dev-journal/present/narrative.md
    75  .claude/skills/dev-test/SKILL.md
   398  .claude/skills/dev-test/tests/test_database.py

    63  .github/workflows/pages.yml
    33  .github/workflows/release.yml

    20  .gitignore
   110  CLAUDE.md
    16  README.md

    16  courses/umich-26fall-rob599-physically-grounded-ai-agents/README.md

   187  paper-hub/README.md
   173  paper-hub/build.py
  1727  paper-hub/data/papers/01-world-models.json
  1656  paper-hub/data/papers/02-objects-scenes-physics.json
  1165  paper-hub/data/papers/03-egocentric-procedural-data.json
  1114  paper-hub/data/papers/04-procedure-structure.json
  1600  paper-hub/data/papers/05-human-embodiment.json
   801  paper-hub/data/papers/06-verify-mistakes.json
  1969  paper-hub/data/papers/07-robot-embodiment.json
  1704  paper-hub/data/papers/08-human-to-robot-and-together.json
   473  paper-hub/data/papers/09-scenes-4d-physics-checks.json
   685  paper-hub/data/papers/10-guidance-skill-fabrication.json
   879  paper-hub/data/schema.json
   933  paper-hub/index.html
  2181  paper-hub/review.html
    84  paper-hub/serve.py
   120  paper-hub/src/comment-bridge.js
   230  paper-hub/src/comment-layer.css
   889  paper-hub/src/comment-layer.js
   933  paper-hub/src/template.html

 21264  TOTAL across 42 files
```

## What each thing is

| Path | Role |
|---|---|
| `README.md` | The two parts, one paragraph each. |
| `CLAUDE.md` | Loaded every session. Overview, entry point, universal gotchas, map. |
| `paper-hub/` | Part one: the database, the page, and the code that builds and serves it. |
| `paper-hub/index.html` | The deliverable. Self-contained, no review scaffolding. Generated, not committed. |
| `paper-hub/review.html` | The same page plus the comment layer, for marking the draft up. Generated, not committed. |
| `paper-hub/build.py` | Reads `data/` and `src/` beside it, validates, emits both pages. Resolves its own paths, so it runs from any cwd. |
| `paper-hub/serve.py` | Localhost static server plus a comment write-back API for `review.html`. Serves its cwd, so run it from `paper-hub/`. |
| `paper-hub/README.md` | User-facing: what the hub is, how to add a paper. |
| `paper-hub/data/schema.json` | The taxonomy. Columns, vocabularies, views, reading protocol. |
| `paper-hub/data/papers/NN-*.json` | The database. Split by topic; the prefix orders nothing at runtime. |
| `paper-hub/src/template.html` | The whole client: CSS, markup shell, one IIFE, four placeholders. |
| `paper-hub/src/comment-layer.{css,js}` | Vendored from the `commentable-html` skill, then forked (marker placement, see the journal). Re-copying overwrites the fork. |
| `paper-hub/src/comment-bridge.js` | Ours. Reconciles the comment layer with this page's tab switching. |
| `courses/` | Part two: one folder per course. Course material never feeds the hub's data. |
| `courses/umich-26fall-rob599-physically-grounded-ai-agents/` | ROB 599, Fall 2026. Its README names what lands there: syllabus, lecture notebooks, slides, debates, recordings. |
| `.github/workflows/pages.yml` | Validate on every push and pull request, deploy `_site/` on push to main. |
| `.github/workflows/release.yml` | On a `v*` tag, attach a standalone page and a data zip to a release. |
| `.claude/skills/dev-handbook/` | Logical: what it is and why. |
| `.claude/skills/dev-journal/` | Chronological: shipped, current, planned. |
| `.claude/skills/dev-test/` | The validation surface. Tests point at `paper-hub/` through `HUB`. |

## What is elided

`.git`, `__pycache__`, `.pytest_cache`, `.venv`, `node_modules`, `_site`,
`.ipynb_checkpoints`, `.DS_Store`, `*.pyc`, `*.bak`, and `*.comments.json` (review
comments, written by `serve.py` at runtime). Nothing else. There are no build caches,
lockfiles or dependency stores, because the project has no dependencies.

Two counts here mislead and are worth naming. Line counts for the JSON data files are a
formatting artifact rather than a content measure; the useful count is papers, from
`python3 paper-hub/build.py --check`. And `index.html` and `review.html` report small
line counts for large files because the inlined database is one very long line.

## Regenerate

The generator is inline in the commit that last regenerated this file: walk the tree,
skip the elided set above, count lines per file, group by top-level directory. Refresh
whenever a directory is added, renamed or removed.

```sh
git log --format=%H -1 -- .claude/skills/dev-handbook/structure.md
```
