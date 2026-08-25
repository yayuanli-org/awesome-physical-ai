# CLAUDE.md

## Overview

`awesome-physical-ai` — a paper database for physical AI, rendered as one
self-contained HTML page. Draft deliverable for **ROB 599, Physically-Grounded AI
Agents** (UMich, Fall 2026), built to outlive the course as a public reference.
The data is the product; the page is a view over it.

## Entry point — `python3 build.py`

```
data/schema.json + data/papers/*.json ─┐
                                       ├─→ build.py ─┬─→ index.html   (deliverable)
src/template.html + src/comment-*.{css,js} ─────────┴─→ review.html   (+ comment layer)
                                                     └─→ _site/       (what CI deploys)
```

- `python3 build.py` — write both pages
- `python3 build.py --check` — validate and report only, write nothing
- `python3 build.py --site _site` — assemble the deploy artifact, touching neither page
- `python3 .claude/skills/dev-test/tests/test_database.py` — the full test surface
- `open index.html` — the deliverable; no server, no network, no dependencies
- `python3 serve.py` then open `review.html` — mark the draft up in the browser
- No lint or format script. Python is stdlib-only.

## Publishing — `.github/workflows/pages.yml`

`main` is the site, live at https://yayuanli-org.github.io/awesome-physical-ai/.
Push to main and CI builds, tests and deploys. Open a pull request and CI runs the
same tests without deploying. Nothing is published by hand.

**The repo is private and the site is public.** The org plan allows a private repo to
publish a public Pages site, which is what keeps `.claude/`, `CLAUDE.md` and the
journal off github.com while the page stays readable by anyone. Outsiders cannot fork
or open a pull request, by choice — suggestions arrive as issues or email.

## Universal gotchas

- **Never edit `index.html` or `review.html`.** Both are generated from one template
  and neither is committed. Edit `data/` or `src/` and rebuild, or your change is gone
  on the next build. A fresh clone has no page until `python3 build.py` runs.
- **A job-level `permissions:` block in a workflow replaces the workflow-level one, it
  does not merge.** The `deploy` job needs its own `contents: read` or checkout fails
  with `Repository not found`. A public repo checks out anonymously and hides this, so
  the failure only appears once the repo is private.
- **Actions minutes are billed now that the repo is private.** Public repos run free.
  Each push costs about a minute of runner time, which is why the workflow does not
  fan out over a matrix.
- **The public site is what `--site` writes, not the repo tree.** GitHub Pages deploys
  the `_site/` artifact, so adding a file to the repo does not publish it and `.claude/`
  stays private-by-omission. To publish something new, add it to `emit_site` in
  `build.py`.
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
- **`review.html` needs `serve.py`, not `file://`.** Comments only persist to disk
  over http. Opened from a filesystem the layer falls back to `localStorage`.

## Folder map

```
teaching_umich_physical_ai/
├── index.html            — built artifact, the deliverable (never hand-edit)
├── review.html           — built artifact, same page + comment layer, for markup
├── build.py              — inlines data into the template, emits both pages
├── serve.py              — localhost static server + comment write-back for review.html
├── README.md             — user-facing: what it is, how to add a paper
├── data/
│   ├── schema.json       — the taxonomy: columns, vocabularies, views, protocol
│   └── papers/*.json     — the database, split into topical chunks [→ dev-handbook]
├── src/
│   ├── template.html     — page shell: CSS, JS, and the four placeholders
│   ├── comment-layer.*   — vendored review layer, review.html only [→ dev-handbook]
│   └── comment-bridge.js — ours: reconciles the layer with this page's tabs
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
