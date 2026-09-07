#!/usr/bin/env python3
"""Build index.html from data/schema.json + data/papers/*.json.

Two pages come out of the same template. index.html is the deliverable: one
self-contained file, no server, no fetch, no CDN, opens from file://.
review.html is the same page with the commentable-html layer inlined, for
marking the draft up before it ships. Readers get the first, we work on the
second, and the review scaffolding never reaches the deliverable.

    python3 build.py            # writes index.html and review.html
    python3 build.py --check    # validate only, write nothing
    python3 build.py --site DIR # assemble the public artifact in DIR

--site is what CI publishes. It writes the page and the raw database into a
fresh directory and nothing else, so build.py, serve.py and .claude/ stay out
of the deployed site. Working-tree index.html and review.html are untouched.
"""
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
TEMPLATE = ROOT / "src" / "template.html"
OUT = ROOT / "index.html"
REVIEW = ROOT / "review.html"
# comment-layer.* comes from the commentable-html skill; re-copy those two to
# upgrade it. comment-bridge.js is ours — it reconciles the layer with the tabs.
LAYER_CSS = [ROOT / "src" / "comment-layer.css"]
LAYER_JS = [ROOT / "src" / "comment-layer.js", ROOT / "src" / "comment-bridge.js"]

REQUIRED = ["id", "title", "year", "venue", "tldr", "arc"]


def load_papers():
    papers, seen = [], {}
    for f in sorted((DATA / "papers").glob("*.json")):
        try:
            chunk = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            sys.exit(f"! {f.name}: {e}")
        if not isinstance(chunk, list):
            sys.exit(f"! {f.name}: expected a JSON array")
        for p in chunk:
            for k in REQUIRED:
                if not p.get(k):
                    sys.exit(f"! {f.name}: paper {p.get('id', '?')} is missing '{k}'")
            if p["id"] in seen:
                sys.exit(f"! duplicate id '{p['id']}' in {f.name} and {seen[p['id']]}")
            seen[p["id"]] = f.name
            p["_src"] = f.name
            papers.append(p)
    return papers


def audit(schema, papers):
    """Report values that are not in the schema vocabulary. Not fatal — the
    vocabulary is meant to grow — but you want to know when it does."""
    vocab = {f["key"]: {v["v"] for v in f.get("vocab", [])}
             for f in schema["fields"] if f.get("vocab")}
    unknown = {}
    for p in papers:
        for key, allowed in vocab.items():
            val = p.get(key)
            vals = val if isinstance(val, list) else ([val] if val else [])
            for v in vals:
                if v not in allowed:
                    unknown.setdefault(key, {}).setdefault(v, []).append(p["id"])
    for key, vals in unknown.items():
        for v, ids in vals.items():
            print(f"  new value  {key}={v}  ({', '.join(ids[:4])}"
                  f"{'…' if len(ids) > 4 else ''})")
    return unknown


def read_all(paths):
    out = []
    for f in paths:
        if not f.exists():
            sys.exit(f"! missing {f.relative_to(ROOT)} — copy it from the "
                     f"commentable-html skill's assets/")
        out.append(f"/* {f.name} */\n" + f.read_text(encoding="utf-8"))
    return "\n".join(out)


def fill_review(html, on):
    """Inline the comment layer, or strip its three placeholders."""
    if not on:
        return (html.replace("__PHYSAI_REVIEW_ATTRS__", "")
                    .replace("__PHYSAI_REVIEW_CSS__", "")
                    .replace("__PHYSAI_REVIEW_JS__", ""))
    css = read_all(LAYER_CSS)
    js = read_all(LAYER_JS)
    # the only sequence that can end the inline block early
    js = js.replace("</script", "<\\/script").replace("</SCRIPT", "<\\/SCRIPT")
    return (html
            .replace("__PHYSAI_REVIEW_ATTRS__",
                     ' data-comment-doc="physai" data-comment-root=".shell"')
            .replace("__PHYSAI_REVIEW_CSS__", f"<style>\n{css}\n</style>\n")
            .replace("__PHYSAI_REVIEW_JS__", f"<script>\n{js}\n</script>"))


def site_dir():
    """The DIR in `--site DIR`, or None."""
    if "--site" not in sys.argv:
        return None
    i = sys.argv.index("--site") + 1
    if i >= len(sys.argv):
        sys.exit("! --site needs a directory")
    return Path(sys.argv[i]).expanduser()


def emit_site(page, dest):
    """Assemble the deployed artifact: the page, plus the raw database beside it.

    Publishing data/ is deliberate. The page is one view over the database and
    the JSON is the database, so anyone can fetch it without scraping the HTML.
    Everything not written here is absent from the site.
    """
    if dest.exists():
        shutil.rmtree(dest)
    (dest / "data" / "papers").mkdir(parents=True)
    (dest / "index.html").write_text(page, encoding="utf-8")
    sources = [DATA / "schema.json", *sorted((DATA / "papers").glob("*.json"))]
    for src in sources:
        shutil.copyfile(src, dest / src.relative_to(DATA.parent))
    print(f"wrote {dest}/  ({len(page)/1024:.0f} KB page + {len(sources)} data files)")


def main():
    schema = json.loads((DATA / "schema.json").read_text(encoding="utf-8"))
    papers = load_papers()
    papers.sort(key=lambda p: (p.get("date") or f"{p['year']}-00"), reverse=True)

    print(f"{len(papers)} papers from {len(set(p['_src'] for p in papers))} files")
    audit(schema, papers)

    counts = {}
    for p in papers:
        for a in (p.get("arc") or []):
            counts[a] = counts.get(a, 0) + 1
    print("  arcs:", ", ".join(f"{k}={v}" for k, v in sorted(counts.items())),
          f", closed-loop={sum(1 for p in papers if p.get('closes_loop'))}")

    if "--check" in sys.argv:
        return

    blob = json.dumps({"schema": schema, "papers": papers},
                      ensure_ascii=False, separators=(",", ":"))
    # keep the JSON safe inside <script type="application/json">
    blob = blob.replace("</", "<\\/").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")

    html = TEMPLATE.read_text(encoding="utf-8")
    if "__PHYSAI_DATA__" not in html:
        sys.exit("! template has no __PHYSAI_DATA__ placeholder")
    html = html.replace("__PHYSAI_DATA__", blob)

    dest = site_dir()
    if dest:
        emit_site(fill_review(html, False), dest)
        return

    for path, review in ((OUT, False), (REVIEW, True)):
        page = fill_review(html, review)
        path.write_text(page, encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}  ({len(page)/1024:.0f} KB)"
              + ("  [comment layer]" if review else ""))


if __name__ == "__main__":
    main()
