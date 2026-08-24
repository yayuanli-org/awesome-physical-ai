# Conventions

"Use X, not Y" rules. Every rule here either has an enforcing check in
`../dev-test/tests/test_database.py` or an explicit note saying why it cannot be
mechanized.

## Data

- **Use a column, not a folder.** No `section`, `category`, or `group` field on a
  paper. Grouping is expressed in `schema.json` views as a filter.
  *Enforced:* `test_no_grouping_fields`.
- **Use a slug id, not a title.** `id` is kebab-case, unique, stable. It is the
  deep-link anchor (`index.html#paper-id`), so renaming one breaks a link someone saved.
  *Enforced:* `test_ids_unique_and_slugged`.
- **Use `date: "YYYY-MM"`, not a bare year.** `year` is also required, and the two must
  agree. Sorting is on `date`.
  *Enforced:* `test_dates_consistent`.
- **Add a vocabulary value to `schema.json` before using it.** `build.py` reports
  unknown values as a notice rather than an error, on purpose — the vocabulary is meant
  to grow. But it grows in the schema first, with a `label` and usually a `help`.
  *Enforced:* `test_values_declared`.
- **Every vocabulary value needs at least one paper.** A value nobody uses is an
  untested claim about the field. Either find the paper or delete the value.
  *Enforced:* `test_no_empty_vocabulary_values`.
- **Every modality used must be declared** in `schema.modalities`.
  *Enforced:* `test_modalities_declared`.
- **Keep cells short.** `tldr`, `why`, `method.intuition`, `experiments.headline` are
  at most two sentences.
  *Enforced:* `test_cells_are_short` (a length ceiling, which is a proxy).
- **Never fabricate a number.** Every figure in a `headline` must come from the paper's
  own abstract, or be arithmetic on figures that do.
  *Not mechanizable.* The check that exists is a human one: pull the abstract from the
  arXiv API and diff the numbers. See `../dev-journal/past/changelog.md` for the pass
  that caught two.
- **Leave `institutions` empty rather than guessing.** An empty cell is honest.
  *Not mechanizable.*
- **`confidence: "medium"` means not read end to end.** It renders on the page. Use it.
  *Enforced:* `test_confidence_declared`.

## Prose voice

The repo follows the user's `Plain` output style. Everything user-visible obeys it:
`tldr`, `why`, `method.intuition`, `experiments.headline`, every `help` and `sub` and
`blurb` in the schema, this handbook, the README, and commit messages.

- **Split, do not glue.** A semicolon or em-dash welding two independent clauses
  becomes two sentences. This is the loudest tell.
  *Enforced:* `test_no_clause_welding`.
- **No antithesis reflex.** Target zero "not just X but Y", "it's not X, it's Y",
  "no X, no Y, just Z". Delete the negated half and state the claim.
  *Enforced:* `test_no_antithesis`.
- **No blacklist vocabulary** — delve, leverage, utilize, robust, comprehensive,
  seamless, crucial, landscape, realm, underscore, facilitate, nuanced, holistic,
  pivotal, novel, foster, elucidate, "it's worth noting", "at its core".
  Nor the Opus-5 set — load-bearing, seam, substrate, provenance, wedge, the unlock,
  surface area, table stakes, scaffolding, "worth stating plainly", "here's the thing".
  *Enforced:* `test_no_blacklist_words`, with an allowance for paper titles, which are
  quotations and must stay verbatim.
- **Claim first.** A `tldr` states the paper's claim, not its topic. "Predicting masked
  video in latent space is enough to plan real pick-and-place zero-shot" beats "A
  self-supervised video model for understanding and planning".
  *Not mechanizable.*
- **Be specific.** The number, not "significantly better".
  *Not mechanizable.*

## Build and files

- **Never hand-edit `index.html` or `review.html`.** Both come from one template.
  Edit `data/` or `src/` and rebuild.
  *Enforced:* `test_build_is_current` — rebuilds and checks both pages are stable.
- **Review scaffolding never reaches the deliverable.** The comment layer is inlined
  into `review.html` only. `index.html` gets `__PHYSAI_REVIEW_ATTRS__`,
  `__PHYSAI_REVIEW_CSS__` and `__PHYSAI_REVIEW_JS__` stripped to nothing.
  *Enforced:* `test_review_scaffolding_is_stripped`.
- **Keep `index.html` self-contained.** No CDN, no external font, no `fetch`. It must
  open from `file://` with nothing beside it. `review.html` inlines its layer for the
  same reason rather than linking it.
  *Enforced:* `test_page_is_self_contained`.
- **`src/comment-layer.{css,js}` are vendored, not ours.** They come from the
  `commentable-html` skill; upgrade by re-copying. `src/comment-bridge.js` is ours —
  it reconciles the layer with this page's tabs. Edit the bridge, not the layer.
- **Data files are split by topic, not by size.** A new topical chunk gets the next
  `NN-` prefix. The prefix orders nothing at runtime — `build.py` sorts papers by date
  — it is only for humans reading the directory.
- **`python3` stdlib only.** No dependencies, in the build or the tests. Adding one
  means anyone cloning this needs an environment, which defeats "open the file".

## Git

- **Single `main` branch.** There is no manager branch and no PR flow here; it is a
  data repo with one maintainer. If it grows collaborators, revisit
  `~/.claude/skills/git-for-ai-teams/references/main-only-fallback.md`.
- **Commit the built `index.html`, ignore `review.html`.** `index.html` is a build
  artifact and also the deliverable, so someone should be able to clone and open it.
  `review.html` is regenerable working scaffolding and would duplicate 400 KB on every
  data change. `*.comments.json` is per-reviewer markup on a draft and stays local.
- **One commit per coherent change to the data or the framework.** A commit that adds
  papers and retunes the views at once is two commits.
