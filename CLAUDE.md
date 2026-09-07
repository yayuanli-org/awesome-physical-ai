# CLAUDE.md

## Overview

`awesome-physical-ai` — a knowledge base for physical AI in two parts. `paper-hub/`
is a paper database rendered as one self-contained HTML page, and it is the public
site. `courses/` holds one folder per course that reads the hub and debates it,
starting with **ROB 599, Physically-Grounded AI Agents** (UMich, Fall 2026). The data
is the product, the page is a view over it, and the hub is written to outlive any course.

## Entry point — `python3 paper-hub/build.py`

```
paper-hub/data/schema.json + data/papers/*.json ─┐
                                                  ├─→ build.py ─┬─→ paper-hub/index.html   (deliverable)
paper-hub/src/template.html + src/comment-*.{css,js} ─┘        ├─→ paper-hub/review.html  (+ comment layer)
                                                                └─→ _site/                 (what CI deploys)
```

- `python3 paper-hub/build.py` — write both pages. Paths resolve from the script, so any cwd works.
- `python3 paper-hub/build.py --check` — validate and report only, write nothing
- `python3 paper-hub/build.py --site _site` — assemble the deploy artifact, touching neither page
- `python3 .claude/skills/dev-test/tests/test_database.py` — the full test surface
- `open paper-hub/index.html` — the deliverable; no server, no network, no dependencies
- `cd paper-hub && python3 serve.py` then open `review.html` — mark the draft up in the browser
- No lint or format script. Python is stdlib-only.
- `courses/` has no build step. Lecture notes are Jupyter notebooks made with the `doc-jupyter` skill.

## Publishing — `.github/workflows/pages.yml`

`main` is the site, live at https://yayuanli-org.github.io/awesome-physical-ai/.
Push to main and CI builds, tests and deploys. Open a pull request and CI runs the
same tests without deploying. Nothing is published by hand.

**The site is the hub only.** `_site/` holds the page and the raw database. Nothing
under `courses/` is published yet; when the first lecture exists, add its export to
`emit_site` or a copy step in the workflow, and update `test_site_artifact_is_minimal`.

**The repo is public, and so is the site.** Everything in the tree is readable by
anyone, `.claude/` and the journal included, and both have been in history since the
first documentation commit. The site is still only what `_site/` holds.

**`dev` validates, `main` deploys.** A push to `dev` runs the build and the tests and
stops. Only a push to `main` publishes.

## Universal gotchas

- **Never edit `paper-hub/index.html` or `paper-hub/review.html`.** Both are generated
  from one template and neither is committed. Edit `paper-hub/data/` or `paper-hub/src/`
  and rebuild, or your change is gone on the next build. A fresh clone has no page until
  `python3 paper-hub/build.py` runs.
- **`courses/` is not the list.** Schedules, lecture numbers and assignments live there,
  never as fields in `paper-hub/data/`. That split is what keeps the hub a reference.
- **A job-level `permissions:` block in a workflow replaces the workflow-level one, it
  does not merge.** The `deploy` job needs its own `contents: read` or checkout fails
  with `Repository not found`. A public repo checks out anonymously and hides this, so
  the failure only appears while the repo is private, which it was when this was found.
- **Actions minutes are free on a public repo and billed on a private one.** The
  workflow stays one job either way, about a minute per push.
- **The public site is what `--site` writes, not the repo tree.** GitHub Pages deploys
  the `_site/` artifact, so adding a file to the repo does not publish it and `.claude/`
  stays private-by-omission. To publish something new, add it to `emit_site` in
  `paper-hub/build.py`.
- **Review scaffolding never reaches the deliverable.** The comment layer is inlined
  into `review.html` only; `index.html` gets the three `__PHYSAI_REVIEW_*` placeholders
  stripped. A test enforces it.
- **Sections are filters over columns, never folders.** A paper that models the world
  and changes it carries both `arc` values and appears in both arcs. There is no
  "which section does this go in" question — only "which column values are true".
- **Group display order ≠ group assignment order.** Framework groups carry a `pri`
  field; the array order is editorial, `pri` decides which group claims a paper first.
  Reordering the array without checking `pri` silently rebalances every bucket.
- **Prose voice is enforced by a test**, not by taste. No semicolons welding two
  clauses, no "not just X but Y", no blacklist words. See `dev-handbook/conventions.md`.
- **`review.html` needs `serve.py` run from inside `paper-hub/`, not `file://`.**
  Comments only persist to disk over http, and `serve.py` serves and writes in its cwd.
  Opened from a filesystem the layer falls back to `localStorage`.

## Folder map

```
teaching_umich_physical_ai/
├── README.md             — the two parts, one paragraph each
├── paper-hub/
│   ├── index.html        — built artifact, the deliverable (never hand-edit)
│   ├── review.html       — built artifact, same page + comment layer, for markup
│   ├── build.py          — inlines data into the template, emits both pages
│   ├── serve.py          — localhost static server + comment write-back for review.html
│   ├── README.md         — user-facing: what the hub is, how to add a paper
│   ├── data/
│   │   ├── schema.json   — the taxonomy: columns, vocabularies, views, protocol
│   │   └── papers/*.json — the database, split into topical chunks [→ dev-handbook]
│   └── src/
│       ├── template.html — page shell: CSS, JS, and the four placeholders
│       ├── comment-layer.* — vendored review layer, review.html only [→ dev-handbook]
│       └── comment-bridge.js — ours: reconciles the layer with this page's tabs
├── courses/
│   └── umich-26fall-rob599-physically-grounded-ai-agents/
│       └── README.md     — syllabus, lectures/, slides/, debates/, recordings, as they land
└── .claude/skills/
    ├── dev-handbook/     — logical: structure, conventions, rationale, flows
    ├── dev-journal/      — chronological: past, present, future
    └── dev-test/         — the validation surface
```

## Skills

- `.claude/skills/dev-handbook/` — how the schema works, why it is shaped this way,
  conventions for adding a paper, the full file tree
- `.claude/skills/dev-journal/` — what shipped, current focus, what is next
- `.claude/skills/dev-test/` — schema, coverage, and prose-voice validation
