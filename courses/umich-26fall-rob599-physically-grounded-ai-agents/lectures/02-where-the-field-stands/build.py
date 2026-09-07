#!/usr/bin/env python3
"""build — turn doc.ipynb into the reading copy and the deck.

    python3 build.py                # doc.html + deck.html
    python3 build.py --share        # also share.html: comments stripped, comment layer wired
    python3 build.py --no-exec      # skip execution (fast, stale figures)
    python3 build.py --clean        # strip comment blockquotes from doc.html too

Run it from the deliverable folder. Cells are meant to be cheap — they load what
`scripts/` already wrote — so executing on every build stays fast and the
committed notebook can carry no outputs at all.

Outputs are named after the notebook, so a folder can hold several documents:
doc.ipynb writes doc.html + deck.html, doc_2.ipynb writes doc_2.html + deck_2.html.

    <stem>.html         the reading copy: your CSS, a foldable TOC, comments as callouts
    <deck>.html         reveal.js, one h2 per slide, every body block a fragment,
                        navigationMode linear so one key walks the whole thing
    <stem>-share.html   --share only: no comments in the prose, comment-layer.js wired
"""
from __future__ import annotations

import argparse, re, shutil, sys
from pathlib import Path

import nbformat as nbf
from nbconvert import HTMLExporter, SlidesExporter
from nbconvert.preprocessors import ExecutePreprocessor
from traitlets.config import Config

HERE = Path(__file__).resolve().parent
COMMENT_RE = re.compile(r"^>\s*\[C\].*$", re.M)

# The deck needs the document's stylesheet rewritten, and nbdoc.py already owns
# that rewriter — it is what puts the same sheet into a live notebook. The two
# ship together in every deliverable, so import it rather than keep a second
# parser in step. DECK_SCOPE is why: nbconvert's slides template embeds the whole
# of JupyterLab's stylesheet, and reveal ships a theme, so every prose element is
# styled through a selector one class deep — `.jp-RenderedHTMLCommon h1`,
# `.reveal h1`. A document sheet names those elements bare and loses every one of
# those contests, which is what made the deck stop looking like the document:
# headings unbolded, half again too large and pure black, table cells
# right-aligned. Two classes of prefix is enough to win them all back.
sys.path.insert(0, str(HERE))
try:
    from nbdoc import scope_css
except ImportError:                      # a folder without nbdoc.py still exports
    scope_css = None

DECK_SCOPE = ".reveal .slides"           # the slide container: beats both vendors
DECK_ROOT = ".reveal"                    # what `body` / `#content` map onto
DECK_SCOPED = (".reveal", ":root", "html")


def deck_css(css: str) -> str:
    """The document's sheet, rewritten to outrank the deck's vendored CSS."""
    if scope_css is None:
        print("  ! nbdoc.py not importable: deck typography will be reveal's, "
              "not the document's", file=sys.stderr)
        return css
    return scope_css(css, DECK_SCOPE, DECK_ROOT, DECK_SCOPED)


def deck_name(stem: str) -> str:
    """`doc` -> `deck.html`, `doc_2` -> `deck_2.html`, anything else -> `<stem>-deck.html`.

    lab.js's Present button computes this same name from the open notebook's path,
    so the rule has to be derivable from the stem alone and stay in step on both
    sides. Keeping "doc" and "deck" as a matched pair is what makes a folder of
    several documents readable.
    """
    return ("deck" + stem[3:] + ".html") if stem == "doc" or stem.startswith("doc_") else stem + "-deck.html"

KATEX_LOCAL = "assets/katex"
KATEX_CDN = "https://cdn.jsdelivr.net/npm/katex@0.16.9/dist"
REVEAL_CDN = "https://unpkg.com/reveal.js@4.0.2"

