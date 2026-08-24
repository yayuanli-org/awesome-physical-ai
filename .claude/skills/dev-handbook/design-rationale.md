# Design rationale

Locked decisions and what was rejected. Written 2026-08-24. Each entry says what was
chosen, what it was chosen over, and what would have to change to reopen it.

## The database is the product; the page is a view

**Locked.** Under the page is a table. Papers are rows, dimensions are columns, and
every section on the site is a filter over those columns.

Rejected: the usual awesome-list shape, a nested markdown outline with papers filed
under headings. It forces a single home per paper, which is false for most of them —
a VLA paper is a modeling paper and a changing paper at once — and it makes any
cross-cutting question ("show me everything that closes the loop") unanswerable
without re-reading the whole list.

Consequence: there is no `section` field anywhere in `data/papers/*.json`, and there
never should be. If a grouping cannot be written as a filter, the columns are wrong.

## Two arcs, and the loop is a cross-section

**Locked.** `model` and `change` are the two top-level arcs. Closing the loop is the
third *view* but not a third topic: it filters on `closes_loop: true` and every paper
in it already appeared above.

Considered and rejected: a third section for closed-loop systems. It would have
duplicated the arc content and implied that "loop" is a kind of paper rather than a
property of one. The property is carried instead by two columns — `closes_loop`
(boolean) and `loop_stage` (multi-select over sense / represent / anticipate / decide
/ act / verify / adapt).

The `loop_stage` column is what makes the parallel visible: procedural mistake
detection in a human-embodied system and VLA failure detection in a robot-embodied
one are the same `verify` stage in different embodiments. Those two literatures barely
cite each other, and the column is the argument that they should.

## Object-centricity is the premise of the model arc, not a bucket inside it

**Locked, and it was the hardest call.**

The original plan gave objects their own group in the modeling arc. Measured: it
claimed 26 of 45 papers, because `world_facet: object-state` is true of nearly
everything. A group that holds more than half its arc is not a group.

What shipped: the arc blurb carries the premise ("the world is objects and the changes
they undergo"), and the group named "Objects: identity, state, and change" holds only
the papers where the object representation *is* the contribution — currently DINOv2,
SAM 2, Object Concepts from Motion, 4D-LRM. Four papers, precisely chosen.

Reopen this if `world_facet` is ever split into "primary" and "secondary" facets. That
would let the group be both prominent and non-swallowing, at the cost of a judgment
call per paper.

## Group display order is separate from group assignment order

**Locked.** Every group in `schema.json` carries a `pri` integer. The array order is
the reading order on the page; `pri` is the order in which groups claim papers,
most specific first.

Without it, first-match-wins over the array produced 26 / 9 / 3 / 0 / 0 / 0 across the
modeling groups. With it, the same groups in the same reading order come out roughly
balanced. `renderFramework` in `src/template.html` sorts by `pri` to assign, then
renders in array order.

Rejected: a hand-assigned `primary_group` field per paper. It is more machinery,
it rots when the views change, and it reintroduces the folder problem through a
back door.

## One self-contained HTML file, built from JSON

**Locked.** `build.py` inlines `schema.json` and every `papers/*.json` into
`src/template.html` at a `__PHYSAI_DATA__` placeholder and writes `index.html`.

Rejected: fetching `papers.json` at runtime. Chrome blocks `fetch` over `file://`, and
the whole point is that the page opens from a filesystem with no server, no network
and no dependencies. Also rejected: a static site generator. The page is one file and
one template; a framework would be more moving parts than content.

Consequence: `index.html` is a build artifact and must never be hand-edited. It is
committed anyway, because the deliverable is the file itself.

## Categories where the world is small, prose where it is rich

**Locked.** `modality` is a closed vocabulary because there are only so many
modalities. "What the content actually is" for a given input, and "why this method
works", are free text, because compressing them into a label destroys exactly the
information a reader came for.

The hybrid shows up in `experiments.datasets`: each entry has a closed `role`
(`existing` / `reannotated` / `remix` / `new` / `synthetic` / `real-robot`) plus a free
`name`. What a paper did to its data is often the real contribution, and it is a small
enough space to enumerate.

## An axis with no members is an untested claim

**Locked as a check, not just a habit.** After the first pass, `change_channel:
fabrication` and `human_role: evaluator` had zero papers. A vocabulary value nobody
uses is a claim about the field that the list has not tested.

Both were filled rather than deleted — BrickGPT for fabrication, and `human_role` was
promoted from single-select to multi-select so that a paper can record a person as
both the one being guided and the one judging the result. `dev-test` now fails on any
empty vocabulary value, so the next one is caught at build time.

## The reading protocol follows the paper, minus the parts about other papers

**Locked.** Introduction is a compressed abstract and related work is a map of the
field, so both are skipped. What is left is the shape of every `problem` / `method` /
`experiments` block:

- **Problem setting** — the function the paper computes at inference. Every input and
  output gets a `modality`, a `tensor` shape, and one line on what the content
  actually is. Training is recorded where it differs, because the interesting design
  choices hide in that difference.
- **Method** — one or two sentences of intuition, the claim the architecture is an
  argument for. Then components. A data engine counts as a method.
- **Experiments** — datasets and what was done to them, metrics, baselines, one
  headline number.

## Venue and institution are best-effort, and say so

**Locked.** Venue records the best verifiable source, usually the arXiv `comment`
field. A paper listed as `arXiv` may have been published since. Institutions are left
empty where the author list did not make them certain rather than guessed.

The alternative — inferring affiliations from author names — produces confident errors
in a public artifact. An empty cell is honest; a wrong one is not.
