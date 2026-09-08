#!/usr/bin/env python3
"""The seed for doc.ipynb: Lecture 2, written as a presentation.

    ~/fun/jupyter/.venv/bin/python scripts/build_doc.py            # only if doc.ipynb is absent
    ~/fun/jupyter/.venv/bin/python scripts/build_doc.py --force    # overwrite it

The unit is a slide: one figure or table, then two to four bullets that carry its
point, then a box that repeats the lecture's map with what is done in ink and the
rest greyed out. Every cell is one block with a slide type on it, so the same file
reads as a page in Lab and presents as a deck.

This script wrote doc.ipynb once. After that the notebook is the source of truth:
every edit typed into a cell in Lab lives only there, so this script refuses to
overwrite an existing doc.ipynb unless told to. Fold edits back in here first if you
want to regenerate.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import nbformat as nbf

sys.path.insert(0, str(Path(__file__).resolve().parent))
from debate1_cells import debate1  # noqa: E402  the Debate 1 brief that closes §5

HERE = Path(__file__).resolve().parent.parent
CELLS: list[tuple[str, str]] = []


def md(src: str) -> None:
    CELLS.append(("markdown", src.strip("\n")))


def code(src: str) -> None:
    CELLS.append(("code", src.strip("\n")))


def flow(body: str, bold: tuple[str, ...] = ()) -> None:
    """A figure. Draw it plain so the columns line up as written; `bold` names the
    words to set in ink, and they are wrapped after the fact so the tags never
    shift a column."""
    body = body.strip("\n")
    for w in bold:
        body = body.replace(w, f"<b>{w}</b>")
    md('<pre class="flow">\n' + body + "\n</pre>")


def bullets(*items: str) -> None:
    """Two to four points under a figure, one claim each. One cell, so the deck
    reveals them together."""
    assert 1 <= len(items) <= 4, f"{len(items)} bullets: the rule is two to four"
    md("\n".join("- " + " ".join(i.split()) for i in items))


# ------------------------------------------------------------------ the map
# The lecture's table of contents, drawn once at the top and again after every
# unit with what is done in ink and the rest greyed out. Unit names are the
# labels in the boxes, so keep them short; a section that runs past the column
# wraps onto a second line.
MAP = [
    ("understand the field", [
        ("§1", "what it is",         ["the loop", "seven stages", "who owns the task", "how far along"]),
        ("§2", "why its own field",  ["three breaks", "when words are enough"]),
        ("§3", "where it stands",    ["overview", "achieved", "adapt", "who closes",
                                      "verify", "thin cells", "state", "challenges"]),
    ]),
    ("join the conversation", [
        ("§4", "read a paper",       ["PACES", "on one paper", "the 13 columns"]),
        ("§5", "the debates",        ["the format", "eight topics", "debate 1",
                                      "reading", "recap", "prompts"]),
        ("§6", "keep the hub alive", ["a row, a cell, a column"]),
    ]),
]
UNITS = [u for _, secs in MAP for _, _, us in secs for u in us]
LABEL_W = 22          # `§6 keep the hub alive` is 21
INDENT = "  "
LINE_W = 96           # a pre.flow line past ~100 characters scrolls instead of wrapping


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


def overview() -> None:
    md(render_map(None))


def box(done_through: str) -> None:
    assert done_through in UNITS, done_through
    md(render_map(done_through))


def slide_type(cell_type: str, src: str) -> str:
    if cell_type == "markdown":
        if re.match(r"^\s*(#\s|<h1)", src):
            return "slide"
        if re.match(r"^\s*(##\s|<h2)", src):
            return "slide"
        if re.match(r"^\s*(###\s|<h3)", src):
            return "subslide"
    return "fragment"


def build(force: bool) -> None:
    out = HERE / "doc.ipynb"
    if out.exists() and not force:
        sys.exit(f"{out.name} exists and holds hand edits. Re-run with --force to overwrite it.")
    nb = nbf.v4.new_notebook()
    nb.metadata.update({
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"},
        "nbdoc": {"doc_id": "rob599-lecture-02",
                  "title": "ROB 599 · Lecture 2 · Physical AI: where the field stands"},
    })
    for i, (kind, src) in enumerate(CELLS):
        cell = nbf.v4.new_markdown_cell(src) if kind == "markdown" else nbf.v4.new_code_cell(src)
        cell.metadata["slideshow"] = {"slide_type": slide_type(kind, src)}
        cell["id"] = f"c{i:03d}"
        nb.cells.append(cell)
    nbf.write(nb, str(out))
    print(f"{out.name}: {len(nb.cells)} cells")


HUB = "https://yayuanli-org.github.io/awesome-physical-ai/"
PACES = "https://medium.com/@jasoncorso/how-to-read-conference-papers-fa78c75f78aa"

# ============================================================ title and overview

md('<h1><span class="kicker">ROB 599 · Lecture 2 · Fall 2026</span>'
   'Physical AI: where the field stands, and how to join the conversation</h1>')

md('<p class="lede"><b>Physical AI studies how the physical world gets changed in the age of '
   'AI.</b> This lecture puts everyone on the same page: what the field is, where it stands in '
   'September 2026, and how to read a paper well enough to argue about it.</p>')

overview()

bullets(
    "The top half is the field. §3 ends in gaps concrete enough to be your paper.",
    "The bottom half is the skill. Read one paper, argue two, and keep the hub growing after "
    "the semester.",
    f"Everything here is in [the hub]({HUB}). This lecture goes stale, and the hub gets edited.",
    "Leave knowing which field to read and search, with enough shared context to prepare a "
    "debate.",
)

# ============================================================ §1

md("## What physical AI is")

flow('''
          the physical world, objects and the changes they undergo
                    │
              sense │                                       ▲
                    ▼                                       │
        ┌─ model it ───────────────────────┐                │  acting changes the world,
        │   represent ──► anticipate       │                │  so what has to be modeled
        └────────────────┬─────────────────┘                │  changes too
                         │ decide                           │
        ┌─ change it ────▼──────────────────┐               │
        │   act ──► verify ──► adapt        ├───────────────┘
        │   through an embodiment: a        │
        │   person wearing glasses, a       │
        │   robot, or the two together      │
        └───────────────────────────────────┘
''', bold=("model it", "change it"))

bullets(
    "The subject is the change. Who carries it is a variable: a person wearing glasses, a "
    "robot, or both.",
    "Model the world, then change it through an embodiment, the hub's word for who or what "
    "moves the atoms. Acting changes what has to be modeled, so the two close into a loop.",
    "Three columns cut the field: stage of the loop, who owns the task, how far along. A "
    "column can be counted, which §3 does.",
)

box("the loop")

md("### The seven stages of the loop")

md('''
<table class="k">
<thead><tr><th>stage</th><th>the question it answers</th><th>papers that live there</th></tr></thead>
<tbody>
<tr><td>sense</td><td>turn sensors into observations</td><td>SAM 2, HOT3D</td></tr>
<tr><td>represent</td><td>turn observations into a state you can act on</td><td>DINOv2, 3D Gaussian Splatting</td></tr>
<tr><td>anticipate</td><td>predict what the world does next</td><td>V-JEPA 2, Genie</td></tr>
<tr><td>decide</td><td>choose the next step or the plan</td><td>SayCan, VLaMP</td></tr>
<tr><td>act</td><td>emit the action: a motor command, an instruction, an overlay</td><td>π₀, ShowHowTo</td></tr>
<tr><td>verify</td><td>check whether the intended change happened</td><td>PREGO, SAFE</td></tr>
<tr><td>adapt</td><td>change the policy or the model from the outcome</td><td>Every Mistake Counts, Inner Monologue</td></tr>
</tbody></table>
''')

bullets(
    "A paper touches two or three stages as a rule. 81 of the 110 do.",
    "A vision-language-action policy (camera and instruction in, joint commands out) is "
    "sense, decide, act. A task assistant on glasses is sense, decide, act, verify.",
    "A person skipping a step and a robot policy failing are the same verify stage, and the "
    "two literatures barely cite each other.",
)

box("seven stages")

md("### Who owns the task, daily to professional")

code('''
import nbdoc
nbdoc.bar("data/domain_counts.csv", title="Papers by domain, daily to professional",
          note="the hub on 2026-09-07 · 110 papers · a paper can carry several",
          ylabel="papers")
''')

bullets(
    "The axis sets what a mistake costs and who owns the knowledge. A wrong step in cooking "
    "costs a minute, in surgery a life.",
    "74 papers touch everyday tasks and 6 touch clinical ones. Intellectual property is the "
    "reason, and the largest record of expert guidance here is 50 hours.",
    "Daily tasks are where the data is. Professional tasks are where the value is.",
)

box("who owns the task")

md("### How far along the work is")

code('''
import nbdoc
nbdoc.bar("data/contribution_counts.csv", title="Papers by what they contribute",
          note="the hub on 2026-09-07 · a paper can be several", ylabel="papers")
''')

bullets(
    "A subfield grows in a fixed order: data, benchmark, method, system, user study, survey.",
    "81 methods, 32 datasets, 32 benchmarks, 17 systems, 14 analyses, 2 surveys.",
    "Daily tasks have reached systems tested on people (Vid2Coach, Satori, AROMA). "
    "Professional tasks are still at data and benchmarks (IndustReal, HoloAssist, Ego-EXTRA).",
)

box("how far along")

# ============================================================ §2

md("## Why physical AI is its own field")

flow('''
                  the state                 the act                     the check
                  ─────────                 ───────                     ─────────
   virtual AI     a file, a page.           emit tokens. Undo is        the return value
                  fully readable            one keystroke               says what happened

   physical AI    seen through a camera     move something through      whether the world
                  on a head. Partial,       a body. Slow, and a cut     changed is a second
                  occluded, moving          does not undo               perception problem
''', bold=("physical AI",))

bullets(
    "The loop that changed the virtual world, think, act, read the result, repeat (ReAct), "
    "breaks in three places once it has a body.",
    "The state is not written anywhere. A camera on a head is partial, occluded and moving, "
    "and third-person detectors collapse from it (Ego-HOIBench).",
    "The act does not undo, and errors compound at every step. ALOHA commits to a chunk of "
    "actions at once and reaches 80 to 90% from ten minutes of demonstrations.",
    "The check is a second perception problem. The brick is seen at 98%, the state of the "
    "assembly at 40% F1 (LEGO Co-builder).",
)

box("three breaks")

md("### When words are enough")

md('''
<table class="k wide plain">
<thead><tr><th>the situation</th><th>words are enough?</th><th>the evidence</th></tr></thead>
<tbody>
<tr><td>the person can read the state, and a mistake is cheap</td>
    <td>yes</td>
    <td>a recipe is text, and people cook from it. AR guidance made assemblers 31% faster and
    made them make more errors</td></tr>
<tr><td>the person cannot read the state</td>
    <td>no</td>
    <td>Vid2Coach, blind cooks: 58.5% fewer errors than their usual workflow</td></tr>
<tr><td>a mistake is expensive</td>
    <td>no</td>
    <td>the professional end of §1: a wrong step costs money or a life</td></tr>
<tr><td>the timing of the help matters</td>
    <td>no</td>
    <td>Satori decides on its own when to speak, which its authors call the hard problem</td></tr>
</tbody></table>
''')

bullets(
    "The actuator can be a person. 48 of the 110 papers carry one and 26 guide them, which is "
    "physical AI with no robot in it.",
    "Most of the time, words are enough. The loop earns its cost when the person cannot read "
    "the state, a mistake is expensive, or the timing matters.",
    "Debate 1 attacks every claim in this section. The brief is in §5.",
)

box("when words are enough")

# ============================================================ §3

md("## Where the field stands")

flow('''
   achieved                         missing                          challenge
   ────────                         ───────                          ─────────
   sense, represent: solved         adapt: 7 of 110                  a guidance loop that
     enough to freeze               the human loop rarely              learns from the last
   anticipate: a world model          closes: 14 of 48                 mistake
     plans zero-shot                verify on the robot: 5           robot failure detection
   act: one policy, many            human+robot: 6                     that borrows from
     tasks, many bodies             hours-long plans: 4                mistake detection
   verify: mistake detection        tactile 2, matter 1              a state verifier rather
     is a subfield                  state beyond objects:              than an object detector
                                      98% against 40%                …and four more
''', bold=("achieved", "missing", "challenge"))

bullets(
    "Achieved is what you can take off the shelf. Missing is what the hub's counts say is "
    "thin. Challenge is missing, made concrete enough to be a paper.",
    "The counts are the hub on 2026-09-07, 110 papers. The charts redraw when the hub changes.",
    "Scale did the modeling and most of the acting. The second half of the loop is open.",
)

box("overview")

md("### What you can build on today")

md('''
<table class="k wide plain">
<thead><tr><th>loop stage</th><th>off the shelf today</th><th>the papers</th></tr></thead>
<tbody>
<tr><td>sense, represent</td>
    <td>Features, object identity over time and 3D scenes are solved well enough to freeze.
    Half the world models in the hub start from a frozen DINOv2.</td>
    <td>DINOv2, SAM 2, 3D Gaussian Splatting</td></tr>
<tr><td>anticipate</td>
    <td>A world model, a model that predicts what the world does next, learned from a million
    hours of internet video plus 62 hours of unlabeled robot video, plans real pick-and-place
    with no task-specific training.</td>
    <td>V-JEPA 2, Genie, Cosmos</td></tr>
<tr><td>decide, act, on a robot</td>
    <td>One policy folds laundry, clears tables and assembles boxes across single-arm,
    dual-arm and mobile platforms. Dexterous imitation works from ten minutes of
    demonstrations on cheap hardware.</td>
    <td>π₀, OpenVLA, Diffusion Policy, ACT / ALOHA</td></tr>
<tr><td>decide, act, on a person</td>
    <td>A guidance system built from what rehabilitation therapists do cut blind cooks' errors
    by 58.5%. An assistant that decides when to speak matches a hand-run wizard.</td>
    <td>Vid2Coach, Satori, ShowHowTo</td></tr>
<tr><td>verify</td>
    <td>Mistake detection is a subfield: four datasets, an online one-class setting that
    trains on correct executions only, and a review.</td>
    <td>Assembly101, CaptainCook4D, PREGO, Mistake Analysis Review</td></tr>
<tr><td>the raw material</td>
    <td>3,670 hours of unscripted first-person life. 1,286 hours of skilled activity filmed
    from inside and outside at once. 829 hours with every finger joint tracked.</td>
    <td>Ego4D, Ego-Exo4D, EgoDex</td></tr>
</tbody></table>
''')

bullets(
    "Every row has a large corpus or a foundation model under it. Progress since 2023 is "
    "progress of scale.",
    "The human rows are systems and studies, and the robot rows are policies. The two "
    "embodiments are at different stages.",
)

box("achieved")

md("### Seven papers adapt")

code('''
import nbdoc
nbdoc.bar("data/loop_stage_counts.csv", title="Papers per loop stage",
          note="the hub on 2026-09-07 · a paper spans several", ylabel="papers")
''')

bullets(
    "7 of 110 papers adapt, meaning they change the policy or the model from the outcome. "
    "31 verify.",
    "The field can tell that something went wrong, and almost never learns from it while "
    "running.",
    "The exceptions are from 2023 and 2022. Every Mistake Counts updates its constraints as "
    "it watches, and Inner Monologue feeds the outcome back as text.",
)

box("adapt")

md("### The human loop rarely closes")

code('''
import nbdoc
nbdoc.table("data/embodiment_loop.csv",
            caption="Who closes the loop, in the hub on 2026-09-07. A paper closes the loop "
                    "when it consumes the effect of its own action at run time.")
''')

bullets(
    "23 of the 30 robot papers consume the effect of their own action. 14 of the 48 human "
    "ones do.",
    "Most guidance work emits an instruction, an image, or an overlay and stops (ShowHowTo, "
    "I²G, the AR guidance study).",
    "A robot policy that never looked at the result would not get published. A guidance "
    "system that never does is the norm.",
)

box("who closes")

md("### Verification is a human-side literature")

code('''
import nbdoc
nbdoc.bar("data/verify_by_embodiment.csv", title="Verify-stage papers, by who moves the atoms",
          note="31 papers verify · the hub on 2026-09-07", ylabel="papers")
''')

bullets(
    "21 of the 31 verify papers watch a person. 5 watch a robot.",
    "SAFE is nearly alone in asking whether a policy is failing on an unseen task, and it "
    "answers from the policy's own internal features.",
    "Both sides ask the same question at the same loop stage and cite different papers.",
)

box("verify")

md("### The thin cells")

code('''
import nbdoc
nbdoc.table("data/thin_cells.csv",
            caption="Every vocabulary value carried by fewer than a tenth of the hub, "
                    "with the newest papers in it.")
''')

bullets(
    "Each row is a claim about the field that the hub has barely tested, and a place to work.",
    "Human and robot together is the smallest embodiment, 6 papers. Carrying a couch through a "
    "doorway with a robot is in no paper here.",
    "Plans commit to minutes. P-JEPA holds 30, and Ego-R1 reaches a week by retrieval.",
    "56 papers hold the state of the world in words, and eight hold mass, friction or force.",
)

box("thin cells")

md("### Models know objects, not state")

md('''
<table class="k wide plain">
<thead><tr><th>benchmark</th><th>the question</th><th>the number</th></tr></thead>
<tbody>
<tr><td>LEGO Co-builder</td>
    <td>is the brick there, against is the assembly in the right state</td>
    <td>98% object detection, 40% state F1 (GPT-4o)</td></tr>
<tr><td>ProcObject-10K</td>
    <td>what happened to this object</td>
    <td>plausible answers with grounding below 45% IoU, so they come from language priors</td></tr>
<tr><td>HD-EPIC</td>
    <td>questions grounded in a digital twin of the kitchen</td>
    <td>Gemini Pro 38.5%</td></tr>
<tr><td>PhyGenBench</td>
    <td>does generated video obey 27 physical laws</td>
    <td>text-to-video models fail most of them, and neither scale nor prompting closes the gap</td></tr>
</tbody></table>
''')

bullets(
    "Models recognize objects and do not know the state of the world. Where the answers look "
    "right, they come from language priors.",
    "The modeling arc looks finished from the outside. These four numbers are what the change "
    "arc needs from it, and none is close.",
)

box("state")

md("### Challenges concrete enough to be a paper")

md('''
<table class="k wide plain">
<thead><tr><th>the challenge</th><th>the gap it fills</th><th>start from</th></tr></thead>
<tbody>
<tr><td>A guidance loop that adapts. Watch what the person did with the last instruction
    and change the next one.</td>
    <td>verify without adapt, 31 papers against 7</td>
    <td>Every Mistake Counts, Vid2Coach, Satori, Inner Monologue</td></tr>
<tr><td>Failure detection for a robot policy, borrowed from mistake detection, and the
    other way round.</td>
    <td>verify, 21 on a person and 5 on a robot</td>
    <td>SAFE, PREGO, Action Effect Modeling, IndustReal</td></tr>
<tr><td>A state verifier rather than an object detector. Score the outcome of a step
    rather than the gesture.</td>
    <td>98% on objects, 40% on state</td>
    <td>LEGO Co-builder, IndustReal, ProcObject-10K, Action Effect Modeling</td></tr>
<tr><td>A person and a robot carry one object through a door.</td>
    <td>human and robot together, 6 papers</td>
    <td>TWIST, Spot-On, Trajectory2Pose, DexUMI</td></tr>
<tr><td>A professional procedure learned from one demonstration, because professional data
    will stay scarce.</td>
    <td>clinical 6, industrial 21, everyday 74</td>
    <td>MICA, Ego-EXTRA, HowToDIV, Neural Task Graphs</td></tr>
<tr><td>A world model that obeys physics you can measure: force, mass and contact.</td>
    <td>physics parameters 8, tactile 2</td>
    <td>PhyGenBench, Force Prompting, Particle-Grid Neural Dynamics, VTV-LLM</td></tr>
<tr><td>A benchmark for guidance that scores the person's outcome on speed and on errors,
    against no guidance.</td>
    <td>13 user studies, no shared metric</td>
    <td>AR Visual Guidance, HoloAssist, Ego-EXTRA, Vid2Coach</td></tr>
</tbody></table>
''')

bullets(
    "Each row is a debate with its two papers, and a semester project.",
    "The gap column is a count from the hub. When a row stops being thin, the hub says so first.",
)

box("challenges")

# ============================================================ §4

md("## How to read a paper so you can argue about it")

flow('''
   PACES            where it sits in the paper           what the hub records
   ─────            ──────────────────────────           ────────────────────
   Problem          the problem setting. Skip the        the function computed at inference:
                    intro, it is a long abstract         inputs and outputs, each with a
                                                         modality and a shape
   Approach         the method                           one or two sentences of intuition,
                                                         then the components
   Claims           the abstract, the contributions      the tldr: the claim, never the topic
                    list, the last paragraph of intro
   Evaluation       the experiments                      datasets and what was done to them,
                                                         metrics, baselines
   Substantiation   your judgment on whether E           the headline number, a confidence,
                    holds up C                           and why the paper earns a place
''', bold=("PACES", "your judgment"))

bullets(
    "Reading is the least systematic thing most graduate students do, and the debates will "
    "show it.",
    f"PACES is Jason's method: Problem, Approach, Claims, Evaluation, Substantiation, asked of "
    f"every paper in that order ([the write-up]({PACES})).",
    "Skip the introduction and the related work on a first read. What is left is the problem, "
    "the method and the experiments, plus the claim and the verdict.",
    "S is a judgment, and it is what a debate is about. The hub's reading protocol is PACES "
    "written into columns.",
)

box("PACES")

md("### PACES on one paper")

md('''
<table class="k narrow plain">
<thead><tr><th></th><th>PREGO, online mistake detection in procedural egocentric video (CVPR 2024)</th></tr></thead>
<tbody>
<tr><td>P</td><td>Online one-class mistake detection: decide, as each action ends, whether it
    was a mistake. Input is the video stream up to now. Output is a flag per action. Training
    sees correct executions only, because the ways a procedure can go wrong cannot be
    enumerated.</td></tr>
<tr><td>A</td><td>Recognize the current action from the stream, predict from a symbolic model
    of the procedure what should come next, and flag the disagreement.</td></tr>
<tr><td>C</td><td>The first online open-set procedural mistake detector, with two benchmarks
    adapted for the setting.</td></tr>
<tr><td>E</td><td>Assembly101-O and EPIC-Tent-O, remixes of existing datasets for the online
    setting. F1 and AUC. Baselines: supervised mistake classifiers and anomaly detection.</td></tr>
<tr><td>S</td><td>The "first" claim is a definition and holds by construction. The accuracy
    claim rests on two benchmarks the authors remixed and baselines they adapted, so check
    whether the baselines saw the same causal input. The follow-up, TI-PREGO, reports that
    per-frame evaluation is hard.</td></tr>
</tbody></table>
''')

bullets(
    "The S row judges E against C and names the thing you would go and check.",
    "A debate side is that row, argued out loud.",
)

box("on one paper")

md("### The 13 columns: where a paper sits")

md('''
<table class="k">
<thead><tr><th>column</th><th>the question</th></tr></thead>
<tbody>
<tr><td>arc</td><td>model the world, change it, or both</td></tr>
<tr><td>loop stage</td><td>sense, represent, anticipate, decide, act, verify, adapt</td></tr>
<tr><td>closes the loop</td><td>does the system feed its own effect back as input at run time. A one-shot predictor does not, a re-planning agent does</td></tr>
<tr><td>embodiment</td><td>who or what moves the atoms: nobody, a person, a robot, both, or a simulated body</td></tr>
<tr><td>human role</td><td>what the person is to the system: absent, observed, assisted, demonstrator, collaborator, or evaluator</td></tr>
<tr><td>what is modeled</td><td>object state, object change, the agent's body, interaction, scene, dynamics, procedure</td></tr>
<tr><td>representation</td><td>the form the world is held in: pixels, latent, 3D geometry, language, graph, program, trajectory, tokens, or physics parameters. The sharpest divider in the field</td></tr>
<tr><td>change channel</td><td>how the decision reaches the world: words, visual guidance, motor action, a plan, an alert, or fabrication</td></tr>
<tr><td>sensing</td><td>where observations come from: a first-person camera, a third-person one, several, the robot's own, depth, gaze, a wearable, audio, touch, a simulator, or web video</td></tr>
<tr><td>regime</td><td>offline with the whole clip, streaming from the past only, or interactive with someone responding inside the loop</td></tr>
<tr><td>horizon</td><td>the time span the output commits to: a frame, seconds, minutes, or hours</td></tr>
<tr><td>domain</td><td>everyday, industrial, clinical, skill, lab or simulator, web</td></tr>
<tr><td>autonomy</td><td>acts only when asked, either side may start, or acts on its own</td></tr>
</tbody></table>
''')

bullets(
    "PACES says whether one paper holds. The 13 columns say where it sits among the other "
    "109, which is what tells you what to read next.",
    "PACES plus the 13 columns is the representation of a paper this course uses.",
    "Fill all of it in and the paper is a row in the hub, which is §6.",
)

box("the 13 columns")

# ============================================================ §5

md("## How the debates work")

flow('''
   before          two papers, read with PACES · one question prompt per paper
                        │
   in the room     side A, the claim holds ─────┐
                                                ├──►  what is the claim · does the evaluation
                   side B, it does not ─────────┘     substantiate it · is the method right
                        │
   after           the hub changes: a cell corrected, a why rewritten, a column argued
''')

bullets(
    "The debates re-run, in public, the reasoning that produced the hub's claims. Reasoning "
    "is the skill this course trains.",
    "Two papers, one prompt each. The sides argue the claim, its substantiation, and the "
    "method, which is C, S and A of PACES.",
    "Write the five PACES rows for both papers before you pick a side.",
    "The first debate is §2, physical AI against virtual AI. Its brief closes this section.",
)

box("the format")

md("### Eight candidate debates")

md('''
<table class="k wide plain">
<thead><tr><th>topic</th><th>two papers</th><th>the prompt</th></tr></thead>
<tbody>
<tr><td>1. Physical AI against virtual AI</td>
    <td>ReAct, Inner Monologue</td>
    <td>Is the physical loop a different problem, or the same loop with worse sensors and a
    slower actuator?</td></tr>
<tr><td>2. What form should a world model hold the world in</td>
    <td>V-JEPA 2, PointWorld</td>
    <td>Latent features or 3D geometry, which one is the coordinate system that pools data
    across bodies?</td></tr>
<tr><td>3. Human video as robot data</td>
    <td>EgoVLA, DexUMI</td>
    <td>Learn the embodiment gap, or remove it with hardware and inpainting?</td></tr>
<tr><td>4. Is robot failure detection the same problem as human mistake detection</td>
    <td>SAFE, PREGO</td>
    <td>Same loop stage in a different embodiment, so does either method survive the
    swap?</td></tr>
<tr><td>5. Score the outcome, or the action</td>
    <td>IndustReal, Action Effect Modeling</td>
    <td>A normal-looking motion with a wrong result. Which representation catches it, and
    at what cost in labels?</td></tr>
<tr><td>6. Does a video generator have physics, or only appearance</td>
    <td>Force Prompting, PhyGenBench</td>
    <td>One paper says a force field is enough to reveal the physics inside. The other says
    scaling does not add any.</td></tr>
<tr><td>7. Is faster guidance better guidance</td>
    <td>AR Visual Guidance, Vid2Coach</td>
    <td>One study measures more errors with guidance, one measures 58.5% fewer. What
    differs, and which metric should a guidance paper be held to?</td></tr>
<tr><td>8. Does a task assistant have to learn from the person</td>
    <td>Every Mistake Counts, Satori</td>
    <td>Update the constraints while watching, or model the user's beliefs and intentions
    up front?</td></tr>
</tbody></table>
''')

bullets(
    "Row 1 is set. Rows 2 to 8 come from §3's gaps, and the syllabus decides.",
    "Each prompt is a question the two papers answer differently, so a side can be argued "
    "from numbers.",
)

md('''
> [C] on the topic table
>
> [C] **ai:** Rows 2 to 8 are candidates from §3's gaps and the hub's group blurbs, two papers and a prompt each. The syllabus decides, so treat this as a menu.
''')

box("eight topics")

debate1(md, flow, bullets, box)

# ============================================================ §6

md("## Keep the hub alive together")

flow('''
   read a paper ──► PACES + 13 columns ──► a row ──► the counts move ──► a gap closes or opens
                                                            │
   a debate ends ──► a wrong cell · a weak why · a value with no paper ──► an edit
''')

bullets(
    "The hub outlives the course by design, with no schedule, lecture numbers or assignments "
    "in it. What it needs from you is rows and arguments.",
    "A row is a paper read with PACES and tagged on the 13 columns. No cell runs past two "
    "sentences, and no number comes from outside the paper.",
    "A cell is a wrong number, a tldr that names the topic instead of the claim, or a tag "
    "too generous. Every correction counts.",
    "A column is a vocabulary value with no paper in it. Find the paper or delete the value, "
    "because the build fails on an empty one.",
)

md('''
> [C] on the contribution protocol
>
> [C] **ai:** The channel is yours to set: issues, email, or collaborator access to the private repo. Left out of the prose until you decide.
''')

box("a row, a cell, a column")

md('''
That is the whole lecture. The field is a loop whose second half is open, and the hub is
the map of it. PACES reads one paper, the debates read two, and the hub is what stays
after the semester.
''')

# ============================================================ §7, if there is time

md("## Where this framing comes from, if there is time")

flow('''
   daily ──────────────────── professional        who owns the task
   digital ────────────────── physical            physical AI is this column
   information ────────────── instruction         analytical to actionable
''', bold=("physical AI is this column",))

bullets(
    "My own work sits on the human-embodiment branch, under the name ambient intelligence: "
    "perception continuous and complete, output in-context and proactive.",
    "Physical AI is the physical column of that space. Deciding when to help is a "
    "verify-and-decide problem over a stream, which is the loop in §1.",
)

md('''
> [C] on prototypes and research
>
> [C] **ai:** The draft lists prototypes and your research under extend, and names nothing else. Two cells here, one per pointer, would do it.
''')


if __name__ == "__main__":
    build(force="--force" in sys.argv[1:])
