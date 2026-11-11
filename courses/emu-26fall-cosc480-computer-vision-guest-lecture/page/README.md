# Guest lecture: the page

`index.html` is the talk, the first half of ROB 599 Lecture 2 cut to about 40 minutes for
EMU's COSC 480/592 Computer Vision on 2026-11-17. The `README.md` one folder up is the same
talk for GitHub, and `build.py` writes both.

```sh
python3 serve.py         # then open http://127.0.0.1:8777/
```

Press P to present. With no steps yet, P opens the step editor. Click the blocks in the
order you will talk about them, then press E to play. The steps save to
`emu-guest-lecture.present.json` beside the page. Comments (C, or the chip at the bottom
right) save to `emu-guest-lecture.comments.json`, which git ignores. Opened as a file with
no server, the page works the same but keeps steps and comments in that browser only.

## Editing it

Edit `build.py`, then run `python3 build.py`. It rewrites `index.html` and `../README.md`,
so never edit those two by hand. Every block carries an id that comments and steps attach
to, so keep a block's id when you change its words. The map boxes come from `MAP` in
`build.py`, so adding or dropping a unit there redraws all of them.

## How it was made

The talk was a doc-jupyter notebook from 2026-11-10 to 2026-11-11, written by a script that
cut Lecture 2's notebook (`notebook/scripts/cut.py`, in git history at `b535c2b`). It keeps
§1 to §3 of Lecture 2 word for word, drops six units, and adds one closing unit of keywords
and links. On 2026-11-11 the notebook became this page, and every block was checked word for
word against its notebook cell before the notebook was deleted.

## The counts are from September

Every number quotes the hub on 2026-09-07, when it held 110 papers. The four charts in
`assets/charts/` were drawn from those counts and are files, so a rebuild never redraws
them. Figure credits are in `assets/img/CREDITS.md`.
