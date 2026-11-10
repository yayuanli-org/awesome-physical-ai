"""nbdoc — the small helper a Jupyter doc's cells import.

Cells stay one line long and the house style lives here, so restyling every
figure in a deliverable is one edit rather than forty. Nothing in here computes
anything: it loads what `scripts/` already wrote and draws it.

    import nbdoc
    nbdoc.bar("data/plan_length_step.csv", title="Remaining plan length", note="n=1062")
    nbdoc.line("data/loss.csv", x="epoch", y=["train", "val"])
    nbdoc.fig("figs/method_train_01.png", caption="Figure 4. Training.")
    nbdoc.table("data/results_main.csv", caption="Table 2. Main results.")
"""
from __future__ import annotations

import csv as _csv
import re
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from IPython.display import HTML, display

# House palette, lifted from the document stylesheet so figures and prose agree.
INK, MUTED, FAINT, LINE = "#1f2330", "#5a6072", "#8b91a3", "#e6e8ef"
ACCENT, BLUE, VIOLET = "#d6689a", "#5b6ee1", "#7a6cc4"
SERIES = [BLUE, ACCENT, VIOLET, "#2f8f6b", "#c26a2b"]

mpl.rcParams.update({
    "figure.dpi": 130,
    # Keep SVG text as <text>, not outlined glyph paths. Paths inflate a
    # 60-bar chart past half a megabyte and stop the browser from styling it.
    "svg.fonttype": "none",
    "savefig.dpi": 130,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": FAINT,
    "axes.labelcolor": MUTED,
    "axes.titlesize": 11,
    "axes.titleweight": "bold",
    "axes.titlecolor": INK,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.color": LINE,
    "grid.linewidth": 0.8,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "xtick.labelsize": 8.5,
    "ytick.labelsize": 8.5,
    "axes.labelsize": 9.5,
    "legend.frameon": False,
    "legend.fontsize": 9,
    "font.size": 10,
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
})

DEFAULT_SIZE = (7.2, 2.4)

# Vector output: a bar chart as SVG is a tenth the bytes of the same chart as a
# 130-dpi PNG, and stays sharp when the deck is projected. Falls back silently
# outside IPython (a plain `python doc.py` run, say).
try:
    from IPython import get_ipython as _gi
    _ip = _gi()
    if _ip is not None:
        _ip.run_line_magic("config", "InlineBackend.figure_formats = ['svg']")
except Exception:
    pass


def _autosize(n, size, per_bar=0.22, floor=7.2):
    """Widen the frame when there are more bars than the default can hold."""
    if size is not DEFAULT_SIZE:
        return size
    w = max(floor, min(14.0, n * per_bar))
    return (w, size[1] + (0.9 if n > 24 else 0.0))


SCOPE = ".jp-RenderedHTMLCommon"        # what Lab renders both markdown and HTML output into
ROOT = ".jp-Notebook"                   # the whole document, once
ROOT_SELS = ("body", "#content", "body #content", "html")
# Selectors already written against the target and so left alone. Lab's own
# classes here; build.py passes reveal's when it scopes the same sheets for the
# deck, where `.jp-` is ordinary content and must be scoped like anything else.
SCOPED = (".jp-", ":root", "html")
# A page sheet's `body` / `#content` rule carries the measure AND the page padding.
# The container it maps to in a notebook is repeated once per cell, so its box
# properties have to be dropped or every paragraph gets 212px of padding. Only
# what is safe to inherit survives.
ROOT_PROPS = ("font", "font-family", "font-size", "font-weight", "line-height",
              "color", "background", "background-color", "letter-spacing",
              "-webkit-font-smoothing", "text-rendering")

# Notebook-only rules. The document sheet cannot know about these because they
# describe the editor, not the page.
PREAMBLE = """
/* --- the notebook as a page ------------------------------------------------ */
.jp-Notebook { --jp-cell-padding: 0px; }
.jp-Cell { padding: 0 !important; }
.jp-Cell.jp-mod-noOutputs .jp-Cell-outputWrapper { display: none; }
/* Kill the empty gutter that reserves room for In[ ]: prompts, and reclaim its
   width for the prose. Markdown cells have no prompt to show. */
.jp-Cell .jp-InputPrompt, .jp-Cell .jp-OutputPrompt { display: none !important; }
.jp-Notebook .jp-Cell { max-width: 980px; margin-left: auto; margin-right: auto; }
/* Cell chrome only on hover, so reading the notebook feels like reading a page. */
.jp-Notebook:not(.jp-mod-commandMode) .jp-Cell:not(.jp-mod-active) .jp-InputArea-editor,
.jp-Notebook .jp-Cell .jp-Collapser { background: transparent; border-color: transparent; }
.jp-RenderedHTMLCommon { padding-right: 0; }
.jp-RenderedHTMLCommon > :first-child { margin-top: 0; }
.jp-RenderedHTMLCommon > :last-child { margin-bottom: 0; }
"""

