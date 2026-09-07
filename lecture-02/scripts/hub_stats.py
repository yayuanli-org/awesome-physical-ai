#!/usr/bin/env python3
"""Count the paper hub into the CSVs the lecture's cells draw.

    python3 scripts/hub_stats.py

Reads paper-hub/data/schema.json and paper-hub/data/papers/*.json, found by walking
up from this file until a folder holding paper-hub/ appears, so the lecture folder
can move anywhere inside the repo. Writes data/*.csv. Stdlib only.

Every number in the lecture's charts comes from here, so re-run it after the hub
changes and re-run the cells. The prose carries the counts as of the date it was
written, and the charts carry the counts as of the last run.
"""
from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "data"


def find_hub() -> Path:
    for parent in HERE.parents:
        hub = parent / "paper-hub" / "data"
        if (hub / "papers").is_dir() and (hub / "schema.json").exists():
            return hub
    sys.exit("hub_stats: no paper-hub/data/ above " + str(HERE))


def load(hub: Path):
    schema = json.loads((hub / "schema.json").read_text(encoding="utf-8"))
    papers = []
    for f in sorted((hub / "papers").glob("*.json")):
        papers.extend(json.loads(f.read_text(encoding="utf-8")))
    return schema, papers


def labels_for(schema, key: str) -> dict[str, str]:
    for field in schema["fields"]:
        if field["key"] == key:
            return {v["v"]: v.get("label", v["v"]) for v in field.get("vocab", [])}
    return {}


def count(papers, key: str) -> Counter:
    c: Counter = Counter()
    for p in papers:
        v = p.get(key)
        if isinstance(v, list):
            c.update(v)
        elif v is not None:
            c[v] += 1
    return c


def write(name: str, header: list[str], rows: list[list]) -> None:
    OUT.mkdir(exist_ok=True)
    with (OUT / name).open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"  data/{name}  {len(rows)} rows")


def examples(papers, key: str, value: str, n: int = 3) -> str:
    hits = [p for p in papers if value in (p.get(key) or [])]
    hits.sort(key=lambda p: p.get("date", ""), reverse=True)
    return ", ".join(p.get("short") or p["title"] for p in hits[:n])


def main() -> None:
    hub = find_hub()
    schema, papers = load(hub)
    n = len(papers)
    print(f"hub_stats: {n} papers in {hub}")

    # --- loop stage, in loop order ------------------------------------------
    lab = labels_for(schema, "loop_stage")
    c = count(papers, "loop_stage")
    write("loop_stage_counts.csv", ["label", "value"],
          [[lab[v].lower(), c[v]] for v in lab])

    # --- domain, daily to professional, then the two non-domains ----------------
    lab = labels_for(schema, "domain")
    c = count(papers, "domain")
    order = ["everyday", "skill", "industrial", "clinical", "lab-sim", "web"]
    write("domain_counts.csv", ["label", "value"],
          [[lab[v].lower(), c[v]] for v in order if v in lab])

    # --- contribution, in development order ------------------------------------
    lab = labels_for(schema, "contribution")
    c = count(papers, "contribution")
    order = ["dataset", "benchmark", "method", "system", "analysis", "survey"]
    write("contribution_counts.csv", ["label", "value"],
          [[lab[v].lower(), c[v]] for v in order if v in lab])

    # --- who closes the loop ----------------------------------------------------
    lab = labels_for(schema, "embodiment")
    tot, closed = Counter(), Counter()
    for p in papers:
        for e in p.get("embodiment") or []:
            tot[e] += 1
            if p.get("closes_loop"):
                closed[e] += 1
    order = ["human", "robot", "human+robot", "none", "sim"]
    write("embodiment_loop.csv", ["embodiment", "papers", "close the loop", "%"],
          [[lab[e], tot[e], closed[e], round(100 * closed[e] / tot[e]) if tot[e] else 0]
           for e in order if e in lab])

    # --- verify-stage papers by embodiment ----------------------------------------
    c = Counter()
    for p in papers:
        if "verify" in (p.get("loop_stage") or []):
            c.update(p.get("embodiment") or [])
    write("verify_by_embodiment.csv", ["label", "value"],
          [[lab[e].lower(), c[e]] for e in order if e in lab])

    # --- the thin cells: every value below a tenth of the hub --------------------
    thin = [
        ("loop_stage", "adapt"), ("embodiment", "human+robot"), ("horizon", "hours"),
        ("sensing", "tactile"), ("change_channel", "fabrication"), ("domain", "clinical"),
        ("domain", "skill"), ("contribution", "survey"), ("representation", "physics-params"),
        ("autonomy", "mixed-initiative"),
    ]
    rows = []
    for key, value in thin:
        lab_k = next(f["label"] for f in schema["fields"] if f["key"] == key)
        lab_v = labels_for(schema, key).get(value, value)
        rows.append([lab_k.lower(), lab_v.lower(), count(papers, key)[value],
                     examples(papers, key, value)])
    write("thin_cells.csv", ["axis", "value", "papers", "examples"], rows)

    # --- one line of totals, for the prose to check itself against ----------------
    arcs = count(papers, "arc")
    both = sum(1 for p in papers if set(p.get("arc") or []) == {"model", "change"})
    print(f"  arcs: model {arcs['model']}, change {arcs['change']}, both {both}; "
          f"closes the loop: {sum(1 for p in papers if p.get('closes_loop'))}")


if __name__ == "__main__":
    main()
