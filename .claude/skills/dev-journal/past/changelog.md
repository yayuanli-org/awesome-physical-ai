# Changelog

Load-bearing changes, newest first. Live git history is `git log --oneline`; this is the
curated layer that says what a change *meant*.

---

## [2026-09-07 14:25 PDT] The repo splits into paper-hub/ and courses/

The knowledge base has two parts now. Everything that sat at the root (`build.py`,
`serve.py`, `data/`, `src/`, the README) moved under `paper-hub/`, unchanged inside.
`courses/umich-26fall-rob599-physically-grounded-ai-agents/` is the first course
folder. It holds a README naming what will land there (syllabus, lecture notebooks,
slides, debates, recordings) and nothing else yet. The root README is one screen that
names both parts.

**The split is what keeps the hub a reference.** `mission.md` lists "the list becomes a
syllabus" as a failure. Course schedules now have a home beside the hub instead of
pressure to become columns in it.

**Nothing on the site changed.** CI runs `python3 paper-hub/build.py` from the repo
root, `build.py` resolves its own paths, and `--site _site` writes the same 12 files.
The tests hang every path off `HUB = ROOT / "paper-hub"`. Course pages are not
published. When the first lecture exists, its export reaches the site through
`emit_site` or a copy step in `pages.yml`, and `test_site_artifact_is_minimal` has to
learn the new files either way.

## [2026-09-07 13:55 PDT] Review markers sit on the content and survive scrolling

Committed on 2026-09-07, but the edits date from 2026-08-24 around 12:00 PDT and sat
uncommitted behind the Pages work that same afternoon. Four files, one idea: a review
comment on this page has to find its target in a three-tab app, and the layer was
written for a single static document.

**Markers ride the anchor's left edge, not the strip to its right.** The vendored
layer parked each pin at `rect.right + 8`, a margin on a prose page and the next
column on a full-bleed table. The pin is now an 18 px dot inside the anchor's own
padding, translucent at rest, and it shows its message count only on hover. Resolved
threads are a hollow ring. The page's rose replaces the layer's amber on anchored
blocks, and comment mode is a rose ring around the viewport rather than louder pins.

**Pins move with whatever scrolls.** Placement is redone on a capture-phase scroll
listener, which is the only kind that hears a nested pane. A pin whose anchor slid
under the sticky header is hidden. This is rect maths on an animation frame; the full
re-render still waits for a mutation or a resize.

**Idle tabs are rendered once at load.** A comment pointing into a tab that has never
been drawn falls back to text matching, and vocabulary labels appear in the rail, the
rows and the table alike, so it landed on the wrong element. `template.html` now fills
the two idle views after first paint. Recorded in `flows/build-pipeline.md`.

**The bridge lost a third of its code.** With the layer hiding pins for boxless
anchors itself, `comment-bridge.js` no longer sweeps them. What remains is the tab
badge on each panel row and the click that switches tab, then polls for the marker
instead of guessing a delay. A smooth scroll was cancelled by the redraw that follows a
tab switch, so the reveal scrolls instantly.

`src/comment-layer.{css,js}` are now a fork of the skill copy, which moved on
independently on 2026-08-30. See `future/mid.md`.

## [2026-08-24 17:55 PDT] Publish the page, privately maintained

The page is live at https://yayuanli-org.github.io/awesome-physical-ai/. The repo is
private and the site is public, which the org plan allows, so `.claude/`, `CLAUDE.md`
and this journal stay unreadable on github.com while the page is readable by anyone.
Nobody outside can fork or open a pull request, which was the trade accepted.

Three things changed to get there, in order of how much they matter.

**Pages deploys an artifact, not the branch.** Serving `main` verbatim published
`build.py`, `serve.py`, `CLAUDE.md` and every file under `.claude/` at the site root.
`build.py --site DIR` now writes the page plus `data/` and nothing else, and
`.github/workflows/pages.yml` deploys that directory. `test_site_artifact_is_minimal`
pins the file list, so a new file in the repo is private until `emit_site` is told
otherwise.

**`index.html` is no longer committed.** 360 KB of generated markup buried every paper
addition under a whole-file diff and went stale behind anyone who forgot to rebuild.
CI builds it on each push. The offline copy moved to tagged releases, which
`.github/workflows/release.yml` cuts on a `v*` tag.

**Pull requests validate without deploying.** Same build, same 23 checks. A malformed
paper entry fails review rather than reaching the page.

One bug worth remembering, because it only appears on a private repo: a job-level
`permissions:` block replaces the workflow-level one instead of merging, so `deploy`
was running without `contents: read`. A public repo checks out anonymously and hid it.
The first run after going private failed with `Repository not found`.

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