# Comment callouts. In the notebook these are live blockquotes, not the <aside>
# that build.py makes for the export, so they need their own rule.
COMMENTS = """
/* --- `> [C]` comment blockquotes ------------------------------------------- */
.jp-RenderedHTMLCommon blockquote {
  margin: 12px 0; padding: 9px 14px 9px 12px;
  border-left: 3px solid var(--cmt-line, #ddd5f2);
  background: var(--cmt-soft, #f4f1fc); border-radius: 0 6px 6px 0;
  font-size: 13.5px; line-height: 1.5; color: #3d3752;
}
.jp-RenderedHTMLCommon blockquote p { margin: 3px 0; }
.jp-RenderedHTMLCommon blockquote strong { color: var(--cmt, #7a6cc4); }
"""

BLOCK = re.compile(r"([^{}]+)\{([^{}]*)\}")
ATRULE = re.compile(r"(@[a-zA-Z-]+[^{]*)\{(.*)\}\s*$", re.S)
COMMENT = re.compile(r"/\*.*?\*/", re.S)


def scope_selector(sel: str, scope: str = SCOPE, root: str = ROOT,
                   scoped: tuple = SCOPED) -> str:
    # A comment sitting in front of a rule is captured with its selector, and CSS
    # allows it there, so `.jp-Foo` arrives as `/* … */ .jp-Foo` and the
    # already-scoped test below misses it. Scoping it again yields
    # `.jp-RenderedHTMLCommon .jp-RenderedHTMLCommon …`, which matches nothing and
    # fails silently. Drop comments before deciding anything.
    sel = COMMENT.sub(" ", sel).strip()
    if not sel or sel.startswith("@"):
        return sel
    if sel.startswith(scoped):
        return sel
    if sel in ROOT_SELS:
        return root
    if sel == "*":
        return f"{scope} *"
    # `body h2` / `#content p` are about the page, so drop the page part.
    sel = re.sub(r"^(body|#content)\s+", "", sel)
    return f"{scope} {sel}"


def _root_only(decls: str) -> str:
    """Keep only the declarations that are safe to apply once to the whole notebook."""
    keep = []
    for d in decls.split(";"):
        prop = d.split(":", 1)[0].strip().lower()
        if prop in ROOT_PROPS:
            keep.append(d.strip())
    return ("; ".join(keep) + ";") if keep else ""


def scope_css(css: str, scope: str = SCOPE, root: str = ROOT,
              scoped: tuple = SCOPED) -> str:
    """Prefix every rule with `scope`, recursing into at-rules.

    The defaults target a JupyterLab notebook. build.py passes reveal's selectors
    to put the same sheets into the deck, where the document's bare `h1` would
    otherwise lose to JupyterLab's own embedded `.jp-RenderedHTMLCommon h1` and to
    reveal's `.reveal h1` — both one class more specific.
    """
    out, i = [], 0
    while i < len(css):
        # Comments pass through. The scan position lands on the newline after the
        # previous `}`, so step over whitespace first or every comment but the
        # file's first one is swallowed into the next selector.
        w = i
        while w < len(css) and css[w] in " \t\r\n":
            w += 1
        if css.startswith("/*", w):
            j = css.find("*/", w)
            j = len(css) if j < 0 else j + 2
            out.append(css[i:j]); i = j; continue
        at = css.find("@", i)
        brace = css.find("{", i)
        if brace < 0:
            out.append(css[i:]); break
        if 0 <= at < brace:
            # an at-rule: keep the header, scope the body if it has one
            depth, j = 0, css.find("{", at)
            if j < 0:
                out.append(css[i:]); break
            k = j
            while k < len(css):
                if css[k] == "{": depth += 1
                elif css[k] == "}":
                    depth -= 1
                    if depth == 0: break
                k += 1
            head = css[at:j].strip()
            body = css[j + 1:k]
            out.append(css[i:at])
            if head.startswith(("@media", "@supports")):
                out.append(f"{head} {{\n{scope_css(body, scope, root, scoped)}\n}}\n")
            else:                                   # @font-face, @keyframes: verbatim
                out.append(f"{head} {{{body}}}\n")
            i = k + 1
            continue
        m = BLOCK.match(css, i)
        if not m:
            out.append(css[i:]); break
        raw = [s for s in m.group(1).split(",") if s.strip()]
        sels = ", ".join(scope_selector(s, scope, root, scoped) for s in raw)
        body = m.group(2)
        if all(s.strip() in ROOT_SELS for s in raw):
            body = _root_only(body)
            if not body.strip():
                i = m.end(); continue
        out.append(f"{sels} {{{body}}}\n")
        i = m.end()
    return "".join(out)


