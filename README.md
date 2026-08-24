# Awesome Physical AI

A paper database for physical AI, rendered as one self-contained HTML page.
Draft for **ROB 599 — Physically-Grounded AI Agents**, University of Michigan, Fall 2026.
Built to outlive the course: a reference anyone in the field can use, not a syllabus.

**https://yayuanli-org.github.io/awesome-physical-ai/**

The site is one self-contained page. To work on it offline, clone and build:

```sh
python3 build.py && open index.html
```

Python 3 and nothing else. No server, no network, no dependencies. Every tagged
release also carries a prebuilt copy of the page for reading without a clone.

## What this is

Under the page is a database. Every paper is a row, every dimension is a column,
and every section on the site is a filter over those columns. There is no folder
anywhere in the data, so a paper that both models the world and changes it carries
both values and shows up in both arcs.

The thesis the taxonomy encodes:

> Physical AI studies how the physical world gets changed in the age of AI.
> Changing the world takes two moves — model it, then change it through an
> embodiment — and acting changes what has to be modeled, so the two close into a loop.

Three views ship on the page:

| View | What it is |
|---|---|
| **Framework** | The two arcs and their groups, as a reading list. Groups are filters. |
| **Papers** | The raw table. Every column, sortable, with a column chooser and JSON export. |
| **How a paper is read** | The reading protocol and the full column dictionary. |

## Layout

```
index.html            the built page — generated, and not committed
review.html           the same page plus a comment layer, for marking the draft up
build.py              inlines data into the template
serve.py              localhost server that persists review comments to disk
src/template.html     page shell: CSS, JS, __PHYSAI_DATA__ placeholder
src/comment-*.{css,js}  the comment layer, inlined into review.html only
data/
  schema.json         the taxonomy: columns, vocabularies, views, reading protocol
  papers/*.json       the database, split into topical chunks
.github/workflows/    validate every pull request, publish every push to main
```

Both HTML files are generated. Edit `data/` or `src/`, never either page.

## Rebuilding

```sh
python3 build.py            # writes index.html and review.html
python3 build.py --check    # validate only, write nothing
python3 build.py --site DIR # assemble what CI publishes, in DIR
```

The build reports any value that is not in the schema vocabulary. That is a
notice rather than an error — the vocabulary is meant to grow. Add the value to
`data/schema.json` when it turns out to be a real category rather than a typo.

## Publishing

`main` is the site. Every push to it runs the tests and redeploys. Every pull
request runs the same tests and fails on a bad entry, so a malformed paper never
reaches the public page. Nothing is deployed by hand.

Neither page is committed. `index.html` is 360 KB of generated markup, and
committing it would bury each paper addition under a whole-file diff and leave a
stale page behind anyone who forgot to rebuild. CI builds it on every push.

The public site is exactly what `build.py --site` writes, which is the page plus
the database as raw JSON:

```
index.html            the page
data/schema.json      the taxonomy, machine-readable
data/papers/*.json    the database, machine-readable
```

`build.py`, `serve.py` and `.claude/` stay in the repo and off the site.

Tag a version to cut a release with a standalone copy of the page attached:

```sh
git tag v2026.08 && git push origin v2026.08
```

## Reviewing a draft

`review.html` is `index.html` with a comment layer over it. Press **C** or hit the
Comment button, click any element or select any text, and the comment threads in a
side panel that says which tab it belongs to. Comments never touch `index.html`, so
readers of the deliverable never see the review machinery.

```sh
python3 serve.py           # http://127.0.0.1:8777/review.html
```

Serve it rather than opening the file directly. Over `file://` the comments live in
one browser's storage; served, they persist to `physai.comments.json` next to the
page, which is what lets someone else read and answer them.


## Adding a paper

Drop an object into any file under `data/papers/` and rebuild. The required
fields are `id`, `title`, `year`, `venue`, `tldr`, `arc`. Everything else is
optional and simply renders as empty.

Open a pull request and CI checks the entry against the schema, the prose rules
and the view filters before anyone reviews it by eye.

The shape, in full:

```jsonc
{
  "id": "kebab-case-slug",
  "short": "Display name",
  "title": "Full title",
  "year": 2025, "date": "2025-06",
  "venue": "CVPR 2025", "venue_type": "conference",
  "authors": ["First Author", "..."], "n_authors": 8,
  "institutions": ["..."],
  "links": { "arxiv": "", "code": "", "page": "", "data": "" },
  "tldr": "One sentence. The claim, not the topic.",

  // physical-AI axes — see data/schema.json for the vocabularies
  "arc": ["model", "change"],
  "closes_loop": true,
  "loop_stage": ["sense", "represent", "anticipate", "decide", "act", "verify", "adapt"],
  "embodiment": ["human"], "human_role": "assisted",
  "world_facet": ["object-state"], "representation": ["latent"],
  "change_channel": ["visual-guidance"], "sensing": ["egocentric"],
  "regime": "streaming", "horizon": "minutes",
  "domain": ["everyday"], "autonomy": "mixed-initiative",
  "contribution": ["method"], "openness": ["code"],

  // the reading protocol
  "problem": {
    "task": "The function the paper computes.",
    "inference": {
      "inputs":  [{ "name": "", "modality": "video", "tensor": "V ∈ R^{T×H×W×3}", "chars": "" }],
      "outputs": [{ "name": "", "modality": "label", "tensor": "y", "chars": "" }]
    },
    "training": { "supervision": "", "note": "what differs from inference" }
  },
  "method": { "intuition": "1–2 sentences", "family": [], "backbone": "", "init": "", "components": [] },
  "experiments": {
    "datasets": [{ "name": "", "role": "existing|reannotated|remix|new|synthetic|real-robot" }],
    "metrics": [], "baselines": [], "headline": "one number that matters"
  },

  "why": "Why it earns a place on this list.",
  "confidence": "high",
  "tags": []
}
```

Two rules keep the database useful:

**Comprehensive structure, short cells.** Every column exists for every paper. No
cell runs past a sentence or two. The detail lives in the paper; this is the index
that tells you which paper to open.

**Categories where the world is small, prose where it is rich.** Modality is a
closed vocabulary because there are only so many modalities. What the content
actually is, and why a method works, are free text, because compressing those into
a label destroys the information you came for.

## Current state

110 papers, 2018–2026. Coverage is deliberately uneven: it is dense where the
framework needed stress-testing (egocentric procedural understanding, mistake
detection, world models, VLAs) and thin elsewhere. Filling it out is the next pass.

Entries marked `"confidence": "medium"` are grounded in the abstract and the
authors' own claims but were not read end to end. Venues record the best
verifiable source, so a paper listed as arXiv may have been published since.
