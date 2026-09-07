---
name: dev-handbook
description: >
  Logical knowledge for awesome-physical-ai: the schema and what each column means,
  conventions for adding or re-tagging a paper, the design rationale behind the
  taxonomy, the build pipeline, and the full file tree. The "what is it now and why".
  Subfiles load on demand: structure.md, mission.md, conventions.md,
  design-rationale.md, dev-setup.md, flows/add-a-paper.md, flows/build-pipeline.md.
  TRIGGER when: adding or editing a paper entry, changing data/schema.json, editing
  src/template.html, asking "what does column X mean", "why is the taxonomy shaped
  this way", "where should this paper go", "why is there no third section for the
  loop", "how does the build work", or before any non-trivial change to the data or
  the page. Do NOT trigger for: what shipped or what is next (→ dev-journal), running
  the validators (→ dev-test).
---

# dev-handbook

## Universal conventions

The full list is in `conventions.md`. The ones that apply to every single edit:

- **Rows are papers, columns are dimensions, sections are filters.** Never introduce a
  folder, a `section:` field, or a hand-assigned bucket. If a grouping cannot be
  expressed as a filter over columns, the columns are wrong.
- **Comprehensive structure, short cells.** Every column exists for every paper. No
  cell runs past a sentence or two. Detail stays in the paper being described.
- **Categories where the world is small, prose where it is rich.** `modality` is a
  closed vocabulary because there are only so many modalities. What the content
  actually is, and why a method works, are free text.
- **Never fabricate a number.** Every figure in `experiments.headline` must appear in
  the paper's own abstract or be arithmetic on figures that do. `dev-test` checks this
  is at least plausible; you are the real check.
- **`confidence: "medium"`** means grounded in the abstract but not read end to end.
  Use it honestly. It is rendered on the page.
- **The hub is `paper-hub/`, the courses are `courses/`, and nothing flows from the
  second into the first.** A schedule or an assignment is never a column.
- **Prose voice is the `Plain` output style, and a test enforces the mechanical part.**
  No semicolon or em-dash welding two independent clauses, no antithesis reflex, no
  blacklist vocabulary.

## Where to find what

| Question | File |
|---|---|
| Where does file X live? What is the full tree? | `structure.md` |
| What is this repo for, over the next few months? | `mission.md` |
| Why is the taxonomy shaped this way? What was rejected? | `design-rationale.md` |
| What are the rules for a data edit? | `conventions.md` |
| How do I add a paper? | `flows/add-a-paper.md` |
| How does `build.py` turn data into the page? | `flows/build-pipeline.md` |
| How do I set up and run this? | `dev-setup.md` |
| What shipped / what is next? | `../dev-journal/SKILL.md` (different skill) |
| How do I run the validators? | `../dev-test/SKILL.md` (different skill) |

## The schema in one screen

`data/schema.json` holds four things. Read it before any data edit.

1. **`thesis`** — the one-line claim and the paragraph under it, rendered at the top
   of the page. Physical AI = how the physical world gets changed in the age of AI.
   Two moves (model, change), closing into a loop.
2. **`views`** — the three page sections. Each has a `filter` (which papers belong)
   and `groups` (each with its own `filter`, a `sub` blurb, and a `pri`). Array order
   is reading order; `pri` is assignment order, most specific first.
3. **`fields`** — the columns. Each has `key`, `label`, `kind`
   (`single` / `multi` / `bool`), `axis` (`topic` / `meta`), `facet` (does it appear
   in the filter rail), `help`, and a `vocab` where the vocabulary is closed.
4. **`reading_protocol`** and **`modalities`** and **`data_roles`** — the per-paper
   reading discipline and the two closed vocabularies used inside `problem` and
   `experiments`.

The 13 physical-AI axes: `arc`, `loop_stage`, `closes_loop`, `embodiment`,
`human_role`, `world_facet`, `representation`, `change_channel`, `sensing`, `regime`,
`horizon`, `domain`, `autonomy`. Plus `contribution` and `openness` on the meta axis.

## When to update this skill

| Change kind | Updates |
|---|---|
| File or directory added, renamed, removed | `structure.md` (refresh, bump the date), and `CLAUDE.md`'s folder map |
| New column, new vocabulary value, view retuned | `design-rationale.md` + `conventions.md` |
| New rule for how a paper is written | `conventions.md`, and add an enforcing check in `../dev-test/` |
| Build pipeline changed | `flows/build-pipeline.md` |
| Strategic direction changed | `mission.md` |