PAGE = """<!doctype html>
<html lang="en"{comment_attrs}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
{comment_css}
<link rel="stylesheet" href="{katex}/katex.min.css">
<script defer src="{katex}/katex.min.js"></script>
<script defer src="{autorender}"></script>
<script>
document.addEventListener("DOMContentLoaded", function () {{
  if (window.renderMathInElement) renderMathInElement(document.body, {{
    delimiters: [
      {{left: "$$", right: "$$", display: true}},
      {{left: "\\\\[", right: "\\\\]", display: true}},
      {{left: "$", right: "$", display: false}}
    ],
    macros: {macros},
    throwOnError: false
  }});
}});
</script>
<style>
{css}
</style>
</head>
<body>
<main id="content">
{body}
</main>
{scripts}
</body>
</html>
"""


def strip_comments(nb):
    """Remove `> [C]` blockquote lines from every markdown cell."""
    out = nbf.v4.new_notebook(metadata=nb.metadata)
    for c in nb.cells:
        c = c.copy()
        if c.cell_type == "markdown":
            c.source = COMMENT_RE.sub("", c.source).strip()
            if not c.source:
                continue
        out.cells.append(c)
    return out


def execute(nb, cwd: Path):
    ep = ExecutePreprocessor(timeout=300, kernel_name=nb.metadata.get(
        "kernelspec", {}).get("name", "python3"))
    ep.preprocess(nb, {"metadata": {"path": str(cwd)}})
    return nb


def body_html(nb) -> str:
    c = Config()
    c.HTMLExporter.template_name = "basic"
    c.HTMLExporter.exclude_input = True
    c.HTMLExporter.exclude_input_prompt = True
    c.HTMLExporter.exclude_output_prompt = True
    body = HTMLExporter(config=c).from_notebook_node(nb)[0]
    return mark_comments(rewrap_containers(body, nb))


def deck_html(nb, reveal_prefix: str) -> str:
    c = Config()
    c.SlidesExporter.exclude_input = True
    c.SlidesExporter.exclude_input_prompt = True
    c.SlidesExporter.exclude_output_prompt = True
    c.SlidesExporter.reveal_url_prefix = reveal_prefix
    c.SlidesExporter.reveal_transition = "none"
    c.SlidesExporter.reveal_theme = "simple"
    c.SlidesExporter.reveal_scroll = True
    return SlidesExporter(config=c).from_notebook_node(nb)[0]


# --------------------------------------------------------------- standalone deck
# nbconvert's slides template loads jQuery and require.js from a CDN and then
# pulls reveal in as an AMD module from a *relative* path. That works off a plain
# static server and nowhere else. Jupyter serves /files/ with
# `Content-Security-Policy: sandbox allow-scripts`, which puts the page in an
# opaque origin; its own subresource requests then carry no cookie, the server
# answers each one with a 302 to the login page, and require.js reports
# "Script error" — reveal never initializes, so in the deck opened from Lab no
# key does anything at all. Folding the four vendored files into the page removes
# every same-origin request, so the deck also travels as a single file. MathJax
# and mermaid stay on their CDNs: cross-origin subresources need no cookie and
# load fine in the sandbox, so only the vendored files had to move.
REQUIRE_BOOT = re.compile(r"<script>\s*require\(.*?\)\s*;?\s*</script>", re.S)
CDN_SCRIPT = re.compile(
    r'<script src="https://cdnjs\.cloudflare\.com/ajax/libs/(?:jquery|require\.js)/[^"]*"></script>')

