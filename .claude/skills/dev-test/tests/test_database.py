#!/usr/bin/env python3
"""Validation surface for the awesome-physical-ai database.

Every check here enforces a rule written down in
.claude/skills/dev-handbook/conventions.md. If you add a convention, add a check.
If a check is wrong, fix the convention first.

Runs standalone with no dependencies:

    python3 .claude/skills/dev-test/tests/test_database.py

Also works under pytest if it happens to be installed:

    pytest .claude/skills/dev-test/
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SCHEMA = json.loads((ROOT / "data" / "schema.json").read_text(encoding="utf-8"))
FILES = sorted((ROOT / "data" / "papers").glob("*.json"))
PAPERS = [p for f in FILES for p in json.loads(f.read_text(encoding="utf-8"))]
FIELD = {f["key"]: f for f in SCHEMA["fields"]}
VOCAB = {k: {v["v"] for v in f.get("vocab", [])} for k, f in FIELD.items() if f.get("vocab")}

# Fields whose text is user-visible and therefore bound by the prose rules.
PROSE_PATHS = [("tldr",), ("why",), ("method", "intuition"), ("experiments", "headline")]


def dig(obj, path):
    for k in path:
        if not isinstance(obj, dict):
            return None
        obj = obj.get(k)
    return obj


def vals(paper, key):
    v = paper.get(key)
    if isinstance(v, bool):
        return [str(v).lower()]
    return v if isinstance(v, list) else ([v] if v else [])


def prose(paper):
    """(label, text) for every user-visible prose cell on a paper."""
    for path in PROSE_PATHS:
        t = dig(paper, path)
        if isinstance(t, str) and t.strip():
            yield ".".join(path), t


# ---------------------------------------------------------------- data shape

def test_ids_unique_and_slugged():
    seen = {}
    bad = []
    for p in PAPERS:
        pid = p.get("id", "")
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", pid):
            bad.append(f"{pid!r} is not a kebab-case slug")
        if pid in seen:
            bad.append(f"duplicate id {pid!r} in {p.get('_src')} and {seen[pid]}")
        seen[pid] = p.get("_src")
    assert not bad, "\n".join(bad)


def test_required_fields():
    required = ["id", "title", "year", "venue", "tldr", "arc"]
    bad = [f"{p.get('id', '?')}: missing {k}" for p in PAPERS for k in required if not p.get(k)]
    assert not bad, "\n".join(bad)


def test_dates_consistent():
    bad = []
    for p in PAPERS:
        d = p.get("date")
        if d is None:
            continue
        if not re.fullmatch(r"\d{4}-\d{2}", d):
            bad.append(f"{p['id']}: date {d!r} is not YYYY-MM")
        elif int(d[:4]) != p["year"]:
            bad.append(f"{p['id']}: date {d} disagrees with year {p['year']}")
    assert not bad, "\n".join(bad)


def test_no_grouping_fields():
    """Sections are filters over columns. A paper never names its own section."""
    banned = {"section", "category", "group", "folder", "bucket"}
    bad = [f"{p['id']}: has {k!r}" for p in PAPERS for k in p if k in banned]
    assert not bad, "\n".join(bad) + "\n(grouping belongs in schema.json views, not on a paper)"


def test_confidence_declared():
    bad = [p["id"] for p in PAPERS if p.get("confidence") not in {"high", "medium", "low"}]
    assert not bad, f"missing or invalid confidence: {bad}"


def test_links_are_urls():
    bad = [
        f"{p['id']}.{k}={v!r}"
        for p in PAPERS
        for k, v in (p.get("links") or {}).items()
        if v and not v.startswith(("http://", "https://"))
    ]
    assert not bad, "\n".join(bad)


def test_cells_are_short():
    """Comprehensive structure, short cells. A ceiling is a proxy for 'two sentences'."""
    limit = 340
    bad = [
        f"{p['id']}.{label} is {len(t)} chars (limit {limit})"
        for p in PAPERS
        for label, t in prose(p)
        if len(t) > limit
    ]
    assert not bad, "\n".join(bad)


# ---------------------------------------------------------- schema conformance

def test_values_declared():
    bad = []
    for p in PAPERS:
        for key, allowed in VOCAB.items():
            for v in vals(p, key):
                if v not in allowed:
                    bad.append(f"{p['id']}: {key}={v!r} is not in schema.json")
    assert not bad, "\n".join(bad) + "\n(add it to data/schema.json first, with a label)"


def test_no_empty_vocabulary_values():
    """An axis with no members is an untested claim about the field."""
    used = {k: set() for k in VOCAB}
    for p in PAPERS:
        for k in VOCAB:
            used[k].update(vals(p, k))
    bad = [f"{k}={v!r}" for k, allowed in VOCAB.items() for v in sorted(allowed - used[k])]
    assert not bad, ("vocabulary values with no paper:\n  " + "\n  ".join(bad)
                     + "\n(find the paper, or delete the value)")


def test_modalities_declared():
    declared = set(SCHEMA["modalities"])
    used = {
        c.get("modality")
        for p in PAPERS
        for side in ("inputs", "outputs")
        for c in (dig(p, ("problem", "inference", side)) or [])
        if c.get("modality")
    }
    assert not (used - declared), f"undeclared modalities: {sorted(used - declared)}"
    assert not (declared - used), f"declared but unused modalities: {sorted(declared - used)}"


def test_dataset_roles_declared():
    allowed = {r["v"] for r in SCHEMA["data_roles"]}
    bad = [
        f"{p['id']}: dataset role {d.get('role')!r}"
        for p in PAPERS
        for d in (dig(p, ("experiments", "datasets")) or [])
        if d.get("role") not in allowed
    ]
    assert not bad, "\n".join(bad)


def test_view_filters_reference_real_columns():
    bad = []
    for view in SCHEMA["views"]:
        for scope, filt in [(view["id"], view.get("filter", {}))] + [
            (g["id"], g.get("filter", {})) for g in view["groups"]
        ]:
            for key, want in filt.items():
                if key not in FIELD:
                    bad.append(f"{scope}: filters on unknown column {key!r}")
                    continue
                allowed = VOCAB.get(key)
                if allowed:
                    for w in (want if isinstance(want, list) else [want]):
                        if w not in allowed:
                            bad.append(f"{scope}: filters on {key}={w!r}, not in vocabulary")
    assert not bad, "\n".join(bad)


def test_every_group_claims_something():
    """A group nobody lands in is dead weight in the reading order."""
    def matches(p, filt):
        # JSON true -> Python "True"; vals() emits JS-style "true". Lower to meet it.
        def norm(w):
            return str(w).lower() if isinstance(w, bool) else str(w)

        return all(
            any(norm(w) in vals(p, k) for w in (want if isinstance(want, list) else [want]))
            for k, want in filt.items()
        )

    empty = []
    for view in SCHEMA["views"]:
        pool = [p for p in PAPERS if matches(p, view.get("filter", {}))]
        claimed = set()
        for g in sorted(view["groups"], key=lambda g: g.get("pri", 999)):
            got = [p for p in pool if p["id"] not in claimed and matches(p, g.get("filter", {}))]
            claimed.update(p["id"] for p in got)
            if not got:
                empty.append(f"{view['id']}/{g['id']} claims 0 papers")
        orphan = [p["id"] for p in pool if p["id"] not in claimed]
        if orphan:
            empty.append(f"{view['id']}: {len(orphan)} papers fall through every group: {orphan[:5]}")
    assert not empty, "\n".join(empty)


def test_group_priorities_are_unique():
    bad = []
    for view in SCHEMA["views"]:
        pris = [g.get("pri") for g in view["groups"]]
        if len(set(pris)) != len(pris) or None in pris:
            bad.append(f"{view['id']}: pri values must be present and distinct, got {pris}")
    assert not bad, "\n".join(bad)


# ------------------------------------------------------------------ prose voice

TITLES = " || ".join(p.get("title", "") for p in PAPERS).lower()

BLACKLIST = [
    "delve", "leverage", "leverages", "leveraging", "utilize", "utilizes", "utilizing",
    "robust", "comprehensive", "nuanced", "seamless", "pivotal", "holistic", "crucial",
    "landscape", "realm", "tapestry", "underscore", "underscores", "facilitate",
    "facilitates", "foster", "fosters", "elucidate", "novel",
    "load-bearing", "substrate", "provenance", "the unlock", "surface area",
    "table stakes", "scaffolding", "it's worth noting", "at its core",
    "worth stating plainly", "here's the thing", "a testament to", "paving the way",
]

ANTITHESIS = [
    r"\bnot just\b", r"\bnot only\b", r"\bit'?s not [a-z]+, it'?s\b",
    r"\bisn'?t (?:a |an |the )?[a-z]+[,;] it\b", r"\brather than a [a-z]+, it\b",
]


def test_no_clause_welding():
    """Split, do not glue. A semicolon or em-dash welding two clauses becomes two sentences."""
    bad = []
    for p in PAPERS:
        for label, t in prose(p):
            if ";" in t:
                bad.append(f"{p['id']}.{label}: semicolon\n    {t}")
            # A pair of em-dashes brackets an appositive and is fine. A lone one
            # followed by a finite clause is a weld.
            if t.count(" — ") == 1 and re.search(
                    r"\w — (?:and|but|so|then|which is why|it |they |this |that )", t):
                bad.append(f"{p['id']}.{label}: em-dash welding two clauses\n    {t}")
    assert not bad, "\n".join(bad)


def test_no_antithesis():
    bad = [
        f"{p['id']}.{label}: {pat}\n    {t}"
        for p in PAPERS
        for label, t in prose(p)
        for pat in ANTITHESIS
        if re.search(pat, t, re.I)
    ]
    assert not bad, "\n".join(bad) + "\n(delete the negated half and state the claim)"


def test_no_blacklist_words():
    """Paper titles are quotations and stay verbatim; our own prose does not."""
    bad = []
    for p in PAPERS:
        for label, t in prose(p):
            low = t.lower()
            for w in BLACKLIST:
                if not re.search(r"\b" + re.escape(w) + r"\b", low):
                    continue
                # allow it if it is quoting a title that is in the database
                if w in TITLES and w in (p.get("title", "").lower()):
                    continue
                bad.append(f"{p['id']}.{label}: {w!r}\n    {t}")
    assert not bad, "\n".join(bad)


def test_schema_prose_is_clean():
    """The blurbs and help strings render on the page and obey the same rules."""
    texts = []
    texts.append(("thesis.line", SCHEMA["thesis"]["line"]))
    texts.append(("thesis.body", SCHEMA["thesis"]["body"]))
    for v in SCHEMA["views"]:
        texts.append((f"{v['id']}.blurb", v["blurb"]))
        texts += [(f"{v['id']}/{g['id']}.sub", g.get("sub", "")) for g in v["groups"]]
    for f in SCHEMA["fields"]:
        if f.get("help"):
            texts.append((f"{f['key']}.help", f["help"]))
    bad = []
    for label, t in texts:
        if not t:
            continue
        if ";" in t:
            bad.append(f"schema {label}: semicolon\n    {t}")
        for pat in ANTITHESIS:
            if re.search(pat, t, re.I):
                bad.append(f"schema {label}: antithesis\n    {t}")
    assert not bad, "\n".join(bad)


# ---------------------------------------------------------------- build health

def test_page_is_self_contained():
    """index.html is the deliverable and must open from file:// with nothing beside it."""
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    bad = []
    for m in re.finditer(r"<(?:script|link|img|iframe|source)[^>]*?(?:src|href)=\"([^\"]+)\"", html):
        bad.append(m.group(1))
    assert not bad, f"external resources in the page: {bad}"
    for call in ("fetch(", "XMLHttpRequest", "new WebSocket"):
        assert call not in html, f"page calls {call} — it must work from file://"


