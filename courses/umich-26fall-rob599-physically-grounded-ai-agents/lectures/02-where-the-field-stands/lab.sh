#!/usr/bin/env bash
# Open this Jupyter doc in JupyterLab, configured the way the format needs.
#
#     ./lab.sh            open doc.ipynb on port 8899
#     ./lab.sh 8890       ...on another port
#
# Three things this sets that a bare `jupyter lab` does not:
#
#   the venv          ~/fun/jupyter/.venv, pinned to JupyterLab 4.2.5. The
#                     machine's python3 is 3.14 with no jupyter, and the pyenv
#                     shim on PATH resolves to it and fails.
#   .labconfig        windowingMode "defer", so every cell is attached to the
#                     DOM. Lab's default keeps only the ~17 around the viewport,
#                     which gives a two-entry table of contents and breaks
#                     in-page search over the rest of the document.
#   expose_app        window.jupyterapp, so lab.js can hide Lab's chrome through
#                     Lab's own commands. Lumino positions the panels absolutely;
#                     CSS that collapses one leaves its gap behind.
#   the deck origin   a plain static server on PORT+1 over this same folder, so
#                     Present has a normal origin to open the deck from. Lab
#                     serves /files/ under `sandbox allow-scripts`, where
#                     window.open returns null and localStorage throws, which is
#                     what killed reveal's `s` speaker view. lab.js prefers this
#                     server and falls back to /files/ when it is not running.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="${NBDOC_VENV:-$HOME/fun/jupyter/.venv}"
PORT="${1:-8899}"
NB="${2:-doc.ipynb}"
# A hashed password in ~/.jupyter/jupyter_notebook_config.json applies to every
# server this machine starts, so a bare launch lands on a login form instead of
# the document, and the auth cookie is per-port so an earlier login does not
# carry over. An explicit token puts the credential in the URL, which is what
# makes the printed link work on the first click. Loopback-only either way.
TOKEN="${NBDOC_TOKEN:-nbdoc}"

if [ ! -x "$VENV/bin/jupyter" ]; then
  echo "no jupyter at $VENV/bin/jupyter" >&2
  echo "  ~/.pyenv/versions/3.11.0/bin/python -m venv $VENV" >&2
  echo "  $VENV/bin/pip install -r ~/fun/jupyter/requirements.txt" >&2
  exit 1
fi

# Untrusted output is dropped on open, and the whole look plus the table of
# contents lives in one cell's output. Anything that rewrites the .ipynb clears
# the signature, so re-sign on every launch rather than debugging a plain-looking
# notebook later.
"$VENV/bin/jupyter" trust "$HERE/$NB" >/dev/null 2>&1 || true

# Same folder, next port up. If something already holds that port, http.server
# exits and Present just falls back to /files/ — lab.js checks the deck exists
# over Lab's own route first, so a stranger on this port cannot misdirect it.
DECK_PORT=$((PORT + 1))
"$VENV/bin/python" -m http.server "$DECK_PORT" --bind 127.0.0.1 --directory "$HERE" \
  >/dev/null 2>&1 &
DECK_PID=$!
trap 'kill "$DECK_PID" 2>/dev/null || true' EXIT INT TERM

echo "  http://127.0.0.1:$PORT/lab/tree/$NB?token=$TOKEN"
echo "  deck origin: http://127.0.0.1:$DECK_PORT/   (Present, and reveal's s key)"

"$VENV/bin/jupyter" lab "$NB" \
  --port="$PORT" \
  --ServerApp.root_dir="$HERE" \
  --IdentityProvider.token="$TOKEN" \
  --PasswordIdentityProvider.hashed_password='' \
  --LabApp.user_settings_dir="$HERE/.labconfig" \
  --LabApp.expose_app_in_browser=True