DECK_BOOT = """<script>
// The slides carry a document's worth of content, so reveal's default sizing —
// scale one fixed 960x700 design box until it fits — is wrong here twice over.
// The scale ends up pinned by the *height*, which blows the type up about 1.9x
// and leaves a wide gutter down each side; and whatever runs past 700px is cut
// off in silence, because reveal gives an overflowing slide no scrollbar. A box
// that tracks the window's aspect ratio fixes both at once: it stays DESIGN_W
// wide and is as tall as the window is in proportion, so the scale is driven by
// the width alone (innerWidth / DESIGN_W) and the gutters go to zero. Anything
// still too tall then scrolls inside its own slide, which the deck stylesheet
// in build.py turns on.
var DESIGN_W = 1040;   // the document's 920px column plus a gutter each side

function deckBox() {
  var w = window.innerWidth || DESIGN_W, h = window.innerHeight || 720;
  return { width: DESIGN_W, height: Math.max(320, Math.round(DESIGN_W * h / w)) };
}

Reveal.initialize({
  navigationMode: "linear",   // one key walks sections, subsections and fragments
  controls: true, progress: true, history: true, transition: "none",
  slideNumber: false,
  width: deckBox().width, height: deckBox().height,
  margin: 0,       // the gutter is padding in DECK_CSS, so it cannot eat the scale
  center: false,   // a slide shaped like a document page reads from its top edge
  // reveal stops at 2x by default. The box tracks the window, so the scale it
  // wants is innerWidth / DESIGN_W and nothing else — capping it puts the side
  // gutters straight back, which is the thing the tracking exists to remove.
  minScale: 0.2, maxScale: 6,
  plugins: [RevealNotes]
});

// height is a function of the window, so it has to be recomputed rather than set
// once. reveal relays out on resize either way; this only corrects the number.
window.addEventListener('resize', function () { Reveal.configure(deckBox()); });

// The template's version of this assumed MathJax was already up and threw on
// every slide change until it was. Ask before using it.
Reveal.addEventListener('slidechanged', function () {
  if (window.MathJax && MathJax.Hub && MathJax.Hub.getAllJax(Reveal.getCurrentSlide()))
    MathJax.Hub.Rerender(Reveal.getCurrentSlide());
});

// A fragment takes up no space until it is shown, so a tall slide grows downward
// as you advance and the block you just revealed can land below the fold — there,
// but only reachable by hand. Bringing it into view is what keeps one key enough
// to present with: the same press reveals the block and scrolls to it.
//
// Two things reveal's scaled wrapper breaks, both found by measuring rather than
// by reading: element.scrollIntoView() mixes the scaled and unscaled coordinate
// spaces, so asked to reveal a block 900px below the fold Chrome moved the
// scroller 12px and stopped; and `behavior: "smooth"` on a scroller inside the
// transform does nothing at all, silently, while the same call with "auto" moves
// it. So: measure by hand, divide the rectangles by Reveal.getScale() to put them
// back in the scroller's own units, and set scrollTop directly. The jump is
// instant, which for presenting is the better of the two anyway — no lag between
// the key and the words.
function scrollBoxOf(el) {
  for (var n = el; n && !n.classList.contains('slides'); n = n.parentElement) {
    var oy = getComputedStyle(n).overflowY;
    if ((oy === 'auto' || oy === 'scroll') && n.scrollHeight > n.clientHeight + 1) return n;
  }
  return null;
}

function bringIntoView(el) {
  var box = el && scrollBoxOf(el);
  if (!box) return;
  var k = Reveal.getScale() || 1, pad = 24;
  var er = el.getBoundingClientRect(), br = box.getBoundingClientRect();
  var top = (er.top - br.top) / k + box.scrollTop, h = er.height / k;
  // A block taller than the slide is pinned by its top; there is no scroll
  // position that shows all of it, and its first line is the one to read.
  if (h > box.clientHeight - pad) box.scrollTop = Math.max(0, top - pad);
  else if (top + h > box.scrollTop + box.clientHeight)
    box.scrollTop = top + h - box.clientHeight + pad;
  else if (top < box.scrollTop + pad) box.scrollTop = Math.max(0, top - pad);
}

Reveal.addEventListener('fragmentshown', function (e) { bringIntoView(e.fragment); });

// Stepping back hides a fragment, so the one to scroll to is the last still shown.
Reveal.addEventListener('fragmenthidden', function () {
  var slide = Reveal.getCurrentSlide();
  if (!slide) return;
  var shown = slide.querySelectorAll('.fragment.visible');
  if (shown.length) { bringIntoView(shown[shown.length - 1]); return; }
  var box = scrollBoxOf(slide.firstElementChild) || slide;
  box.scrollTop = 0;
});

// Arriving on a slide should start at its top, not wherever it was left last time.
Reveal.addEventListener('slidechanged', function (e) {
  var s = e.currentSlide;
  if (!s) return;
  s.scrollTop = 0;
  if (s.parentElement && s.parentElement.tagName === 'SECTION') s.parentElement.scrollTop = 0;
});
</script>"""


