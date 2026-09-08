#!/usr/bin/env python3
"""One-shot: put the Debate 1 cells from debate1_cells.py into the existing doc.ipynb.

Inserts them before the §5 closer ("The debates change the hub, and §6 is how."), and
patches two existing cells so the lecture points at the brief. Refuses to run twice.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import nbformat as nbf

sys.path.insert(0, str(Path(__file__).resolve().parent))
from debate1_cells import debate1  # noqa: E402

HERE = Path(__file__).resolve().parent.parent
NB = HERE / "doc.ipynb"

CELLS: list[tuple[str, str]] = []


def md(src: str) -> None:
    CELLS.append(("markdown", src.strip("\n")))


def flow(body: str) -> None:
    md('<pre class="flow">\n' + body.strip("\n") + "\n</pre>")


def slide_type(src: str) -> str:
    if re.match(r"^\s*(#\s|<h1|##\s|<h2)", src):
        return "slide"
    if re.match(r"^\s*(###\s|<h3)", src):
        return "subslide"
    return "fragment"


PATCHES = {
    "The first debate is §2, physical AI against virtual AI. Is it needed at all, where is the\nboundary, and what is the technical difference. ":
    "The first debate is §2, physical AI against virtual AI. Is it needed at all, where is the\nboundary, and what is the technical difference. Its brief, the reading, a ten-minute recap\nand ten motions, closes this section. ",
    "the technical difference. Every claim above is there to be attacked.</p></div>":
    "the technical difference. Every claim above is there to be attacked. The brief is in §5.</p></div>",
}


def main() -> None:
    nb = nbf.read(str(NB), as_version=4)
    if any(str(c.get("id", "")).startswith("d1-") for c in nb.cells):
        sys.exit("doc.ipynb already holds the debate 1 cells")
    closer = [i for i, c in enumerate(nb.cells)
              if c.source.startswith("The debates change the hub")]
    if len(closer) != 1:
        sys.exit(f"expected one §5 closer cell, found {len(closer)}")
    patched = 0
    for c in nb.cells:
        for old, new in PATCHES.items():
            if old in c.source:
                c.source = c.source.replace(old, new)
                patched += 1
    if patched != len(PATCHES):
        sys.exit(f"expected {len(PATCHES)} text patches, applied {patched}")
    debate1(md, flow)
    new = []
    for i, (kind, src) in enumerate(CELLS):
        cell = nbf.v4.new_markdown_cell(src)
        cell.metadata["slideshow"] = {"slide_type": slide_type(src)}
        cell["id"] = f"d1-{i:03d}"
        new.append(cell)
    at = closer[0]
    nb.cells[at:at] = new
    nbf.validate(nb)
    nbf.write(nb, str(NB))
    print(f"inserted {len(new)} cells at {at}; notebook now {len(nb.cells)} cells; patched {patched}")


if __name__ == "__main__":
    main()