def _build_style(sheets) -> str:
    parts = []
    for p in sheets:
        parts.append(f"/* ================= {Path(p).name} ================= */")
        parts.append(scope_css(Path(p).read_text(encoding="utf-8")))
    parts.append(PREAMBLE)
    parts.append(COMMENTS)
    return "\n".join(parts)



def style(*sheets, chrome=True, quiet=True):
    """Apply the deliverable's stylesheets to this notebook, live.

    Call it from a hidden cell at the top. JupyterLab sanitises `<style>` out of
    markdown cells, but not out of a trusted cell's *output*, so this is the only
    place a notebook can carry its own look. Reading the .css files at run time
    rather than baking them into the .ipynb means editing doc.css or custom.css
    and re-running this one cell restyles the whole document.

    `chrome=True` also installs the reading environment — floating table of
    contents, zen, focus, reveal, present — from lab.css and lab.js when those
    are in the folder. Same channel and same one cell, so a deliverable does not
    have to remember a second call. `nbdoc.chrome()` runs it on its own.
    """
    here = Path.cwd()
    paths = [Path(p) for p in sheets] or [p for p in (here / "doc.css", here / "custom.css") if p.exists()]
    paths = [p for p in paths if p.exists()]
    if not paths:
        display(HTML("<p style='color:#b23b52'>nbdoc.style(): no stylesheet found</p>"))
        return
    # The cell hides itself. Lab virtualises the notebook, so :first-child is not
    # reliable — a marker in this cell's own output plus :has() is.
    hide = (".jp-Cell:has(> .jp-Cell-outputWrapper .nbdoc-style-host),"
            ".jp-Cell:has(.nbdoc-style-host) { display: none !important; }\n"
            ".nbdoc-style-host { display: none; }\n")
    display(HTML('<div class="nbdoc-style-host"></div><style>\n'
                 + hide + _build_style(paths) + "\n</style>"))
    if not quiet:
        print("styled from " + ", ".join(p.name for p in paths))
    if chrome:
        _chrome(quiet=quiet)   # the keyword above shadows the function's name


# The reading environment, in the order the files have to load.
CHROME_CSS = ("toc-layer.css", "lab.css")
CHROME_JS = "lab.js"
TOC_JS = "toc-layer.js"


def chrome(quiet=True):
    """Install the reading environment into JupyterLab: a floating table of
    contents, and zen / focus / reveal / present.

    Same channel as `style()` — a trusted cell's output — but this one carries
    `<script>` as well as `<style>`. JupyterLab runs script tags found in trusted
    HTML output (rendermime's evalInnerHTMLScriptTags); an untrusted notebook
    replaces the whole output with a "Run" button, so run `jupyter trust
    doc.ipynb` after anything rewrites the file.

    Unlike the document sheets, lab.css does NOT go through the selector
    rewriter. It names JupyterLab's own classes, so it is already scoped.

    toc-layer.js is parked in a `<script type="text/plain">` rather than run
    here: it builds its nav from the headings it can see, and Lab attaches 500
    cells over several seconds, so lab.js runs it once the count settles.
    """
    here = Path.cwd()
    css = [here / n for n in CHROME_CSS]
    js, toc = here / CHROME_JS, here / TOC_JS
    if not js.exists():
        if not quiet:
            print(f"nbdoc.chrome(): no {CHROME_JS} in {here} — skipped")
        return
    parts = ['<div class="nbdoc-style-host"></div>']
    for p in css:
        if p.exists():
            parts.append(f"<style>\n/* ===== {p.name} ===== */\n"
                         + p.read_text(encoding="utf-8") + "\n</style>")
    if toc.exists():
        # Parked, not run. The closing tag has to be broken up or the browser
        # ends this script element at the first </script> inside the payload.
        parts.append('<script type="text/plain" id="nbdoc-toc-src">'
                     + toc.read_text(encoding="utf-8").replace("</script", "<\\/script")
                     + "</script>")
    parts.append("<script>\n" + js.read_text(encoding="utf-8") + "\n</script>")
    display(HTML("\n".join(parts)))
    if not quiet:
        print("chrome from " + ", ".join(p.name for p in css + [toc, js] if p.exists()))