def test_review_scaffolding_is_stripped():
    """Two pages, one template. The comment layer belongs to review.html only."""
    index = (ROOT / "index.html").read_text(encoding="utf-8")
    review = (ROOT / "review.html").read_text(encoding="utf-8")
    for marker in ('data-comment-doc="physai"', "comment-layer.js", "commentThread"):
        assert marker not in index, f"review scaffolding leaked into index.html: {marker!r}"
    assert 'data-comment-doc="physai"' in review, "review.html has no comment layer"
    for page, name in ((index, "index.html"), (review, "review.html")):
        assert "__PHYSAI_REVIEW" not in page, f"{name} has an unfilled placeholder"


def test_site_artifact_is_minimal():
    """The public site is exactly what --site writes. Everything else stays private.

    Pages deploys the artifact, not the repo tree, so this is the only thing standing
    between a new file in the repo and that file being on the internet.
    """
    with tempfile.TemporaryDirectory() as tmp:
        dest = Path(tmp) / "_site"
        built = subprocess.run(
            [sys.executable, "build.py", "--site", str(dest)],
            cwd=ROOT, capture_output=True, text=True,
        )
        assert built.returncode == 0, built.stderr
        got = sorted(str(p.relative_to(dest)) for p in dest.rglob("*") if p.is_file())
    want = sorted(["index.html", "data/schema.json"]
                  + [f"data/papers/{f.name}" for f in FILES])
    assert got == want, f"site artifact holds {got}\n  expected {want}"