# The document's own stylesheet lays out a page; a slide is a different box.
# These are the only rules that differ, and every one is scoped under `.reveal`
# so none of it can reach the reading copy.
DECK_CSS = """
/* reveal sets `padding: 20px 0` through exactly these two selectors, which is
   what a rule written as `.reveal .slides section` silently loses to. Matching
   its shape is what makes the padding land. `height: 100%` plus `overflow-y` is
   the scrollbar reveal never gives an over-long slide, and without it the last
   lines of a slide are simply cut off. */
.reveal .slides > section:not(.stack),
.reveal .slides > section > section {
  padding: 30px 0 44px; height: 100%; overflow-y: auto; overflow-x: hidden;
  /* reveal sizes the slide at 1.25em/1.3 of its own; the document sizes itself,
     and the scoped `body` rule has already put those values on `.reveal`. */
  font-size: inherit; line-height: inherit;
}
/* A `.stack` is the h-slide wrapping a column of h3 subslides — a container, not
   a slide. Scrolling belongs to whichever subslide is showing, so leaving the
   stack scrollable too paints a second, dead scrollbar beside the live one. */
.reveal .slides > section.stack {
  padding: 0; height: 100%; overflow: hidden;
  /* the subslides inherit through here, so it has to pass the values on too */
  font-size: inherit; line-height: inherit;
}
/* The measure, the same 920px column the reading copy sets on `#content`, so a
   line breaks in the deck where it breaks in the document. `:not(section)` keeps
   it off the nested subslides, which reveal positions absolutely and sizes for
   itself; a max-width on those shifts them off centre. */
.reveal .slides section > :not(section) {
  max-width: 920px; margin-left: auto; margin-right: auto;
}
/* Everything the document does not say. On a page a heading is bold and inherits
   its colour and line-height from the body, and a list item inherits its size —
   the document never has to write that down. In the deck both vendored sheets do
   write it down, at `.reveal h1` and `.jp-RenderedHTMLCommon h1`, where a bare
   `h1` was never in the contest. `:is()` keeps these at one class, so they beat
   the vendors and still lose to the document's own rules, which the scoper put
   two classes up. */
.reveal :is(h1, h2, h3, h4, h5, h6) {
  color: inherit; font-weight: bold; line-height: inherit;
  text-transform: none; text-shadow: none;
}
.reveal :is(ul, ol, li) { font-size: inherit; }

/* reveal scores every slide's background and switches to white text where it
   reads dark. An unpainted background element reads back as transparent black,
   so it reaches that verdict about a white page, and `section.has-dark-background
   h1` is one element more specific than anything a document sheet can say — the
   headings turn white on white and stay there. Reading the real colour back off
   the page is not the fix either: a dark-mode browser extension rewrites it
   first, so the value is whatever that extension chose. The document owns its
   colours, so take the guess out of the cascade instead. */
.reveal .slides .has-dark-background,
.reveal .slides .has-dark-background :is(h1, h2, h3, h4, h5, h6) { color: inherit; }

/* nbconvert builds slides out of JupyterLab's own cell markup, so the deck's DOM
   is not the reading copy's: prose sits inside `.jp-RenderedHTMLCommon` and
   figures inside `.jp-RenderedSVG`, and those containers carry Lab's colour, its
   font size and its `white-space: pre-wrap` — which would fold the ASCII flow
   diagrams. The document's sheet names the containers nbconvert's `basic`
   template emits instead (`.output_svg`, `.output_png`), so it never reaches
   these. Inheritance is the whole fix: let the containers pass the document's
   values through rather than setting their own. */
.reveal .slides :is(.jp-Cell, .jp-RenderedHTMLCommon, .jp-OutputArea-output) {
  color: inherit; font-size: inherit; line-height: inherit;
  /* Lab makes each cell its own scroll box, which inside a slide reserves a
     second scrollbar beside the slide's own. The slide is the scroll box here. */
  overflow: visible;
}
.reveal .slides pre { white-space: pre; }
.reveal .slides :is(.jp-RenderedSVG, .jp-RenderedImage) :is(img, svg) {
  display: block; margin: 14px auto; max-width: 100%;
}

.reveal .comment-callout { display: none }
"""


