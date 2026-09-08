# Lecture 2: Physical AI, where the field stands, and how to join the conversation

`doc.ipynb` is the lecture note, written as a presentation. Open it in JupyterLab and it
reads as a designed page you can type into. The same file presents as a deck.

```sh
bash lab.sh            # opens doc.ipynb in JupyterLab on port 8899
```

In Lab: <kbd>Alt+T</kbd> table of contents, <kbd>Alt+Z</kbd> hides Lab's chrome,
<kbd>Alt+F</kbd> dims every cell but the one you are in, Present opens the deck.

## The format

One unit per slide: a figure or a table, then two to four bullets that carry its point,
then a box that repeats the lecture's map with the units done in ink and the rest greyed
out. In the deck a heading is a slide, and the figure, the bullets and the box are three
presses of →. The map is `MAP` in `scripts/build_doc.py`, `box()` draws it, and the
colours are the last block of `custom.css`. Numbers live in the tables; a bullet is one
claim.

## What is in here

```
doc.ipynb            the lecture. Edit it here; this is the source of truth.
data/*.csv           counts of the paper hub, written by scripts/hub_stats.py
scripts/hub_stats.py counts paper-hub/data/papers/*.json into data/
scripts/build_doc.py the seed. It wrote doc.ipynb once and refuses to overwrite it
                     unless told to, because every edit made in Lab lives only in
                     doc.ipynb.
scripts/make.sh      counts, style cell, execute, trust, export. --seed rebuilds
                     doc.ipynb from the seed first and erases hand edits.
custom.css           this lecture's own styling, on top of doc.css
doc.html, deck.html  exports for people without Jupyter. Generated, not committed.
```

Everything else (`nbdoc.py`, `labstyle.py`, `doc.css`, `build.py`, `lab.*`,
`toc-layer.*`, `.labconfig/`, `assets/reveal/`) is copied from the `doc-jupyter`
skill unchanged.

## After the hub changes

```sh
bash scripts/make.sh   # recount, re-execute the charts, re-export
```

The charts redraw from the new counts. The prose carries the counts as of the date
it names, so re-read §3 when the hub grows.

## Comments

A `> [C]` line in a cell is a note between the author and the assistant. Type one
under the cell it is about, delete it when answered. `build.py` strips them from
the deck.
