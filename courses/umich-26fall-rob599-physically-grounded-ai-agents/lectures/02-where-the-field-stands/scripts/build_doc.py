#!/usr/bin/env python3
"""The seed for doc.ipynb: Lecture 2, written to the writing-system's shape rules.

    ~/fun/jupyter/.venv/bin/python scripts/build_doc.py            # only if doc.ipynb is absent
    ~/fun/jupyter/.venv/bin/python scripts/build_doc.py --force    # overwrite it

One block per cell, a slide type on every cell, an overview figure before any prose,
and every section opening with its own figure. This script wrote doc.ipynb once.
After that the notebook is the source of truth: every edit typed into a cell in Lab
lives only there, so this script refuses to overwrite an existing doc.ipynb unless
told to. Fold edits back in here first if you want to regenerate.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import nbformat as nbf

HERE = Path(__file__).resolve().parent.parent
CELLS: list[tuple[str, str]] = []


def md(src: str) -> None:
    CELLS.append(("markdown", src.strip("\n")))


def code(src: str) -> None:
    CELLS.append(("code", src.strip("\n")))


def flow(body: str) -> None:
    """A figure. pre.flow is styled dashed and muted; <b> marks the payload."""
    md('<pre class="flow">\n' + body.strip("\n") + "\n</pre>")


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
   'AI.</b> This is the first lecture with notes, and every lecture after it is a debate. This one '
   'puts everyone on the same page first: what the field is, why it exists, where it stands in '
   'September 2026, and how to read a paper well enough to argue about it.</p>')

flow('''
        <b>the hub</b>   awesome-physical-ai · 110 papers · 13 columns · three views
                                      │
                ┌─────────────────────┼─────────────────────┐
                ▼                     ▼                     ▼
        <b>§1 what it is</b>        <b>§2 why it matters</b>     <b>§3 where it stands</b>
        one definition,       virtual AI changes     achieved, missing, and
        three anatomies       bits. This changes     challenges concrete
                              atoms                  enough to be a paper
                                      │
                          the skill to join in
                                      │
                ┌─────────────────────┼─────────────────────┐
                ▼                     ▼                     ▼
        <b>§4 read a paper</b>       <b>§5 the debates</b>        <b>§6 keep the hub alive</b>
        PACES, laid on the    two papers, one        a row, a cell, or a
        paper's own           prompt, argue the      column. The protocol
        structure             claim                  is coming
''')

md(f'''
Two halves, three sections each. The top row is the understanding, which is what physical
AI is (§1), why the physical half of AI deserves its own field (§2), and where 110 papers
say the field stands (§3). §3 matters most, because it ends in gaps concrete enough to
become your paper. The bottom row is the skill, which is a way of reading a paper that
survives a debate (§4), the debate format (§5), and how the hub keeps growing after this
semester (§6). Everything below is in [the hub]({HUB}), and the hub is the thing to keep,
because this lecture goes stale and the hub gets edited.
''')

md('''
<div class="callout do"><span class="t">the take-home</span>
<p>By the end you should know which field to read and search, and hold enough shared
context to prepare a debate. Whether your side wins depends on your reasoning, and
reasoning is what the debates train.</p></div>
''')

# ============================================================ §1

md("## What physical AI is")

flow('''
          the physical world, objects and the changes they undergo
                    │
              sense │                                     ▲
                    ▼                                     │
        ┌─ <b>model it</b> ──────────────────────┐            │  the world is different
        │   represent ──► anticipate     │            │  now, so what has to be
        └────────────────┬───────────────┘            │  modeled has changed
                         │ decide                     │
        ┌─ <b>change it</b> ─────▼───────────────┐            │
        │   act ──► verify ──► adapt     ├────────────┘
        │   through an embodiment, a     │
        │   person wearing glasses, a    │
        │   robot, or the two together   │
        └────────────────────────────────┘
''')

md('''
Physical AI studies how the physical world gets changed in the age of AI. The phrase
usually gets read the other way round, as AI in a physical form, a robot with a language
model inside. That is one instance of it. The subject of the field is the change, and
whoever carries the change is a variable. It can be a person wearing glasses, a robot arm,
or the two together.
''')

md('''
Changing the world takes two moves. First model it, which means building a representation
faithful enough to act on. Then change it, by pushing a decision into the world through an
embodiment, the hub's word for who or what moves the atoms. Acting changes the world, which
changes what has to be modeled, so the two moves close into a loop. The hub is organized as
those two arcs, with the loop as a cross-section rather than a third section, because
closing the loop is a property of a paper and not a kind of paper. A paper that does both
carries both and appears in both.
''')

md('''
Three ways to cut the field up, and each is a column in the hub rather than a folder.
Where a paper sits on the loop, who owns the task from daily to professional, and how far
along the work is from a dataset to a survey. A column can be filtered and counted, which
is what §3 does with all three. A folder can only be browsed.
''')

md("### By stage of the loop")

md('''
<table class="k">
<thead><tr><th>stage</th><th>the question it answers</th><th>papers that live there</th></tr></thead>
<tbody>
<tr><td>sense</td><td>turn sensors into observations</td><td>SAM 2, HOT3D</td></tr>
<tr><td>represent</td><td>turn observations into a state you can act on</td><td>DINOv2, 3D Gaussian Splatting</td></tr>
<tr><td>anticipate</td><td>predict what the world does next</td><td>V-JEPA 2, Genie</td></tr>
<tr><td>decide</td><td>choose the next step or the plan</td><td>SayCan, VLaMP</td></tr>
<tr><td>act</td><td>emit the action, a motor command, an instruction, or an overlay</td><td>π₀, ShowHowTo</td></tr>
<tr><td>verify</td><td>check whether the intended change happened</td><td>PREGO, SAFE</td></tr>
<tr><td>adapt</td><td>change the policy or the model from the outcome</td><td>Every Mistake Counts, Inner Monologue</td></tr>
</tbody></table>
''')

md('''
A paper touches two or three stages as a rule, 81 of the 110 do, so the column is
multi-select. The stage names are ordinary words on purpose. A vision-language-action
model, a policy that reads a camera and an instruction and emits joint commands, is sense,
decide, act. A task assistant on glasses that watches you cook and speaks up when you skip
a step is sense, decide, act, verify.
''')

md('''
The column makes a parallel visible that citation graphs hide. Detecting that a person
skipped a step and detecting that a robot policy is failing are the same verify stage in
two embodiments, and the two literatures barely cite each other. §3 comes back to that
gap, because it is one you could fill.
''')

md("### By who owns the task, daily to professional")

code('''
import nbdoc
nbdoc.bar("data/domain_counts.csv", title="Papers by domain, daily to professional",
          note="the hub on 2026-09-07 · 110 papers · a paper can carry several",
          ylabel="papers")
''')

md('''
The domain axis decides two things at once, what a mistake costs and who owns the
knowledge. On the daily end, cooking, carrying a couch through a doorway with a friend,
assembling flat-pack furniture, the knowledge is common, the video is on the internet, and
a wrong step costs a minute. On the professional end, aircraft maintenance, surgery, a
factory line, the procedure is somebody's intellectual property, the recordings are
private, and a wrong step costs money or a life.
''')

md('''
The chart is the hub's own count and its shape is the point. 74 papers touch everyday
tasks and 6 touch clinical ones. That is the field's shape as much as this list's, and
intellectual property is the reason. A professional dataset is expensive to record and
hard to release, so the largest record of expert guidance in the hub is 50 hours. Ego-EXTRA
has a real expert guide a trainee while seeing only the trainee's first-person view. Daily
tasks are where the data is, and professional tasks are where the value is.
''')

md("### By stage of development")

code('''
import nbdoc
nbdoc.bar("data/contribution_counts.csv", title="Papers by what they contribute",
          note="the hub on 2026-09-07 · a paper can be several", ylabel="papers")
''')

md('''
A subfield grows in a fixed order. Someone records data, then someone turns the data into
a benchmark that scores a task. Methods climb the benchmark. A system puts a method in
front of a person, a user study says whether the person was helped, and a survey says what
the subfield learned. The contribution column records which of those a paper is, and a
paper can be several.
''')

md('''
The count says where the field is in that order, with 81 methods, 32 datasets, 32
benchmarks, 17 systems, 14 analyses and 2 surveys. Read it against the domain axis and the
two ends are at different stages. Daily tasks have reached systems and user studies.
Vid2Coach, Satori and AROMA are guidance systems tested on people, and the open questions
there are interface and timing. Professional tasks are still at data and benchmarks.
IndustReal, HoloAssist and Ego-EXTRA record the work, and the methods on them are still
step recognition and planning.
''')

md('''
That is the anatomy, a loop, an ownership axis and a development stage, and all three are
columns you can filter. §2 asks why the physical half of AI needs its own field at all.
''')

# ============================================================ §2

md("## Why physical AI is its own field")

flow('''
                      the state                the act                     the check
                      ─────────                ───────                     ─────────
     virtual AI       a file, a page.          emit tokens. Undo is        the return value
                      Fully readable           one keystroke               says what happened

     <b>physical AI</b>   seen through a camera    move something through      whether the world
                      on a head. Partial,      a body. Slow, and a cut     changed is a second
                      occluded, moving         does not undo               perception problem
''')

md('''
Virtual AI changes bits and physical AI changes atoms, and the difference is more than the
material. The models that changed the virtual world are being pointed at the physical one,
and the loop they run does not survive the trip unchanged. ReAct is that loop in its
cleanest form, think, act, read the observation, repeat. It sits in the hub under acting
without a body, because every embodied agent borrowed it. The body breaks the loop at
three places, and those three are what make physical AI its own field.
''')

md('''
The state is not written anywhere. A virtual agent reads the file, and a physical one sees
through a camera on a head, which is partial, occluded by the hands, and moving. Object
detectors trained on third-person photos collapse from that viewpoint. Ego-HOIBench measures
the drop and recovers part of it from the one cue that survives occlusion, the hand's own
pose.
''')

md('''
The act goes through a body with dynamics. Errors compound because a policy re-decides at
every timestep, which is why ALOHA commits to a chunk of actions at once and reaches 80 to
90% success from ten minutes of demonstrations on cheap hardware. And a cut does not undo,
so a wrong action is not a wrong token that the next token corrects.
''')

md('''
Whether the world changed is a separate perception problem. In the virtual loop the return
value says what happened. In the physical loop, seeing that the brick is on the table is
solved, at 98% detection, and knowing whether the assembly is in the right state is not, at
40% F1 for GPT-4o. LEGO Co-builder measured that gap on purpose, and it is where guidance
systems fail.
''')

md('''
The virtual loop also lacks something the physical one has, because the actuator can be a
person. 48 of the 110 papers carry a person as the embodiment, and 26 of those guide the
person, through words, an overlay, or an alert. That branch has its own channels and its
own failure modes, and it is physical AI with no robot in it.
''')

md("### Where physical AI is over-engineering")

md('''
Most of the time, words are enough. A recipe is text, and people cook from it. In the one
study that varied the visualization rather than the interaction, AR guidance made
assemblers 31% faster and made them make more errors. So the honest question is where the
physical loop earns its cost. My answer is three conditions, and the loop earns its cost
when the person cannot read the state themselves, when a mistake is expensive, or when the
timing of the help matters. Vid2Coach is the first case, with blind cooks, a state they
cannot see, and 58.5% fewer errors than their usual workflow. Satori is the third, an
assistant that decides on its own when to speak, which its authors call the hard problem.
The professional end of §1.2 is the second.
''')

md('''
<div class="callout note"><span class="t">debate 1 is this section</span>
<p>Physical AI against virtual AI. Is it needed at all, where is the boundary, and what is
the technical difference. Every claim above is there to be attacked.</p></div>
''')

md('''
That is the case for the field, and the first debate is whether it holds. §3 takes stock of
what the field has done with it.
''')

# ============================================================ §3

md("## Where the field stands")

flow('''
     <b>achieved</b>                       <b>missing</b>                        <b>challenge</b>
     ────────                       ───────                        ─────────
     sense, represent               adapt                          a guidance loop that
       solved enough to freeze        7 of 110                       learns from the last
     anticipate                     the human loop rarely            mistake
       a world model plans            closes, 14 of 48             robot failure detection
       zero-shot                    verify on the robot, 5           that borrows from
     act                            human+robot, 6                   mistake detection
       one policy, many tasks,      hours-long plans, 4            a state verifier rather
       many bodies                  tactile 2, matter 1              than an object detector
     verify                         state, beyond objects          …and four more
       mistake detection is a         98% against 40%
       subfield
''')

md('''
The three columns are the three questions in the second half of this lecture's title.
Achieved is what you can take off the shelf today. Missing is what the hub's own counts say
is thin. Challenge is missing, made concrete enough to be a paper. The counts are the hub on
2026-09-07, 110 papers, and the charts below redraw when the hub changes.
''')

md("### What you can build on today")

md('''
<table class="k wide plain">
<thead><tr><th>loop stage</th><th>off the shelf today</th><th>the papers</th></tr></thead>
<tbody>
<tr><td>sense, represent</td>
    <td>Features, object identity over time, and 3D scenes are solved well enough to freeze.
    Half the world models in the hub start from a frozen DINOv2.</td>
    <td>DINOv2, SAM 2, 3D Gaussian Splatting</td></tr>
<tr><td>anticipate</td>
    <td>A world model, a model that predicts what the world does next, learned from a million
    hours of internet video plus 62 hours of unlabeled robot video, plans real pick-and-place
    with no task-specific training. Actions can even be recovered from video that has none.</td>
    <td>V-JEPA 2, Genie, Cosmos</td></tr>
<tr><td>decide, act, on a robot</td>
    <td>One policy folds laundry, clears tables and assembles boxes across single-arm,
    dual-arm and mobile platforms. Dexterous imitation works from ten minutes of
    demonstrations on cheap hardware.</td>
    <td>π₀, OpenVLA, Diffusion Policy, ACT / ALOHA</td></tr>
<tr><td>decide, act, on a person</td>
    <td>A guidance system built from what rehabilitation therapists do cut blind cooks'
    errors by 58.5%. An assistant that decides when to speak matches a hand-run wizard.
    Step images render in the user's own kitchen.</td>
    <td>Vid2Coach, Satori, ShowHowTo</td></tr>
<tr><td>verify</td>
    <td>Mistake detection is a subfield with four datasets, an online one-class setting that
    trains on correct executions only, and a review.</td>
    <td>Assembly101, CaptainCook4D, PREGO, Mistake Analysis Review</td></tr>
<tr><td>the raw material</td>
    <td>3,670 hours of unscripted first-person life. 1,286 hours of skilled activity filmed
    from inside and outside at once, with coaches narrating. 829 hours with every finger
    joint tracked.</td>
    <td>Ego4D, Ego-Exo4D, EgoDex</td></tr>
</tbody></table>
''')

md('''
Two things to notice. Every row has a large corpus or a foundation model under it, so most
of the field's progress since 2023 is progress of scale. And the human rows are systems and
studies where the robot rows are policies. The two embodiments are at different development
stages, which §1.3 measured.
''')

md("### What the counts say is thin")

code('''
import nbdoc
nbdoc.bar("data/loop_stage_counts.csv", title="Papers per loop stage",
          note="the hub on 2026-09-07 · a paper spans several", ylabel="papers")
''')

md('''
Seven of 110 papers adapt, which means they change the policy or the model from the
outcome. Thirty-one verify. So the field can tell that something went wrong and almost
never learns from it while running. Every Mistake Counts updates its constraints as it
watches, and Inner Monologue feeds the outcome back to a planner as text. Those are the
exceptions, and they are from 2023 and 2022.
''')

code('''
import nbdoc
nbdoc.table("data/embodiment_loop.csv",
            caption="Who closes the loop, in the hub on 2026-09-07. A paper closes the loop "
                    "when it consumes the effect of its own action at run time.")
''')

md('''
The human-embodied loop rarely closes. 23 of the 30 robot papers consume the effect of their
own action at run time. 14 of the 48 human ones do. Most guidance work emits an instruction,
an image, or an overlay and stops. ShowHowTo, I²G and the AR guidance study all sit at the
act stage alone. A robot policy that never looked at the result would not get published. A
guidance system that never does is the norm.
''')

code('''
import nbdoc
nbdoc.bar("data/verify_by_embodiment.csv", title="Verify-stage papers, by who moves the atoms",
          note="31 papers verify · the hub on 2026-09-07", ylabel="papers")
''')

md('''
Verification is a human-side literature. 21 of the 31 verify papers watch a person, and 5
watch a robot. SAFE is nearly alone in asking whether a vision-language-action policy is
failing on a task it has never seen, and it answers from the policy's own internal
features. Both sides ask the same question at the same loop stage and cite different
papers.
''')

code('''
import nbdoc
nbdoc.table("data/thin_cells.csv",
            caption="The thin cells: every vocabulary value carried by fewer than a tenth "
                    "of the hub, with the newest papers in it.")
''')

md('''
Each row is a claim about the field that the hub has barely tested, and each is a place to
work.

- Human and robot together is the smallest embodiment. Carrying a couch through a doorway
  with a robot is in no paper here.
- Plans commit to minutes. P-JEPA holds a 30-minute procedure in one model, and Ego-R1
  reaches a week by retrieval rather than by modeling.
- Hardness, elasticity and friction are invisible to a camera, and two papers touch.
- One paper's output is matter. BrickGPT prunes each generated brick against gravity so a
  hand or an arm can build the result.
- 56 papers hold the state of the world in words, and eight hold mass, friction or force.
- Two surveys exist, so the field has not written down what it learned.
''')

md('''
One gap is not a count. Models recognize objects and do not know the state of the world.
LEGO Co-builder measures 98% object detection and 40% state F1. ProcObject-10K gets
plausible answers about what happened to an object with grounding below 45% IoU, so the
answers come from language priors. HD-EPIC puts Gemini Pro at 38.5% on questions grounded
in a digital twin of the kitchen. On PhyGenBench, text-to-video models fail most of 27
physical laws, and neither scale nor prompting closes the gap. The modeling arc looks
finished from the outside. These four numbers are what the change arc needs from it, and
none of them is close.
''')

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
<tr><td>A world model that obeys physics you can measure, force, mass and contact.</td>
    <td>physics parameters 8, tactile 2</td>
    <td>PhyGenBench, Force Prompting, Particle-Grid Neural Dynamics, VTV-LLM</td></tr>
<tr><td>A benchmark for guidance that scores the person's outcome on speed and on errors,
    against no guidance.</td>
    <td>13 user studies, no shared metric</td>
    <td>AR Visual Guidance, HoloAssist, Ego-EXTRA, Vid2Coach</td></tr>
</tbody></table>
''')

md('''
Each row is a debate with its two papers, and each is a semester project. The gap column is
a count from the hub, so when a row stops being thin, the hub says so first.
''')

md('''
That is where the field stands. Scale did the modeling and most of the acting, and the
second half of the loop is open. The rest of the lecture is how to take part, starting with
how to read.
''')

# ============================================================ §4

md("## How to read a paper so you can argue about it")

flow('''
     <b>PACES</b>            where it sits in the paper           what the hub records
     ─────            ──────────────────────────           ────────────────────
     Problem          the problem setting. Skip the        the function computed at inference,
                      intro, it is a long abstract         with inputs and outputs given a modality
                                                           and a shape. Training only where it differs
     Approach         the method                           one or two sentences of intuition,
                                                           then the components
     Claims           the abstract, the contributions      the tldr, which is the claim and
                      list, the last paragraph of intro    never the topic
     Evaluation       the experiments                      datasets and what was done to them,
                                                           metrics, baselines
     Substantiation   <b>your judgment</b> on whether E       the headline number, a confidence,
                      holds up C                           and why the paper earns a place
''')

md(f'''
Reading is the least systematic thing most graduate students do, and the debates will show
it. PACES is Jason's method, five questions asked of every paper in order. What Problem it
solves, what Approach it takes, what it Claims, how it Evaluates, and whether the evaluation
Substantiates the claim ([the write-up]({PACES})). The last one is a judgment rather than a
summary, and it is the one a debate is about.
''')

md('''
The five map onto the paper's own sections, minus the two that are about other papers. The
introduction is a long abstract and the related work is a map of the field, so skip both on
a first read. Come back to related work when you are mapping the field yourself, which is
what the hub does for you. What is left is the problem setting, the method, and the
experiments, and PACES is those three plus the claim and the verdict.
''')

md('''
The hub's reading protocol is PACES written into columns. Problem is the function the
paper computes at inference. Every input and output gets a modality, a tensor shape and one
line on what the content actually is, and training is written down only where it differs
from inference, because the interesting design choices hide in that difference. Approach is
one or two sentences of intuition, the claim the architecture is an argument for, then the
components. Claim is the tldr, which states the claim and never the topic. Evaluation is
the datasets and what was done to them, used as-is, re-annotated, remixed, or new, plus
metrics and baselines. Substantiation is the headline number, the confidence field, and
one line on why the paper earns a place.
''')

md("### PACES on one paper")

md('''
<table class="k narrow plain">
<thead><tr><th></th><th>PREGO, online mistake detection in procedural egocentric video (CVPR 2024)</th></tr></thead>
<tbody>
<tr><td>P</td><td>Online one-class mistake detection, which means deciding as each action
    ends whether it was a mistake. The input is the video stream up to now, with no future
    frames. The output is a flag per action. Training sees correct executions only, because
    the ways a procedure can go wrong cannot be enumerated.</td></tr>
<tr><td>A</td><td>Recognize the current action from the stream, predict from a symbolic
    model of the procedure what should come next, and flag the disagreement.</td></tr>
<tr><td>C</td><td>The first online open-set procedural mistake detector, with two benchmarks
    adapted for the setting.</td></tr>
<tr><td>E</td><td>Assembly101-O and EPIC-Tent-O, both remixes of existing datasets for the
    online setting. F1 and AUC. Baselines are supervised mistake classifiers and anomaly
    detection.</td></tr>
<tr><td>S</td><td>The "first" claim is a definition and holds by construction. The accuracy
    claim rests on two benchmarks the authors remixed and baselines they adapted, so the
    thing to check is whether the baselines saw the same causal input. The follow-up,
    TI-PREGO, reports that per-frame evaluation is hard, which is the kind of caveat this
    row exists to record.</td></tr>
</tbody></table>
''')

md('''
Notice the shape of the S row. It is a judgment of E against C, with the specific thing you
would go and check. A debate side is that row, argued out loud.
''')

md("### The other dimensions: where a paper sits")

md('''
PACES tells you whether one paper holds. It does not tell you where the paper sits among the
other 109, which is what you need to know what to read next and where a gap is. That is
what the hub's 13 topic columns are for, and together with PACES they are the
representation of a paper this course uses. Fill all of it in and the paper is a row in the
hub, which is §6.
''')

md('''
<table class="k">
<thead><tr><th>column</th><th>the question</th></tr></thead>
<tbody>
<tr><td>arc</td><td>model the world, change it, or both</td></tr>
<tr><td>loop stage</td><td>sense, represent, anticipate, decide, act, verify, adapt</td></tr>
<tr><td>closes the loop</td><td>does the system feed its own effect back as input at run time. A one-shot predictor does not, and a re-planning agent does</td></tr>
<tr><td>embodiment</td><td>who or what moves the atoms, whether nobody, a person, a robot, both, or a simulated body</td></tr>
<tr><td>human role</td><td>what the person is to the system, absent, observed, assisted, demonstrator, collaborator, or evaluator</td></tr>
<tr><td>what is modeled</td><td>object state, object change, the agent's body, interaction, scene, dynamics, procedure</td></tr>
<tr><td>representation</td><td>the form the world is held in, whether pixels, latent, 3D geometry, language, graph, program, trajectory, tokens, or physics parameters. The sharpest divider in the field</td></tr>
<tr><td>change channel</td><td>how the decision reaches the world, by words, visual guidance, motor action, a plan, an alert, or fabrication</td></tr>
<tr><td>sensing</td><td>where observations come from, a first-person camera, a third-person one, several, the robot's own, depth, gaze, a wearable, audio, touch, a simulator, or web video</td></tr>
<tr><td>regime</td><td>offline with the whole clip, streaming from the past only, or interactive with someone responding inside the loop</td></tr>
<tr><td>horizon</td><td>the time span the output commits to, a frame, seconds, minutes, or hours</td></tr>
<tr><td>domain</td><td>everyday, industrial, clinical, skill, lab or simulator, web</td></tr>
<tr><td>autonomy</td><td>acts only when asked, either side may start, or acts on its own</td></tr>
</tbody></table>
''')

md('''
PACES reads one paper, and §5 is how the class argues two.
''')

# ============================================================ §5

md("## How the debates work")

flow('''
     before          two papers, read with PACES · one question prompt per paper
                          │
     in the room     side A, the claim holds ──────┐
                                                   ├──►  what is the claim · does the evaluation
                     side B, it does not ──────────┘     substantiate it · is the method the right way
                          │
     after           the hub changes. A cell corrected, a why rewritten, a column argued
''')

md('''
The hub's shape is a set of claims about the field, two arcs and a loop, thirteen columns,
and the vocabulary inside each. The debates are the reasoning that produced those claims,
re-run in public with you in the room. Reasoning is the skill this course trains, and a
debate is the cheapest way to make reasoning visible, with two sides, one claim, and a room
that has read the same two papers.
''')

md('''
A session takes two papers. Each comes with a question prompt written for that paper. The
two sides argue three things in order, what the paper's claim actually is, whether the
evaluation substantiates it, and whether the method is the right way to get there. Those
are the C, the S and the A of PACES, which is why §4 came before this.
''')

md('''
The first debate is §2, physical AI against virtual AI. Is it needed at all, where is the
boundary, and what is the technical difference. Prepare by writing the five PACES rows for
both papers before you pick a side. A side chosen before the S row is written is a side
you cannot defend.
''')

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

md('''
> [C] on the topic table
>
> [C] **ai:** Row 1 is from your draft, with a candidate pair of papers. Rows 2 to 8 are candidates I pulled from §3's gaps and from the hub's own group blurbs, two papers each with a prompt. The syllabus decides the real list, so treat this as a menu and cut it down.
''')

md('''
The debates change the hub, and §6 is how.
''')

# ============================================================ §6

md("## Keep the hub alive together")

flow('''
     you read a paper ──► PACES + the 13 columns ──► a row ──► the counts move ──► a gap closes, or opens
                                                                       │
     a debate ends ──► a cell is wrong · a why is weak · a value has no paper ──► an edit
''')

md('''
The hub outlives the course by design. It carries no schedule, no lecture numbers, and no
assignments, so that a researcher who has never heard of ROB 599 can use it. The bet is
that with enough attention it becomes to physical AI what one vision course's reading list
became to vision a decade ago. What it needs from you is rows and arguments.
''')

md('''
- **A row.** A paper read with PACES and tagged on the 13 columns. The shape of an entry is
  in the hub's README, and every field is one or two sentences at most.
- **A cell.** A number that is not in the paper's abstract, a tldr that names the topic
  instead of the claim, or a tag that was too generous. Every correction of one of those
  is a contribution.
- **A column.** A vocabulary value with no paper in it is a claim about the field that the
  hub has not tested. Find the paper or delete the value. The build fails on an empty
  value, which is how the hub keeps itself honest.
''')

md('''
Two rules keep the database useful. Every column exists for every paper and no cell runs
past two sentences, so the table stays scannable and the detail stays in the paper.
Categories where the world is small and prose where it is rich, so a modality is a closed
vocabulary and why a method works is free text. And never write a number that is not in
the paper.
''')

md('''
> [C] on the contribution protocol
>
> [C] **ai:** The channel is yours to set: issues, email, or collaborator access to the private repo. I left it out of the prose until you decide, since the draft says the protocol will come.
''')

md('''
That is the whole lecture. The field is a loop whose second half is open, and the hub is
the map of it. PACES is how you read one paper, the debates are how the class reads two,
and the hub is what stays after the semester.
''')

# ============================================================ §7, if there is time

md("## Where this framing comes from, if there is time")

md('''
My own work sits on the human-embodiment branch, under the name ambient intelligence.
Perception is continuous and complete, and output is in-context and proactive. Three axes
place any application in it, daily to professional, digital to physical, and analytical
information to actionable instruction. Physical AI is the physical column of that space,
and the loop in §1 is what a proactive output needs, because deciding when to help is a
verify-and-decide problem over a stream.
''')

md('''
> [C] on prototypes and research
>
> [C] **ai:** The draft lists prototypes and your research under extend, and names nothing else. I did not write them in rather than guess. Two cells here, one per pointer, would do it.
''')


if __name__ == "__main__":
    build(force="--force" in sys.argv[1:])
