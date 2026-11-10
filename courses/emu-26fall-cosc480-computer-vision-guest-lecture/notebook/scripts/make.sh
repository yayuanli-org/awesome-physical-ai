#!/usr/bin/env bash
# Rebuild everything around doc.ipynb, without rewriting doc.ipynb itself.
#
#   bash scripts/make.sh
#
# Lecture 2's make.sh recounts the hub first. This one never does, because the talk
# quotes the hub as it stood on 2026-09-07 (110 papers). A recount would redraw the
# charts from newer numbers under bullets that still say 110.
#
#   1. labstyle.py     installs and runs the hidden style cell
#   2. execute         so the charts are already there when it opens cold
#   3. jupyter trust   or Lab strips the style and the scripts on open
#   4. build.py        doc.html and deck.html, for readers without Jupyter
#   5. readme.py       ../README.md, what GitHub shows for this folder
set -euo pipefail
cd "$(dirname "$0")/.."
V=~/fun/jupyter/.venv/bin

"$V/python" labstyle.py doc.ipynb

"$V/python" - <<'PY'
import nbformat as nbf
from nbconvert.preprocessors import ExecutePreprocessor
from pathlib import Path
p = Path("doc.ipynb")
nb = nbf.read(str(p), as_version=4)
ExecutePreprocessor(timeout=120).preprocess(nb, {"metadata": {"path": str(p.parent.resolve())}})
nbf.write(nb, str(p))
errs = [o for c in nb.cells for o in c.get("outputs", []) if o.get("output_type") == "error"]
print("executed:", len(nb.cells), "cells, errors:", errs or "none")
PY

"$V/jupyter" trust doc.ipynb
"$V/python" build.py --no-exec
"$V/python" scripts/readme.py
