#!/usr/bin/env python3
"""cut — write this talk's doc.ipynb from ROB 599 Lecture 2's notebook.

    ~/fun/jupyter/.venv/bin/python scripts/cut.py            # only if doc.ipynb is absent
    ~/fun/jupyter/.venv/bin/python scripts/cut.py --force    # overwrite it
    bash scripts/make.sh                                     # then style, run, export

The talk is the first half of Lecture 2 (§1 the loop, §2 the seven stages, §3 toward
production), cut to about 40 minutes for a computer vision class that meets physical AI
for the first time. It stays broad: every stage keeps its slides, and the units in DROP
go, either for time or because they lean on background the class has not had. Lecture
2's text is kept word for word. What changes is the title, the opening, every map box
(redrawn for the shorter map), and one new closing unit of keywords and links.

The kept cells quote the hub as it stood on 2026-09-07 (110 papers), so this script
copies Lecture 2's counts in data/ and never recounts them. It also copies the figures
the kept cells show, with their CREDITS.md rows, and the tooling Lecture 2's notebook
runs on.

It wrote doc.ipynb once. After that the notebook is the source of truth, so the script
refuses to overwrite an existing doc.ipynb unless told to.
"""
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

import nbformat as nbf

HERE = Path(__file__).resolve().parent.parent           # notebook/
COURSES = HERE.parent.parent                             # courses/
L2 = (COURSES / "umich-26fall-rob599-physically-grounded-ai-agents" / "lectures"
      / "02-where-the-field-stands" / "notebook")

REPO = "https://github.com/yayuanli-org/awesome-physical-ai"
HUB = "https://yayuanli-org.github.io/awesome-physical-ai/"

# Lecture 2's cells, kept through the map box after "build on today", §3's last unit.
LAST = "c092"
# Units dropped from §1 to §3, each with its bullets and its map box.
DROP = {
    "c025", "c026",                  # 2.1 the sensing-channel chart
    "c027", "c028",                  # 2.1 RGB no more: a ViT reading JPEG's DCT blocks
    "c040", "c041",                  # 2.3 what anticipate papers predict: pixels, latents, words
    "c046", "c047",                  # 2.4 anticipate and decide, one network or two
    "c059", "c060", "c061",          # 2.5 the robot galleries: Diffusion Policy, Code as Policies, DreamZero
    "c080", "c081", "c082", "c083",  # §3 what gets built: contribution by domain
}

# Copied from Lecture 2's notebook unchanged. The doc-jupyter tooling and its settings.
TOOLING = ["build.py", "nbdoc.py", "labstyle.py", "lab.sh", "lab.css", "lab.js", "doc.css",
           "custom.css", "toc-layer.css", "toc-layer.js", ".gitignore", "scripts/readme.py"]
TOOLING_DIRS = [".labconfig", "assets/reveal"]

# ------------------------------------------------------------------ the map
# Lecture 2's map with §4 to §7 gone and one closing section. Same drawing code as
# Lecture 2's scripts/build_doc.py, so the boxes look the same.
MAP = [
    ("understand the field", [
        ("§1", "what it is",         ["the loop", "embodiment"]),
        ("§2", "the anatomy",        ["seven stages", "sense", "represent", "anticipate",
                                      "decide", "act", "verify", "adapt"]),
        ("§3", "toward production",  ["the missing part", "build on today"]),
    ]),
    ("go further", [
        ("§4", "where to look next", ["keywords and links"]),
    ]),
]
UNITS = [u for _, secs in MAP for _, _, us in secs for u in us]
LABEL_W = 23          # `§4 where to look next` is 21, plus two spaces before its units
INDENT = "  "
LINE_W = 96


def render_map(done_through: str | None) -> str:
    """The map as a pre.flow. `None` draws the overview, everything in ink."""
    n_done = len(UNITS) if done_through is None else UNITS.index(done_through) + 1
    state = {u: ("done" if i < n_done else "todo") for i, u in enumerate(UNITS)}
    sep = '<span class="sep"> · </span>'
    lines = []
    if done_through is not None:
        lines.append('<span class="lbl">where we are</span>')
    for group, secs in MAP:
        lines.append(f'<span class="grp">{group}</span>')
        for tag, name, units in secs:
            label = f"{tag} {name}"
            cls = "done" if any(state[u] == "done" for u in units) else "todo"
            head = f'{INDENT}<b class="{cls}">{label}</b>' + " " * (LABEL_W - len(label))
            width = len(INDENT) + LABEL_W
            row, used, first = [], 0, True
            for u in units:
                piece = (0 if first else 3) + len(u)
                if not first and width + used + piece > LINE_W:
                    lines.append(head + sep.join(row))
                    head, row, used, first = " " * width, [], 0, True
                    piece = len(u)
                row.append(f'<span class="{state[u]}">{u}</span>')
                used += piece
                first = False
            lines.append(head + sep.join(row))
    return '<pre class="flow map">\n' + "\n".join(lines) + "\n</pre>"


def is_box(src: str) -> bool:
    return src.startswith('<pre class="flow map">') and "where we are" in src


def done_through(src: str) -> str:
    """The last unit a Lecture 2 box draws in ink: the unit that box closes."""
    done = re.findall(r'<span class="done">([^<]*)</span>', src)
    assert done and done[-1] in UNITS, f"a box closes a unit this map does not hold: {done[-1:]}"
    return done[-1]


