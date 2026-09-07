#!/usr/bin/env python3
"""labstyle — make the notebook itself look like the document.

    python3 labstyle.py doc.ipynb            # insert/refresh the style cell, then execute it

Puts a hidden code cell at the top of the notebook that calls `nbdoc.style()`.
That reads `doc.css` and `custom.css` from the folder, rewrites every selector to
sit inside JupyterLab's markdown container, and emits the result as the cell's
output. It then calls `nbdoc.chrome()`, which sends `lab.css`, `lab.js` and
`toc-layer.*` down the same channel: the floating table of contents, and the
zen / focus / reveal / present modes.

Why the output and not a markdown cell: **JupyterLab strips `<style>` out of
markdown cells**, trusted or not, because markdown is sanitised unconditionally.
A trusted cell's *output* is not sanitised, so the output is the only place a
notebook can carry its own look. Verified on Lab 4.2.5.

The same asymmetry carries the scripts. Lab runs `<script>` tags found in a
trusted cell's output (rendermime's `evalInnerHTMLScriptTags`), and replaces the
whole output with a "Run" button when the notebook is untrusted — so the trust
step at the end of this script is what makes any of it appear.

The cell is tagged so it stays out of the way:

    slide_type: skip     RISE never shows it
    source_hidden        you see the styled document, not the plumbing
    keep_output          nbstripout keeps this one output, so the style is
                         already applied when someone opens the notebook cold

Re-running this replaces the cell rather than stacking another one. Editing
`custom.css` and re-running just that cell restyles the whole document without
touching the notebook.
"""
from __future__ import annotations

import argparse, subprocess, sys
from pathlib import Path

import nbformat as nbf

TAG = "nbdoc-style"
SOURCE = "import nbdoc; nbdoc.style()"

# RISE presents the live notebook. Its defaults are a 960x700 slide with no
# scrolling, which clips a paper's paragraphs and tables on the right. A
# percentage width follows the window, and scroll keeps a dense slide readable
# instead of cutting it off.
RISE = {
    "autolaunch": False,
    "scroll": True,
    "width": "95%",
    "height": "95%",
    "theme": "simple",
    "transition": "none",
    "controls": True,
    "progress": True,
    "slideNumber": False,
}


def install(path: Path) -> int:
    nb = nbf.read(str(path), as_version=4)
    nb.metadata["rise"] = RISE
    cell = nbf.v4.new_code_cell(SOURCE)
    cell.metadata.update({
        "slideshow": {"slide_type": "skip"},
        "tags": [TAG],
        "jupyter": {"source_hidden": True},
        "keep_output": True,          # nbstripout honours this per cell
        "editable": False,
    })
    cell["id"] = "nbdocstyle"
    nb.cells = [c for c in nb.cells if TAG not in (c.metadata.get("tags") or [])]
    nb.cells.insert(0, cell)
    nbf.write(nb, str(path))
    return len(nb.cells)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("notebook", type=Path)
    ap.add_argument("--no-run", action="store_true",
                    help="insert the cell but do not execute it (the style will be blank until you do)")
    a = ap.parse_args()

    n = install(a.notebook)
    print(f"style cell installed; notebook now has {n} cells")
    print("rise metadata set: " + ", ".join(f"{k}={v}" for k, v in RISE.items() if k in ("width", "height", "scroll", "theme")))

    if a.no_run:
        print("not executed — run the first cell in Lab, or drop --no-run")
        return

    # Execute in place so the style is already applied when the notebook is opened
    # cold. Only the style cell needs to run; the rest is re-executed by build.py.
    from nbconvert.preprocessors import ExecutePreprocessor
    nb = nbf.read(str(a.notebook), as_version=4)
    one = nbf.v4.new_notebook(cells=[nb.cells[0]], metadata=nb.metadata)
    ExecutePreprocessor(timeout=60).preprocess(one, {"metadata": {"path": str(a.notebook.parent)}})
    nb.cells[0] = one.cells[0]
    nbf.write(nb, str(a.notebook))
    out = nb.cells[0].get("outputs", [])
    size = sum(len(str(o.get("data", {}).get("text/html", ""))) for o in out)
    print(f"executed: {size/1024:.1f} KB of scoped CSS stored as the cell's output")
    print("Now: jupyter trust", a.notebook.name, " (untrusted output is stripped on open)")


if __name__ == "__main__":
    main()
