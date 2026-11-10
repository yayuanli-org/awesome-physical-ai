# Guest lecture: Where Physical AI Stands

`doc.ipynb` is the talk: the first half of ROB 599 Lecture 2, cut to about 40 minutes for
EMU's COSC 480/592 Computer Vision on 2026-11-17. The `README.md` one folder up is this
notebook exported for GitHub.

```sh
bash lab.sh            # opens doc.ipynb in JupyterLab on port 8899
bash lab.sh 8897       # the same, when Lecture 2's Lab already holds 8899
```

In Lab, Present opens the deck. `deck.html` is the same deck for a browser without
Jupyter, written by `bash scripts/make.sh`.

## How it was made

`scripts/cut.py` wrote `doc.ipynb` once from Lecture 2's notebook, in
`../../umich-26fall-rob599-physically-grounded-ai-agents/lectures/02-where-the-field-stands/notebook/`.
It keeps §1 to §3 word for word, drops six units (listed in `DROP`, each with its
reason), redraws every map box for the shorter map, and adds one closing unit of
keywords and links. It copied the figures, the counts and the tooling as well. Edit
`doc.ipynb` from now on, because `cut.py --force` would erase those edits.

## The counts are from September

Every number quotes the hub on 2026-09-07, when it held 110 papers. `scripts/make.sh`
styles, runs and exports the notebook, and unlike Lecture 2's it never recounts the hub.
A recount would redraw the charts from today's hub under bullets that still say 110.