def read_asset(path: Path) -> str:
    """Inline-safe text. `</script` inside a JS string would close the tag early."""
    return path.read_text(encoding="utf-8").replace("</script", "<\\/script")


def standalone_deck(html: str, folder: Path) -> str:
    """Fold the vendored reveal into the page and drop the AMD boot."""
    rev = folder / "assets/reveal"
    css = [rev / "dist/reveal.css", rev / "dist/theme/simple.css"]
    js = [rev / "dist/reveal.js", rev / "plugin/notes/notes.js"]
    if not all(p.exists() for p in css + js):
        return html                      # CDN build: cross-origin assets, nothing to fold

    html = CDN_SCRIPT.sub("", html)
    html = html.replace('<link href="assets/reveal/dist/reveal.css" rel="stylesheet"/>',
                        "<style>\n" + css[0].read_text(encoding="utf-8") + "\n</style>", 1)
    html = html.replace('<link href="assets/reveal/dist/theme/simple.css" id="theme" rel="stylesheet"/>',
                        '<style id="theme">\n' + css[1].read_text(encoding="utf-8") + "\n</style>", 1)
    # With require.js gone, reveal's UMD wrapper falls through to window.Reveal
    # and window.RevealNotes, which is what DECK_BOOT expects.
    inlined = "".join("<script>\n" + read_asset(p) + "\n</script>\n" for p in js)
    # A function replacement, because re treats a replacement *string* as a template
    # and reveal.js is full of regex literals whose backslashes it would try to expand.
    boot, n = REQUIRE_BOOT.subn(lambda _m: inlined + DECK_BOOT, html)
    if n != 1:
        raise SystemExit("build: nbconvert's require() boot block was not found; "
                         "the slides template changed, so the deck would ship broken")
    return boot


CMT_BQ = re.compile(r"<blockquote>(.*?)</blockquote>", re.S)
CELL_SPLIT = re.compile(r'(?m)^(?=<div class="cell )')
CELL_ID = re.compile(r'id="cell-id=([^"]+)"')


def rewrap_containers(html: str, nb) -> str:
    """Put back the wrapper elements the cells were flattened out of.

    html2nb descends through a <div> that wraps a whole section, so the section
    becomes hundreds of cells instead of one. The wrapper still matters — page CSS
    targets it by id, e.g. a media query that lets one results section break out of
    the prose measure — so the export rebuilds it around the run of cells that came
    from it.
    """
    want = {c["id"]: tuple(
        (d.get("tag", "div"), d.get("id"), tuple(d.get("class") or ()))
        for d in c.metadata.get("nbdoc", {}).get("container", []))
        for c in nb.cells}
    if not any(want.values()):
        return html

    def open_tag(t):
        tag, cid, cls = t
        attrs = (f' id="{cid}"' if cid else "") + (f' class="{" ".join(cls)}"' if cls else "")
        return f"<{tag}{attrs}>"

    out, cur = [], ()
    for chunk in CELL_SPLIT.split(html):
        m = CELL_ID.search(chunk)
        stack = want.get(m.group(1), ()) if m else cur
        common = 0
        while common < min(len(cur), len(stack)) and cur[common] == stack[common]:
            common += 1
        out += [f"</{t[0]}>" for t in reversed(cur[common:])]
        out += [open_tag(t) for t in stack[common:]]
        out.append(chunk)
        cur = stack
    out += [f"</{t[0]}>" for t in reversed(cur)]
    return "".join(out)


def mark_comments(html: str) -> str:
    """Rewrite the `> [C] …` blockquotes into styled <aside> callouts.

    CSS cannot select on text, so the class has to be attached here rather than
    in doc.css. Blockquotes that are not comments are left exactly as they were.
    """
    def sub(m):
        inner = m.group(1)
        if "[C]" not in inner:
            return m.group(0)
        inner = inner.replace("[C]", "")
        inner = re.sub(r"<p>\s*on\s+(.*?)</p>",
                       r'<span class="cmt-on">on \1</span>', inner, count=1)
        return f'<aside class="cmt">{inner}</aside>'
    return CMT_BQ.sub(sub, html)


