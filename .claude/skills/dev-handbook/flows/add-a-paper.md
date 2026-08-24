# Flow: add a paper

The canonical operation. Start here before touching `data/papers/`.

## 1. Ground it

Pull the real abstract before writing anything. Guessing produces confident errors in
a public artifact.

```
http://export.arxiv.org/api/query?id_list=2506.09985&max_results=1
```

Take the title, the author list, the published date, and the `arxiv:comment` field —
the comment usually names the accepted venue. See `../dev-setup.md` for the batch
recipe and the rate-limit note.

If the paper is not on arXiv, or is old enough that you know it cold, write from
knowledge and set `confidence: "medium"` unless you have actually read it.

## 2. Pick the file

Any file under `data/papers/`. The `NN-` prefix orders nothing at runtime —
`build.py` sorts every paper by `date` — so it is only there for humans scanning the
directory. Put it where a reader would look for it. A new topic gets the next prefix.

## 3. Fill the required fields

`id`, `title`, `year`, `venue`, `tldr`, `arc`. The build refuses anything missing one.

- `id` — kebab-case slug, unique, stable. It is the deep-link anchor, so do not rename.
- `tldr` — one or two sentences stating the paper's *claim*, not its topic. "Predicting
  masked video in latent space is enough to plan real pick-and-place zero-shot" beats
  "A self-supervised video model for understanding and planning".
- `venue` — what you can verify. `arXiv` is an honest answer.

## 4. Fill the axes

All 13 topic axes plus `contribution` and `openness`. Vocabularies are in
`data/schema.json`; each value carries a `help` string explaining what it means.

The three that get mis-tagged most often:

- **`world_facet`** — pick the facets the paper *contributes to*, not the ones that
  merely appear in it. Almost every paper contains objects; tag `object-state` only
  when the object representation is part of the contribution. Over-tagging here is
  what unbalances the framework groups.
- **`human_role`** — separate from `embodiment`. A person can be data without being an
  actuator. It is multi-select: a user study makes them an `evaluator` as well as
  whatever else they are. `demonstrator` means their behaviour is the training signal,
  which puts the paper on the robot side rather than the guided-human side.
- **`representation`** — the form the world is held in *by this paper's contribution*.
  A dataset of video is `pixels`; a benchmark whose answers are text is `language`.

## 5. Fill the reading protocol

`problem`, `method`, `experiments`. The shape and the reasoning behind it are in
`../design-rationale.md`. Two things people skip and should not:

- **`problem.training.note`** — what differs from inference. The interesting design
  choices hide in that difference.
- **`experiments.datasets[].role`** — what the authors did to their data
  (`existing` / `reannotated` / `remix` / `new` / `synthetic` / `real-robot`). Often the
  real contribution.

`experiments.headline` gets one number, and that number must appear in the abstract.

## 6. Write `why`

One sentence on why this earns a place on the list. Not a summary — `tldr` already did
that. This is the editorial line: what it settles, what it opens, what it sits opposite.

## 7. Build and test

```sh
python3 build.py
python3 .claude/skills/dev-test/tests/test_database.py
```

The build prints any value not declared in the schema. If it is a real new category,
add it to `data/schema.json` with a `label` and a `help` first. If it is a typo, fix it.

The test surface enforces the mechanical half of the conventions — schema conformance,
vocabulary coverage, prose voice, build freshness. It does not check whether the
numbers are true. That is on you.

## 8. Check the framework did not rebalance

Adding papers shifts which group claims what. Open the page and look at the group
counts. If one group has swallowed its arc, the fix is almost always a `pri` adjustment
in `data/schema.json` or a too-generous `world_facet` on the new paper — see
`../design-rationale.md` under "Group display order is separate from group assignment
order".