_chrome = chrome


def _rows(path):
    with Path(path).open(encoding="utf-8", newline="") as f:
        return list(_csv.DictReader(f))


def _finish(ax, title, note):
    if title:
        ax.set_title(title, loc="left", pad=10)
    if note:
        ax.text(1.0, 1.02, note, transform=ax.transAxes, ha="right", va="bottom",
                fontsize=8.5, color=FAINT)
    try:
        ax.figure.tight_layout()
    except Exception:
        pass
    # Nothing is returned on purpose. The inline backend already displays the
    # figure; handing back an Axes prints its repr into the document above it.
    return None


def bar(path, title="", note="", ylabel="count", color=BLUE, median=None,
        size=DEFAULT_SIZE, rotate=None):
    """Bar chart from a two-column `label,value` CSV."""
    rows = _rows(path)
    labels = [r["label"] for r in rows]
    values = [float(r["value"]) for r in rows]
    fig, ax = plt.subplots(figsize=_autosize(len(values), size))
    ax.bar(range(len(values)), values, color=color, alpha=0.85, width=0.82)
    ax.set_xticks(range(len(labels)))
    if rotate is None:
        rotate = 45 if max((len(l) for l in labels), default=0) > 6 else 0
    ax.set_xticklabels(labels, rotation=rotate, ha="right" if rotate else "center")
    ax.set_ylabel(ylabel)
    ax.grid(axis="x", visible=False)
    if median is not None:
        pos = _bin_of(labels, median)
        if pos is not None:
            ax.axvline(pos, color=ACCENT, linestyle="--", linewidth=1)
            ax.text(pos + 0.15, ax.get_ylim()[1] * 0.92, f"median {median:g}",
                    color=ACCENT, fontsize=8.5)
    return _finish(ax, title, note)


_RANGE = re.compile(r"(-?[\d.]+)\s*[-\u2013\u2014to]+\s*(-?[\d.]+)")


def _bin_of(labels, value):
    """Which bar does `value` fall in? Labels look like `11-13 actions`.

    Returns a fractional index so the rule lands inside its bin rather than on
    the bar's left edge, or None when the labels carry no numeric range.
    """
    for i, lab in enumerate(labels):
        m = _RANGE.search(lab)
        if not m:
            continue
        lo, hi = float(m.group(1)), float(m.group(2))
        if lo <= value <= hi:
            span = (hi - lo) or 1
            return i - 0.5 + (value - lo) / span
    return None


def line(path, x, y, title="", note="", ylabel="", size=DEFAULT_SIZE, marker=""):
    """Line chart from a CSV. `y` is one column name or a list of them."""
    rows = _rows(path)
    ys = [y] if isinstance(y, str) else list(y)
    xs = [float(r[x]) for r in rows]
    fig, ax = plt.subplots(figsize=size)
    for i, col in enumerate(ys):
        ax.plot(xs, [float(r[col]) for r in rows], label=col,
                color=SERIES[i % len(SERIES)], linewidth=1.8, marker=marker)
    ax.set_xlabel(x)
    ax.set_ylabel(ylabel or (ys[0] if len(ys) == 1 else ""))
    if len(ys) > 1:
        ax.legend(loc="best")
    return _finish(ax, title, note)


def fig(path, caption="", width="100%"):
    """Show a pre-rendered image that `scripts/` produced. No compute here."""
    src = str(path)
    cap = f'<figcaption class="fig-note">{caption}</figcaption>' if caption else ""
    display(HTML(f'<figure class="nbdoc-fig"><img src="{src}" style="width:{width}">{cap}</figure>'))


def table(path, caption="", num_cols=None, index=False):
    """Render a CSV as a semantic HTML table.

    Semantic markup matters: the comment layer derives labels like
    "row - column" from real <th> cells when the export is read through it.
    """
    rows = _rows(path)
    if not rows:
        return
    cols = list(rows[0])
    num = set(num_cols or [c for c in cols if all(_isnum(r[c]) for r in rows)])
    head = "".join(f'<th class="{"num" if c in num else ""}">{c}</th>' for c in cols)
    body = "".join(
        "<tr>" + "".join(f'<td class="{"num" if c in num else ""}">{r[c]}</td>' for c in cols) + "</tr>"
        for r in rows)
    cap = f"<caption>{caption}</caption>" if caption else ""
    display(HTML(f"<table>{cap}<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"))


def _isnum(v):
    try:
        float(v)
        return True
    except (TypeError, ValueError):
        return False
