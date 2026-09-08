# Lecture 2: Physical AI, where the field stands, and how to join the conversation

`doc.ipynb` is the lecture note, written as a presentation. Open it in JupyterLab and it
reads as a designed page you can type into. The same file presents as a deck.

```sh
bash lab.sh            # opens doc.ipynb in JupyterLab on port 8899
```

In Lab: <kbd>Alt+T</kbd> table of contents, <kbd>Alt+Z</kbd> hides Lab's chrome,
<kbd>Alt+F</kbd> dims every cell but the one you are in, Present opens the deck.

## The format

One unit per slide: a figure, a gallery of paper figures and photos, or a table, then two
to four bullets that carry its point, then a box that repeats the lecture's map with the
units done in ink and the rest greyed out. In the deck a heading is a slide, and each
figure, gallery, bullet list and box is one press of →. The map is `MAP` in
`scripts/build_doc.py`, `box()` draws it, `gallery()` writes a row of captioned images
from `assets/img/`, and the colours are the last blocks of `custom.css`. Numbers live in
the tables; a bullet is one claim. Every stage of §2 keeps two rows, a person's and a
robot's, because the same stage is a different problem for each.

## What is in here

```
doc.ipynb            the lecture. Edit it here; this is the source of truth.
data/*.csv           counts of the paper hub, written by scripts/hub_stats.py, plus
                     dataset_hours.csv, a hand-kept table of released video hours with
                     the paper each number comes from (hours_by_domain.csv sums it)
assets/img/          the figures and photos the galleries show, resized; CREDITS.md
                     names the paper or the Wikimedia Commons license for each
scripts/hub_stats.py counts paper-hub/data/papers/*.json into data/
scripts/build_doc.py the seed. It wrote doc.ipynb once and refuses to overwrite it
                     unless told to, because every edit made in Lab lives only in
                     doc.ipynb. scripts/debate1_cells.py holds the Debate 1 cells.
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
it names, so re-read the numbers in §2 and §3 when the hub grows.

## Comments

A `> [C]` line in a cell is a note between the author and the assistant. Type one
under the cell it is about, delete it when answered. `build.py` strips them from
the deck.