# ------------------------------------------------------------------ new cells
TITLE = ('<h1><span class="kicker">Guest lecture · EMU COSC 480/592 Computer Vision · '
         'November 17, 2026 · Yayuan Li, University of Michigan</span>'
         'Where Physical AI Stands: From First-Person Video to Agents That Act</h1>')

OPENING = "\n".join("- " + b for b in [
    "One pass over the field: what physical AI is, the seven stages people work on, and how "
    "far each is from production.",
    "Broad rather than deep. Every stage names its papers, and the last slide lists keywords "
    "to search later.",
    f"Everything here is in [the hub]({HUB}), an open database of physical AI papers. These "
    f"slides are on [GitHub]({REPO}).",
    "Leave knowing which stage interests you and what to search for next.",
])

KEYWORDS = [  # stage, words to search for, the two papers Lecture 2's §2 table names
    ("2.1 sense", "egocentric video, smart glasses, tactile sensing", "SAM 2, HOT3D"),
    ("2.2 represent", "representation learning, self-supervised learning, JEPA",
     "DINOv2, 3D Gaussian Splatting"),
    ("2.3 anticipate", "world models, procedural reasoning, counterfactual reasoning",
     "V-JEPA 2, Genie"),
    ("2.4 decide", "task planning with language models, video language planning, "
                   "proactive AR assistants", "SayCan, VLaMP"),
    ("2.5 act", "vision-language-action models, diffusion policy, world action models",
     "π₀, ShowHowTo"),
    ("2.6 verify", "mistake detection, failure detection", "PREGO, SAFE"),
    ("2.7 adapt", "continual learning, self-evolving AI", "Every Mistake Counts, Inner Monologue"),
]

CLOSING = [
    ("slide", "## Where to look next"),
    ("fragment", '<table class="k">\n<thead><tr><th>stage</th><th>search for</th>'
                 "<th>start with</th></tr></thead>\n<tbody>\n"
     + "\n".join(f"<tr><td>{s}</td><td>{k}</td><td>{p}</td></tr>" for s, k, p in KEYWORDS)
     + "\n</tbody></table>"),
    ("fragment", "\n".join("- " + b for b in [
        "Each row is one stage: the words to search for, and two papers to start with.",
        f"Resource hub and these slides: [github.com/yayuanli-org/awesome-physical-ai]({REPO}).",
        f"New to the field? The hub's [must-read list for students]({HUB}#must-read/student) is "
        "four papers, each one part of a vision-language-action model.",
    ])),
]


# ------------------------------------------------------------------ build
def copy(rel: str) -> None:
    src, dst = L2 / rel, HERE / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir():
        shutil.copytree(src, dst, dirs_exist_ok=True)
    else:
        shutil.copy2(src, dst)


def main(force: bool) -> None:
    out = HERE / "doc.ipynb"
    if out.exists() and not force:
        sys.exit(f"{out.name} exists and holds hand edits. Re-run with --force to overwrite it.")

    nb = nbf.read(str(L2 / "doc.ipynb"), as_version=4)
    ids = [c.get("id") for c in nb.cells]
    assert LAST in ids and DROP <= set(ids), "Lecture 2's cell ids moved; re-check LAST and DROP"

    cells = []
    for c in nb.cells:
        if c.get("id") not in DROP:
            src = c.source
            if c.get("id") == "c000":
                c.source = TITLE
            elif c.get("id") == "c002":
                c.source = render_map(None)
            elif c.get("id") == "c003":
                c.source = OPENING
            elif c.cell_type == "markdown" and is_box(src):
                c.source = render_map(done_through(src))
            if c.cell_type == "code":
                c.outputs, c.execution_count = [], None
            cells.append(c)
        if c.get("id") == LAST:
            break
    for i, (kind, src) in enumerate(CLOSING):
        cell = nbf.v4.new_markdown_cell(src)
        cell.metadata["slideshow"] = {"slide_type": kind}
        cell["id"] = f"g{i:03d}"
        cells.append(cell)

    nb.cells = cells
    nb.metadata.setdefault("nbdoc", {}).update({
        "doc_id": "emu-cosc480-guest-lecture-2026-11-17",
        "title": "Where Physical AI Stands · EMU COSC 480/592 guest lecture",
    })

    for rel in TOOLING + TOOLING_DIRS:
        copy(rel)

    text = "\n".join(c.source for c in cells)
    imgs = sorted(set(re.findall(r'assets/img/([^"\')\s]+)', text)))
    csvs = sorted(set(re.findall(r'data/([\w-]+\.csv)', text)))
    for f in imgs:
        copy(f"assets/img/{f}")
    for f in csvs:
        copy(f"data/{f}")

    stems = {Path(f).stem for f in imgs}
    keep = []
    for line in (L2 / "assets/img/CREDITS.md").read_text(encoding="utf-8").splitlines():
        m = re.match(r"\| ([^|]+) \|", line)
        if m and not line.startswith(("| file", "|---")):
            if not {s.strip() for s in m.group(1).split(",")} & stems:
                continue
        keep.append(line)
    (HERE / "assets/img/CREDITS.md").write_text("\n".join(keep) + "\n", encoding="utf-8")

    nbf.write(nb, str(out))
    print(f"{out.name}: {len(cells)} cells, {len(imgs)} figures, {len(csvs)} count files")


if __name__ == "__main__":
    main(force="--force" in sys.argv[1:])
