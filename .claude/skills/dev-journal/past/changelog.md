# Changelog

Load-bearing changes, newest first. Live git history is `git log --oneline`; this is the
curated layer that says what a change *meant*.

---

## [2026-08-24 11:30 PDT] Bootstrap the `.claude` scaffold and the test surface

Added `CLAUDE.md`, `dev-handbook/`, `dev-journal/`, `dev-test/`. The handbook captures
what was decided and rejected while building the framework; without it the reasoning
lived only in one session's context.

The test surface is the piece that changes how the repo behaves. 21 checks in one
stdlib-only script enforce the mechanizable half of the conventions. Writing it
immediately caught violations the human pass had missed:

- Two antithesis constructions and two semicolon welds in the papers added last
  (`humoto`, `web2grasp`, `narrated-videos-3d`).
- Two semicolons in `schema.json`'s own help text, which renders on the page.
- Four blacklist words ("novel objects", "robust to perturbation") sitting in
  `experiments.headline` paraphrases. Rewriting them to "unseen objects" and "hold up
  under perturbation" is more precise as well as compliant.
- `tokens` used as a modality but never declared in `schema.modalities`.

Two of the checks were themselves wrong on the first run and are worth remembering:
a *pair* of em-dashes is a legitimate parenthetical and only a lone one welds clauses;
and Python's `str(True)` is `"True"` while the page's `String(true)` is `"true"`, which
made the whole loop view look empty to the validator.

## [2026-08-24 11:29 PDT] Review page split out of the deliverable

Landed by a parallel session in this directory while the scaffold was being written.
Worth recording because it changed the build contract.

`build.py` now emits two pages from one template. `index.html` stays the deliverable —
self-contained, no server, nothing beside it. `review.html` is the same page with the
`commentable-html` layer inlined, so the draft can be marked up in a browser before it
ships. Three placeholders (`__PHYSAI_REVIEW_ATTRS__`, `_CSS_`, `_JS_`) are filled for
one page and stripped for the other.

The layer is inlined rather than linked, for the same reason the database is: both
pages have to work from a filesystem. `src/comment-layer.{css,js}` are vendored from
the skill; `src/comment-bridge.js` is ours and reconciles the layer with this page's
tab switching, since comment anchors have to survive a view change. `serve.py` at root
persists comments to `physai.comments.json`, which is what makes them survive a session.

Caught mid-flight: for a few minutes the template referenced three sibling files that
had just been moved into `src/`, and `test_page_is_self_contained` failed. Two lessons
recorded rather than fixed, because both were transient — a second session can leave
the tree in a state no commit should capture, and the test surface is what made that
visible within seconds instead of after a push.

Added `test_review_scaffolding_is_stripped` to make the new contract enforceable, and
extended `test_build_is_current` to check both pages are deterministic. 22 checks now.

## [2026-08-24 01:30 PDT] Framework v0.1 and 110 papers

The initial build. Deliverable is `index.html`, one self-contained page over a JSON
database.

**The taxonomy.** Physical AI as two arcs — model the world, change it through an
embodiment — with the loop as a cross-section rather than a third section. 13 topic
axes plus `contribution` and `openness`. Every section on the page is a filter over
columns; there are no folders in the data. Rationale and rejected alternatives are in
`../../dev-handbook/design-rationale.md`.

**The reading protocol.** Per-paper structure follows the paper minus intro and related
work: problem setting with per-component modality, tensor shape and content
characteristics; method intuition in one or two sentences; experiments with what was
done to each dataset. Rendered as the page's third tab.

**Two design corrections found by measurement, not by argument:**

- An objects group in the modeling arc claimed 26 of 45 papers, because
  `world_facet: object-state` is true of nearly everything. Object-centricity became
  the arc's premise, stated in the blurb, and the group narrowed to the four papers
  where the object representation is the contribution.
- First-match-wins over the group array produced buckets of 26 / 9 / 3 / 0 / 0 / 0.
  Splitting display order from assignment order via a `pri` field fixed it without
  changing the reading order.

**The papers.** 110 entries, 2018–2026, seeded from the maintainer's ~400 captured
papers in org-roam plus canon. Grounded against ~290 abstracts pulled from the arXiv
API rather than written from memory. A numeric audit compared every figure in an
`experiments.headline` against its source abstract: six mismatched, four were false
positives, two were real and fixed (ALOHA's "$20k", PhysObjects' "457K").

An audit of vocabulary values with zero papers found two — `change_channel:
fabrication` and `human_role: evaluator`. Both were filled rather than deleted, and
`human_role` was promoted from single-select to multi-select so a person can be both
guided and judging. That audit is now `test_no_empty_vocabulary_values`.