def test_build_is_current():
    """Both pages are generated and neither is committed, so the only thing to
    check is that building twice from the same data gives the same bytes."""
    built = subprocess.run(
        [sys.executable, "build.py"], cwd=ROOT, capture_output=True, text=True
    )
    assert built.returncode == 0, built.stderr
    # build.py writes in place, so re-run and confirm both pages are stable
    before = {n: (ROOT / n).read_bytes() for n in ("index.html", "review.html")}
    subprocess.run([sys.executable, "build.py"], cwd=ROOT, capture_output=True, text=True)
    for n, b in before.items():
        assert (ROOT / n).read_bytes() == b, f"{n} build is not deterministic"


def test_embedded_json_parses():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    m = re.search(r'<script id="db" type="application/json">(.*?)</script>', html, re.S)
    assert m, "no embedded database in index.html"
    db = json.loads(m.group(1).replace("<\\/", "</"))
    assert len(db["papers"]) == len(PAPERS), (
        f"page has {len(db['papers'])} papers, data/ has {len(PAPERS)} — rebuild"
    )


# ------------------------------------------------------------------------ main

def main():
    checks = [(n, f) for n, f in sorted(globals().items())
              if n.startswith("test_") and callable(f)]
    failed = 0
    print(f"{len(PAPERS)} papers from {len(FILES)} files, {len(SCHEMA['fields'])} columns\n")
    for name, fn in checks:
        try:
            fn()
            print(f"  ok    {name}")
        except AssertionError as e:
            failed += 1
            print(f"  FAIL  {name}\n        " + str(e).replace("\n", "\n        "))
    print(f"\n{len(checks) - failed}/{len(checks)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