def read_css(folder: Path) -> str:
    parts = []
    for name in ("doc.css", "custom.css"):
        p = folder / name
        if not p.exists() and name == "doc.css":
            p = HERE / "doc.css"          # fall back to the skill's house sheet
        if p.exists():
            parts.append(f"/* ---- {p.name} ---- */\n" + p.read_text(encoding="utf-8"))
    return "\n\n".join(parts)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("notebook", nargs="?", default="doc.ipynb", type=Path)
    ap.add_argument("--share", action="store_true", help="also write share.html with the comment layer")
    ap.add_argument("--clean", action="store_true", help="hide comments in doc.html too")
    ap.add_argument("--no-exec", action="store_true", help="do not run the cells")
    ap.add_argument("--no-deck", action="store_true")
    a = ap.parse_args()

    folder = a.notebook.resolve().parent
    nb = nbf.read(str(a.notebook), as_version=4)
    meta = nb.metadata.get("nbdoc", {})
    doc_id = meta.get("doc_id", a.notebook.stem)
    title = meta.get("title", doc_id)
    stem = a.notebook.stem
    names = {"doc": f"{stem}.html", "deck": deck_name(stem), "share": f"{stem}-share.html"}

    if not a.no_exec:
        print("executing cells ...", flush=True)
        execute(nb, folder)

    katex = KATEX_LOCAL if (folder / KATEX_LOCAL / "katex.min.js").exists() else KATEX_CDN
    # Vendored KaTeX bundles here keep auto-render beside katex.min.js; the npm
    # layout puts it under contrib/. Probe rather than assume.
    autorender = f"{katex}/auto-render.min.js"
    if katex == KATEX_LOCAL and not (folder / KATEX_LOCAL / "auto-render.min.js").exists():
        autorender = f"{katex}/contrib/auto-render.min.js"
    elif katex == KATEX_CDN:
        autorender = f"{katex}/contrib/auto-render.min.js"
    macros = meta.get("katex_macros", {})
    css = read_css(folder)

    def page(nbn, name, with_layer):
        scripts = ""
        attrs = ""
        ccss = ""
        if (folder / "toc-layer.js").exists():
            scripts += '<script src="toc-layer.js"></script>\n'
            ccss += '<link rel="stylesheet" href="toc-layer.css">\n'
        if with_layer and (folder / "comment-layer.js").exists():
            attrs = f' data-comment-doc="{doc_id}" data-comment-root="#content"'
            ccss += '<link rel="stylesheet" href="comment-layer.css">\n'
            scripts += '<script src="comment-layer.js"></script>\n'
        html = PAGE.format(title=title, katex=katex, autorender=autorender, css=css, body=body_html(nbn),
                           macros=repr(macros).replace("'", '"'),
                           comment_attrs=attrs, comment_css=ccss.rstrip(), scripts=scripts.rstrip())
        (folder / name).write_text(html, encoding="utf-8")
        print(f"  {name}  {len(html)/1024:.0f} KB")

    page(strip_comments(nb) if a.clean else nb, names["doc"], with_layer=False)

    if a.share:
        page(strip_comments(nb), names["share"], with_layer=True)

    if not a.no_deck:
        prefix = "assets/reveal" if (folder / "assets/reveal/dist/reveal.js").exists() else REVEAL_CDN
        html = deck_html(strip_comments(nb), prefix)
        extra = "<style>\n" + deck_css(css) + "\n" + DECK_CSS + "\n</style>"
        html = html.replace("</head>", extra + "\n</head>", 1)
        # DECK_BOOT replaces nbconvert's Reveal.initialize wholesale, which is also
        # where navigationMode gets set — nbconvert exposes no traitlet for it, and
        # the reveal default is axis-locked: -> walks the h2 sections and skips every
        # h3 under them, so presenting with -> silently drops half the deck.
        html = standalone_deck(html, folder)
        (folder / names["deck"]).write_text(html, encoding="utf-8")
        print(f"  {names['deck']}  {len(html)/1024:.0f} KB   (reveal: {prefix})")


if __name__ == "__main__":
    main()
