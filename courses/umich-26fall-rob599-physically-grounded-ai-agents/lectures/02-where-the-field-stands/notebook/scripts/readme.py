#!/usr/bin/env python3
"""readme — write the lecture folder's README.md from doc.ipynb, for GitHub.

    python3 scripts/readme.py              # ../README.md + assets/charts/*.svg

GitHub renders a folder's README.md under its file list, so this is what a reader
sees when they open the lecture folder on the site. It is the notebook's cells in
order, with the HTML GitHub's sanitizer would flatten rewritten into tags it keeps:

    class="done" / "todo" / "yr"     bold, plain, bold          (GitHub drops class)
    div.callout                      blockquote
    div.pair                         a two-column table
    div.gal (figures in a row)       a one-row table of images with captions under
    chart outputs                    assets/charts/<name>.svg, since GitHub drops data: URIs
    > [C] comment lines              removed
    src="assets/img/…"               src="notebook/assets/img/…", the README sits one level up

Generated, and committed, because GitHub cannot run the notebook. Edit doc.ipynb
and run this again (scripts/make.sh does).
"""
import re
import sys
from pathlib import Path

import nbformat as nbf

HERE = Path(__file__).resolve().parent.parent           # notebook/
OUT = HERE.parent / "README.md"                          # the lecture folder
CHARTS = HERE / "assets" / "charts"
STYLE_TAG = "nbdoc-style"
PREFIX = "notebook/"                                     # README -> notebook/ paths
WIDTH = 880                                              # GitHub's README column, roughly
NOTE = ("<!-- Generated from notebook/doc.ipynb by notebook/scripts/readme.py. "
        "Edit the notebook, not this file. -->\n")


# ----------------------------------------------------------------- markdown cells
def strip_comments(src: str) -> str:
    """Drop every blockquote that opens with `> [C]`, the author's notes."""
    return re.sub(r"^> \[C\].*\n(?:^>.*\n?)*", "", src, flags=re.M)


def rewrite_map(src: str) -> str:
    src = re.sub(r'<(span|b) class="done">(.*?)</\1>', r"<b>\2</b>", src)
    src = re.sub(r'<(span|b) class="todo">(.*?)</\1>', r"\2", src)
    src = re.sub(r'<span class="grp">(.*?)</span>', r"<b>\1</b>", src)
    src = re.sub(r'<span class="lbl">(.*?)</span>', r"<i>\1</i>", src)
    src = re.sub(r'<span class="sep">(.*?)</span>', r"\1", src)
    src = re.sub(r'<span class="yr">(.*?)</span>', r"<b>\1</b>", src)
    src = re.sub(r'<pre class="flow(?: map)?">', "<pre>", src)
    return src


def rewrite_callouts(src: str) -> str:
    """div.callout -> blockquote, its .t title in bold on its own line."""
    def one(m):
        body = m.group(1)
        body = re.sub(r'<span class="t">(.*?)</span>\s*', r"<b>\1</b><br>", body, count=1)
        return "<blockquote>" + body + "</blockquote>"
    return re.sub(r'<div class="callout[^"]*">(.*?)</div>', one, src, flags=re.S)


def rewrite_pairs(src: str) -> str:
    """div.pair with two inner divs -> a two-column table. The non-greedy match
    stops before the pair's own closing tag, so the last inner </div> is put back."""
    def one(m):
        cells = re.findall(r"<div>(.*?)</div>", m.group(1) + "</div>", flags=re.S)
        tds = []
        for c in cells:
            c = re.sub(r'<span class="t">(.*?)</span>\s*', r"<b>\1</b><br>", c, count=1)
            tds.append(f'<td valign="top" width="50%">{c.strip()}</td>')
        return "<table><tr>" + "".join(tds) + "</tr></table>"
    return re.sub(r'<div class="pair">(.*?)</div>\s*</div>', one, src, flags=re.S)


