# Flow: the build pipeline

```
data/schema.json ──┐                              ┌─→ index.html    placeholders stripped
data/papers/*.json ┼─→ build.py ─→ template.html ─┤
src/comment-*.{css,js} ┘           (4 placeholders) └─→ review.html   layer inlined
```

Two pages come out of one template. `index.html` is the deliverable — self-contained,
no server, no scaffolding. `review.html` is the same page with the comment layer
inlined so the draft can be marked up before it ships. The split exists so review
machinery never reaches a reader.

## What `build.py` does

1. Reads `data/schema.json`.
2. Reads every `data/papers/*.json` in sorted filename order, checks each is an array,
   checks required fields (`id`, `title`, `year`, `venue`, `tldr`, `arc`), and refuses
   duplicate ids across files. Stamps each paper with `_src` so a later reader knows
   which file it came from.
3. Sorts every paper by `date` descending. Filename prefixes order nothing.
4. Audits values against the schema vocabularies and prints anything undeclared. This
   is a notice, not an error — the vocabulary is meant to grow.
5. Serializes `{schema, papers}` to compact JSON, escapes `</`, ` `, ` ` so it
   survives inside a `<script type="application/json">` tag, and substitutes it for the
   `__PHYSAI_DATA__` placeholder in `src/template.html`.
6. Writes `index.html`.

`--check` runs steps 1–4 and stops.

## What the page does at load

`src/template.html` is the whole client: CSS, markup shell, and one IIFE. It parses the
inlined JSON once and never fetches anything.

The pieces worth knowing before editing it:

- **`state`** — view, query, `filters` (one `Set` per faceted field), sort, visible
  columns, `dedupe`. Every render reads from this.
- **`passesExcept(paper, skipKey)`** — the filter predicate. Skipping one key is what
  lets the facet rail show live counts that exclude the facet being counted, so
  ticking a box never shows a zero.
- **`renderFramework`** — the important one. It builds `claim`, a map from group id to
  papers, by walking groups in `pri` order and letting each claim what is unclaimed.
  Then it renders in *array* order. Display order and assignment order are separate on
  purpose; see `../design-rationale.md`.
- **`renderTable`** — `COLDEF` defines every column; a column without a `get` falls
  back to rendering its schema vocabulary as chips. Adding a field to the schema makes
  it filterable automatically, but it needs a `COLDEF` entry to be a table column.
- **`renderPanel`** — the detail card. `ioBlock` renders the problem-setting I/O.
- **`renderProtocol`** — the third tab, generated from `schema.reading_protocol` and
  the field dictionary. It is rendered once and cached via a `data-done` attribute.

## Editing the template

- The placeholder `__PHYSAI_DATA__` must survive. `build.py` exits if it is gone.
- Keep it self-contained: no CDN, no external font, no `fetch`. `test_page_is_self_contained`
  fails the build otherwise, and the page has to work from `file://`.
- `localStorage` access is wrapped in `try/catch` because it throws in some `file://`
  contexts.
- Theme: light tokens on bare `:root`, dark overrides in both a
  `prefers-color-scheme` block and a `[data-theme="dark"]` block, so the manual toggle
  wins in both directions.
- After any template edit, rebuild. `index.html` is not watched.
