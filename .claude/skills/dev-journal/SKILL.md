---
name: dev-journal
description: >
  Chronological knowledge for awesome-physical-ai: what shipped (past/), what the
  current focus is (present/narrative.md), what is planned by horizon
  (future/short.md, mid.md, long.md). Live data such as git log and file counts is
  fetched by shell on read, never stored. TRIGGER when: the user asks "what's next",
  "what's left", "what should I add", "what's the backlog", "what shipped", "where
  were we", "what's the current focus", or before proposing a large restructuring so
  it can be cross-checked against planned work. Do NOT trigger for: what a column
  means or why the taxonomy is shaped this way (→ dev-handbook), running the
  validators (→ dev-test).
---

# dev-journal

## Buckets

| Question | Bucket |
|---|---|
| What shipped? | `past/changelog.md` |
| What is the current focus? | `present/narrative.md` |
| What is next session? | `future/short.md` (P0, P1) |
| Planned but not urgent? | `future/mid.md` (P2) |
| Exploratory / someday? | `future/long.md` (P3) |
| What did we run to learn something? | `iterations/<id>/` (empty so far) |

## Present (live data — never stored)

Run these; do not paste their output into markdown.

```sh
git log --oneline -15
git status --short
python3 build.py --check                                 # paper count, arc split, new values
python3 .claude/skills/dev-test/tests/test_database.py   # full validation
python3 -c "
import json,glob
for f in sorted(glob.glob('data/papers/*.json')):
    print(f'{len(json.load(open(f))):3d}  {f}')"
```

To see how the framework groups are currently balanced, open `index.html` and read the
count at the right of each group heading. A group that has swallowed its arc is the
signal that a `pri` needs retuning or a new paper was tagged too generously — see
`../dev-handbook/design-rationale.md`.

## Timestamps

Every entry that records what happened when carries a real timestamp with timezone:
`[2026-08-24 01:30 PDT]` or ISO 8601. This matters if the repo ever gets parallel
branches — timestamps are what let two journals interleave at merge instead of
colliding as one textual conflict.

Does not apply to `future/*.md` items (no event time yet) or to anything in
`../dev-handbook/` (atemporal — it describes the current state).

## Update triggers

| Bucket | When |
|---|---|
| `past/changelog.md` | every commit that changes the framework or adds a batch of papers |
| `present/narrative.md` | when the focus shifts; roughly weekly while active |
| `future/*.md` | when a plan changes, or when a session surfaces work it is not doing now |
| `iterations/<id>/` | once per investigative run, never updated after |

## Themes

No theme files yet. The convention: when the first change of a multi-commit epic lands,
open `present/themes/<id>.md` with a child-change table and exit criteria; when the last
one lands, migrate it to `past/themes/<id>.md` with the decisions it locked. The
likely first theme is the coverage pass described in `future/mid.md`.
