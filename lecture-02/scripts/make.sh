#!/usr/bin/env bash
# Rebuild everything around doc.ipynb, without rewriting doc.ipynb itself.
#
#   bash scripts/make.sh            counts, style cell, execute, trust, export
#   bash scripts/make.sh --seed     the same, after regenerating doc.ipynb from
#                                   scripts/build_doc.py. THIS ERASES HAND EDITS.
#
#   1. hub_stats.py    counts the paper hub into data/*.csv
#   2. build_doc.py    only with --seed, or when doc.ipynb does not exist yet
#   3. labstyle.py     installs and runs the hidden style cell
#   4. execute         so the charts are already there when it opens cold
#   5. jupyter trust   or Lab strips the style and the scripts on open
#   6. build.py        doc.html and deck.html, for readers without Jupyter
set -euo pipefail
cd "$(dirname "$0")/.."
V=~/fun/jupyter/.venv/bin

python3 scripts/hub_stats.py

if [ "${1:-}" = "--seed" ] || [ ! -f doc.ipynb ]; then
  "$V/python" scripts/build_doc.py --force
fi

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