def rewrite_galleries(src: str) -> str:
    """div.gal of figures -> one table row of images, captions in the row under."""
    src = re.sub(r'<div class="rowlbl[^"]*">(.*?)</div>\s*', r"<b>\1</b>\n", src)

    def one(m):
        n = int(m.group(1))
        figs = re.findall(r'<figure><img src="([^"]+)" alt=""><figcaption>(.*?)</figcaption></figure>',
                          m.group(2), flags=re.S)
        if not figs:
            return m.group(0)
        w = WIDTH // n
        imgs = "".join(f'<td valign="top" width="{100 // n}%"><img src="{PREFIX}{f}" width="{w}"></td>'
                       for f, _ in figs)
        caps = "".join(f'<td valign="top"><sub>{c.strip()}</sub></td>' for _, c in figs)
        return f"<table><tr>{imgs}</tr><tr>{caps}</tr></table>"
    return re.sub(r'<div class="gal c(\d)[^"]*">(.*?)</div>', one, src, flags=re.S)


def rewrite_title(src: str) -> str:
    m = re.match(r'<h1><span class="kicker">(.*?)</span>(.*?)</h1>', src, flags=re.S)
    if not m:
        return src
    kicker, title = m.group(1).strip(), m.group(2).strip()
    return (f"# {title}\n\n{kicker}. This page is exported from [the notebook]({PREFIX}doc.ipynb), "
            f"which is the editable, presentable form. Open it with `bash {PREFIX}lab.sh`.")


def markdown(src: str) -> str:
    src = strip_comments(src)
    src = rewrite_title(src)
    src = rewrite_map(src)
    src = rewrite_callouts(src)
    src = rewrite_pairs(src)
    src = rewrite_galleries(src)
    src = re.sub(r'<table class="[^"]*">', "<table>", src)
    src = re.sub(r'<(th|td) class="[^"]*">', r"<\1>", src)
    src = src.replace('src="assets/img/', f'src="{PREFIX}assets/img/')
    return src.strip()


# --------------------------------------------------------------------- code cells
def chart_name(src: str, i: int) -> str:
    m = re.search(r'data/([\w-]+)\.csv', src)
    return f"{i:02d}-{m.group(1) if m else 'chart'}"


def code(cell, i: int) -> str:
    if STYLE_TAG in (cell.metadata.get("tags") or []):
        return ""
    parts = []
    for o in cell.get("outputs", []):
        data = o.get("data", {})
        if "image/svg+xml" in data:
            svg = data["image/svg+xml"]
            svg = "".join(svg) if isinstance(svg, list) else svg
            name = chart_name(cell.source, i) + ".svg"
            (CHARTS / name).write_text(svg, encoding="utf-8")
            parts.append(f'<img src="{PREFIX}assets/charts/{name}">')
        elif "text/html" in data:
            html = data["text/html"]
            html = "".join(html) if isinstance(html, list) else html
            html = re.sub(r' class="[^"]*"', "", html)
            parts.append(html.strip())
    return "\n\n".join(parts)


def main():
    nb = nbf.read(str(HERE / "doc.ipynb"), as_version=4)
    CHARTS.mkdir(parents=True, exist_ok=True)
    for old in CHARTS.glob("*.svg"):
        old.unlink()
    blocks = [NOTE]
    for i, c in enumerate(nb.cells):
        text = markdown(c.source) if c.cell_type == "markdown" else code(c, i)
        if text:
            blocks.append(text)
    OUT.write_text("\n\n".join(blocks) + "\n", encoding="utf-8")
    charts = sorted(p.name for p in CHARTS.glob("*.svg"))
    print(f"wrote {OUT.relative_to(HERE.parent.parent)}  ({OUT.stat().st_size // 1024} KB, "
          f"{len(blocks) - 1} blocks, {len(charts)} charts in assets/charts/)")
    left = re.findall(r'class="([^"]+)"', OUT.read_text(encoding="utf-8"))
    if left:
        print("  classes GitHub will drop:", sorted(set(left)), file=sys.stderr)


if __name__ == "__main__":
    main()
