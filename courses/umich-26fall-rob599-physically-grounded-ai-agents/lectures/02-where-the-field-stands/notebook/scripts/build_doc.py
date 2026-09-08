#!/usr/bin/env python3
"""The seed for doc.ipynb: Lecture 2, written as a presentation.

    ~/fun/jupyter/.venv/bin/python scripts/build_doc.py            # only if doc.ipynb is absent
    ~/fun/jupyter/.venv/bin/python scripts/build_doc.py --force    # overwrite it

The unit is a slide: one figure, gallery or table, then two to four bullets that
carry its point, then a box that repeats the lecture's map with what is done in ink
and the rest greyed out. Every cell is one block with a slide type on it, so the
same file reads as a page in Lab and presents as a deck.

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


def timeline(body: str) -> None:
    """A flow figure whose lines start with a year. The year is set in ink."""
    body = body.strip("\n")
    body = re.sub(r"^(\s*)(\d{4}(?:[–-]\d{2})?)", r'\1<span class="yr">\2</span>', body, flags=re.M)
    md('<pre class="flow">\n' + body + "\n</pre>")


def bullets(*items: str) -> None:
    """Two to four points under a figure, one claim each. One cell, so the deck
    reveals them together."""
    assert 1 <= len(items) <= 4, f"{len(items)} bullets: the rule is two to four"
    md("\n".join("- " + " ".join(i.split()) for i in items))


def gallery(items, cols: int | None = None, label: str | None = None, size: str = "") -> None:
    """A row of figures from assets/img/, each with a caption. `label` names whose
    row this is (a person, a robot, together), `size` is tall or short. Wide
    figures want a row of one or two, or they shrink past reading."""
    n = cols or len(items)
    cls = f"gal c{n}" + (f" {size}" if size else "")
    figs = "".join(
        f'<figure><img src="assets/img/{f}" alt=""><figcaption>{c}</figcaption></figure>'
        for f, c in items)
    kind = "robot" if label and "robot" in label else ("both" if label and "together" in label else "")
    lbl = f'<div class="rowlbl {kind}">{label}</div>\n' if label else ""
    md(lbl + f'<div class="{cls}">\n{figs}\n</div>')


# ------------------------------------------------------------------ the map
# The lecture's table of contents, drawn once at the top and again after every
# unit with what is done in ink and the rest greyed out. Unit names are the
# labels in the boxes, so keep them short; a section that runs past the column
# wraps onto a second line. A section with no units is a heading only.
MAP = [
    ("understand the field", [
        ("§1", "what it is",        ["the loop", "embodiment"]),
        ("§2", "the anatomy",       ["seven stages", "sense", "represent", "anticipate",
                                     "decide", "act", "verify", "adapt"]),
        ("§3", "toward production", ["what gets built", "the missing part", "build on today"]),
    ]),
    ("join the conversation", [
        ("§4", "read a paper",       ["PACES", "on one paper"]),
        ("§5", "the debates",        ["the format", "debate 1", "what to read", "prompts"]),
        ("§6", "keep the hub alive", ["a row, a cell, a column"]),
        ("§7", "my research",        []),
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
            if not units:
                cls = "done" if n_done == len(UNITS) else "todo"
                lines.append(f'{INDENT}<b class="{cls}">{label}</b>')
                continue
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
   'AI.</b> This lecture puts everyone on the same page: what the field is, what people in it '
   'work on, how far it is from production in September 2026, and how to read a paper well '
   'enough to argue about it.</p>')

overview()

bullets(
    "The top half is the field: what it is, the seven stages people work on, and how far "
    "each is from production.",
    "The bottom half is the skill. Read one paper, argue two, and keep the hub growing after "
    "the semester.",
    f"Everything here is in [the hub]({HUB}). This lecture goes stale, and the hub gets edited.",
    "Leave knowing which stage to read and search, with enough shared context to prepare a "
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
    "Model the world, then change it through an embodiment, the hub's word for who moves "
    "the atoms. Acting changes the model, so the two close into a loop.",
    "Every hub paper is tagged with the stages it touches, so the loop can be counted. "
    "§2 walks it one stage at a time.",
)
box("the loop")

md("### Embodiment: who moves the atoms")

flow('''
                      a person                     a robot                    the two together
                      ────────                     ───────                    ────────────────
   the AI's job       teach the person to do       do the task itself         share one task
   what it is good    harder tasks than a robot    narrow tasks, full         a couch through
   for today          can do, with a person's      automation, no one         a doorway. Not in
                      hands and judgment           in the loop                the hub yet
   in the hub         48 papers                    30 papers                  6 papers
''', bold=("a person", "a robot", "the two together"))

gallery([
    ("emb-hololens-topside.jpg",
     "<b>A person.</b> An expert at a laptop circles the switch a crew member wearing a "
     "headset should flip. NASA NEEMO, 2015."),
    ("emb-pi0-robots.jpg",
     "<b>A robot.</b> The seven platforms one π₀ policy drives, from a single arm to a "
     "mobile bimanual base. Black et al., 2024."),
    ("emb-spoton.jpg",
     "<b>Together.</b> A person in mixed reality directs a team of quadrupeds through doors, "
     "drawers and light switches. Spot-On, 2025."),
], cols=3)

bullets(
    "The AI either teaches a person or is the robot. A person brings hands and judgment, "
    "and a robot brings full automation on a narrow task.",
    "People handle harder tasks than robots today, so a human-side system deploys earlier, "
    "and its footage trains the robot later. EgoDex, EgoVLA and DexUMI already do this.",
    "A person and a robot on one task is the smallest branch, 6 of 110 papers, and the one "
    "the next decade needs.",
    "Both embodiments change the world, so every stage in §2 keeps two rows, a person above "
    "and a robot below.",
)
box("embodiment")

# ============================================================ §2

md("## The anatomy of the field: seven stages")

flow('''
          the physical world, objects and the changes they undergo
                    │
          2.1 sense │                                       ▲
                    ▼                                       │
        ┌─ model it ───────────────────────────────┐        │
        │   2.2 represent ──► 2.3 anticipate       │        │  the loop of §1, with the
        └────────────────────────┬─────────────────┘        │  stage each subsection
                                 │ 2.4 decide               │  walks written onto it
        ┌─ change it ────────────▼─────────────────┐        │
        │   2.5 act ──► 2.6 verify ──► 2.7 adapt   ├────────┘
        └──────────────────────────────────────────┘
''', bold=("2.1 sense", "2.2 represent", "2.3 anticipate", "2.4 decide", "2.5 act",
           "2.6 verify", "2.7 adapt"))

bullets(
    "The research topics of the field are the seven stages of the loop in §1. Each gets a "
    "subsection: what it is, what people build, where it stands.",
    "Every subsection keeps the two rows of embodiment, because the same stage is a "
    "different problem for a person and for a robot.",
    "Two stages, 2.6 verify and 2.7 adapt, are where the hub is thinnest, and the lecture "
    "ends up there.",
)

md('''
<table class="k">
<thead><tr><th>stage</th><th>the question it answers</th><th>papers that live there</th></tr></thead>
<tbody>
<tr><td>2.1 sense</td><td>turn sensors into observations</td><td>SAM 2, HOT3D</td></tr>
<tr><td>2.2 represent</td><td>turn observations into a state you can act on</td><td>DINOv2, 3D Gaussian Splatting</td></tr>
<tr><td>2.3 anticipate</td><td>predict what the world does next</td><td>V-JEPA 2, Genie</td></tr>
<tr><td>2.4 decide</td><td>choose the next step or the plan</td><td>SayCan, VLaMP</td></tr>
<tr><td>2.5 act</td><td>emit the action: a motor command, an instruction, an overlay</td><td>π₀, ShowHowTo</td></tr>
<tr><td>2.6 verify</td><td>check whether the intended change happened</td><td>PREGO, SAFE</td></tr>
<tr><td>2.7 adapt</td><td>change the policy or the model from the outcome</td><td>Every Mistake Counts, Inner Monologue</td></tr>
</tbody></table>
''')

bullets(
    "A paper touches two or three stages as a rule. 81 of the 110 do.",
    "A vision-language-action policy (camera and instruction in, joint commands out) is "
    "sense, decide, act. A task assistant on glasses is sense, decide, act, verify.",
    "A person skipping a step and a robot policy failing are the same verify stage, and "
    "the two literatures barely cite each other.",
)
box("seven stages")

# ------------------------------------------------------------ 2.1 sense

md("### 2.1 Sense: what the hardware sees, and where the signal stops")

gallery([
    ("sense-aria-blowup.png",
     "<b>Research glasses.</b> Project Aria carries two scene cameras, an RGB camera, two "
     "eye cameras, seven microphones and two IMUs. Meta, 2023."),
    ("sense-hololens-neemo.jpg",
     "<b>A headset with a display.</b> HoloLens adds a depth camera, hand tracking, and "
     "holograms drawn in the wearer's view. NASA NEEMO 21."),
    ("sense-rayban-meta.jpg",
     "<b>Consumer glasses.</b> Ray-Ban Meta has one camera, microphones and speakers, and "
     "since September 2025 a display in the lens, for $799."),
    ("sense-sketchmehow.jpg",
     "<b>Projector and camera.</b> The instruction is drawn onto the workspace itself, and "
     "no one wears anything. SketchMeHow, 2021."),
], cols=4, label="a person")

bullets(
    "A camera on the head sees what the person sees. 51 of the 110 papers start from that "
    "stream, more than from any other sensor.",
    "The return channel is the second half of the hardware, a display in the lens, a "
    "speaker, or a projector that draws on the table.",
    "The view is partial, hidden by the hands, and moving. All-day glasses with a display "
    "are arriving at consumer prices from three vendors in 2026.",
)

gallery([
    ("sense-umi.jpg",
     "<b>A camera on the wrist.</b> UMI's gripper carries a wide-angle camera, side mirrors "
     "for stereo and an IMU, and is held by a person or bolted to an arm. Chi et al., 2024."),
    ("sense-sparsh.jpg",
     "<b>Touch.</b> Vision-based tactile pads (DIGIT, GelSight) film a gel as it deforms. "
     "Sparsh learns from 460k such images. Meta, 2024."),
], cols=2, label="a robot")

gallery([
    ("sense-realsense.jpg",
     "<b>Depth.</b> A stereo depth camera returns a point cloud, the usual source of the "
     "hub's 3D. Intel RealSense D435."),
    ("sense-velodyne.jpg",
     "<b>Range.</b> LiDAR sweeps a laser and returns distance, standard on mobile robots and "
     "rare on arms. Velodyne."),
    ("sense-aloha.jpg",
     "<b>The whole rig.</b> ALOHA puts two cameras over the table and one on each wrist, and "
     "a person moves the leader arms to teach it. Zhao et al., 2023."),
], cols=3)

bullets(
    "A robot's cameras sit on the wrist and over the table. Depth and LiDAR add range, and "
    "a tactile pad on the fingertip adds contact.",
    "Touch is where the hub is thinnest. 2 of 110 papers sense it, and 8 hold force, mass "
    "or friction in their state.",
    "Every sensor is calibrated and priced per arm. Hand-held grippers (UMI, DexUMI) are "
    "the way around it, because the data arrives with no robot in the room.",
)

code('''
import nbdoc
nbdoc.bar("data/sensing_counts.csv", title="Papers by sensing channel",
          note="the hub on 2026-09-07 · 110 papers · a paper can carry several",
          ylabel="papers")
''')

bullets(
    "Cameras dominate on both rows, egocentric first and the robot's own second. Everything "
    "that is not a camera is a tenth of the hub or less.",
    "Simulators and web video count as sensors here, because 39 papers learn from them and "
    "never see a real one.",
)

gallery([
    ("sense-rgbnomore.png",
     "<b>Skip the decode.</b> A ViT reads JPEG's DCT coefficients straight off the disk and "
     "never sees RGB. Park and Johnson, CVPR 2023."),
    ("sense-rgbnomore-dct.png",
     "<b>What it reads.</b> The 8×8 frequency blocks JPEG stores are patches already, "
     "which is why a transformer takes them and a convnet does not."),
], cols=2, size="short")

bullets(
    "From sensing to representing is still research. Where the sensor stops and the "
    "representation starts is a design choice, and moving it is a paper.",
    "RGB no more trains a ViT on the encoded JPEG and gets 39.2% faster training and 17.9% "
    "faster inference with no accuracy loss.",
    "The robot-side twin is Sparsh, touch representations learned from raw tactile images "
    "across three sensor types, in place of hand-built force and slip models.",
)
box("sense")

# ------------------------------------------------------------ 2.2 represent

md("### 2.2 Represent: there is no best representation, only the one for the job")

timeline('''
   2012  AlexNet                supervised features from a labeled corpus
   2017  Transformer            attention, built to train in parallel on GPUs
   2020  ViT · NeRF             an image as patches; a scene as a neural field
   2021  CLIP · MAE · DINO      image and text in one space; masked and self-distilled features
   2022  latent diffusion       generate; the representation is what a denoiser learns
   2023  I-JEPA · DINOv2 · 3DGS predict in latent space; frozen features; explicit geometry
   2024  V-JEPA                 the same prediction over video
   2025  V-JEPA 2 · DINOv3      video → latent world model → robot planning
''')

bullets(
    "Representation learning is this stage. Each milestone changed what a downstream model "
    "can read off an image, from labels to language to geometry to the future.",
    "The transformer won on parallel training, not accuracy. A ViT trails a ResNet on "
    "mid-sized data and only wins past 14M images (Dosovitskiy et al., 2020).",
    "When compute stops binding, other designs come back. All-MLP (MLP-Mixer, 2021) and "
    "recurrent (Mamba, 2023) models both match transformers on their benchmarks.",
)

gallery([
    ("rep-clip.png",
     "<b>Language-aligned.</b> CLIP puts an image and its caption in one space, so a class "
     "can be named instead of labeled. Radford et al., 2021."),
    ("rep-dinov2.jpg",
     "<b>Self-supervised.</b> The first three components of DINOv2's features, with no "
     "labels, already separate parts. Oquab et al., 2023."),
], cols=2, size="short")

gallery([
    ("rep-ijepa.png",
     "<b>Predictive.</b> I-JEPA predicts the representation of a masked region, never the "
     "pixels. Assran et al., 2023."),
    ("rep-3dgs.jpg",
     "<b>Geometric.</b> 3D Gaussian Splatting holds a scene as explicit primitives that "
     "render in real time. Kerbl et al., 2023."),
], cols=2, size="short")

bullets(
    "There is no best one. Half the hub's world models start from a frozen DINOv2 because "
    "freezing it is cheap, not because it fits their task.",
    "The choice follows the need and the budget. Language-aligned to follow instructions, "
    "geometric to plan a grasp, predictive to anticipate, and a convnet when production "
    "data is small.",
    "Read a representation paper for the downstream task it was tested on. That is the "
    "job it is good for, and often the only one.",
)
box("represent")

# ------------------------------------------------------------ 2.3 anticipate

md("### 2.3 Anticipate: think before you move")

gallery([
    ("ant-peva.jpg",
     "<b>A body's world model.</b> PEVA predicts first-person video from the wearer's own "
     "3D pose, and can render the counterfactual move. Bai et al., 2025."),
    ("ant-worldprediction.jpg",
     "<b>The semantic side.</b> WorldPrediction tests whether a model can say which action "
     "took a scene from state A to state B, and in which order. 2025."),
], cols=2)

bullets(
    "People think before they move, and often run the counterfactual first: what fails if "
    "I slice the potato instead of dicing it. Physical AI needs the same stage.",
    "The text side reasons over steps and effects. Procedural reasoning and counterfactual "
    "reasoning are the search terms, and WorldPrediction benchmarks both.",
    "The vision side is the world model, a video generator rendering the action and its "
    "effect from the actor's viewpoint. PEVA for a body, V-JEPA 2 for a robot.",
    "A person and a robot follow the prediction differently. That difference is 2.4 and 2.5.",
)

code('''
import nbdoc
nbdoc.bar("data/anticipate_by_representation.csv",
          title="What the anticipate-stage papers predict",
          note="29 papers anticipate · the hub on 2026-09-07 · a paper can carry several",
          ylabel="papers")
''')

bullets(
    "29 papers anticipate. 15 predict pixels, 8 a latent, 7 words. What the prediction is "
    "made of is an open choice, and it sets what 2.4 can do.",
    "Pixels are the easiest to check and the most expensive to plan in. A latent is cheap "
    "to plan in and cannot be looked at.",
)

gallery([
    ("ant-vjepa2-flow.png",
     "<b>Video in, robot out.</b> V-JEPA 2 learns from a million hours of internet video, "
     "then 62 hours of unlabeled robot video, then picks and places on an arm in a lab it "
     "never saw. Meta, 2025."),
], cols=1, size="short")

bullets(
    "Only the last 62 hours involve a robot. The planner samples actions and keeps the one "
    "whose predicted latent lands nearest the goal.",
    "Predicted futures still break physics where it can be measured. Text-to-video models "
    "fail most of PhyGenBench's 27 laws, and scale does not close the gap.",
)
box("anticipate")

# ------------------------------------------------------------ 2.4 decide

md("### 2.4 Decide: pick one future, and say why")

code('''
import nbdoc
nbdoc.bar("data/anticipate_decide.csv", title="Anticipate and decide: one stage or two?",
          note="the hub on 2026-09-07 · 110 papers", ylabel="papers")
''')

bullets(
    "Most of the time the two are one network. 8 papers do both explicitly, 36 decide with "
    "no separate prediction, and 21 predict without ever choosing.",
    "When they separate, anticipate generates futures and decide selects one. That is the "
    "boundary, and it is why the lecture keeps two subsections.",
    "The human embodiment forces the split. The person, not the model, executes, so the "
    "decision has to be handed over in a form they can check.",
)

gallery([
    ("dec-vlp-tree.jpg",
     "<b>Sample, score, choose.</b> Video Language Planning grows a tree of generated "
     "video futures and keeps the branch a value model scores highest. Du et al., 2023."),
], cols=1, size="short")

bullets(
    "Selection is a search over imagined outcomes. Video Language Planning searches a tree "
    "of generated clips, and V-JEPA 2 samples actions and picks by predicted cost.",
    "More compute buys a better plan in both, which is the argument for keeping anticipate "
    "and decide separable even when one network does both.",
)

gallery([
    ("dec-satori.jpg",
     "<b>When to speak.</b> Satori models what the person believes, wants and intends, and "
     "decides on its own when to show guidance. Li et al., 2024."),
    ("dec-vid2coach.jpg",
     "<b>What to say.</b> Vid2Coach turns a how-to video into instructions a blind cook "
     "can act on, with a completion check per step. Huh et al., 2025."),
], cols=2, label="a person")

gallery([
    ("dec-arguidance.jpg",
     "<b>How much to show.</b> AR guidance for assembly made workers 31% faster, and they "
     "made more errors. 2025."),
], cols=1, size="short")

bullets(
    "For a person, deciding includes what to say and when. Satori's authors call timing the "
    "hard problem, and the AR study shows more guidance is not better.",
    "Too much and the person is overwhelmed, too little and they distrust it. A chatbot's "
    "essay followed by three options is the virtual version of the same failure.",
    "The physical version has stakes. A step near fire, electricity or a patient needs a "
    "decision the person can check before acting, with the reason attached.",
)
box("decide")

# ------------------------------------------------------------ 2.5 act

md("### 2.5 Act: a person just acts, a robot has to be controlled")

code('''
import nbdoc
nbdoc.bar("data/act_by_channel.csv", title="What the act-stage papers emit",
          note="the hub on 2026-09-07 · a paper can carry several", ylabel="papers")
''')

bullets(
    "For a person, act is the easy stage. Given a good decision, they do it. The system's "
    "act is an instruction, an image or an overlay.",
    "For a robot, act is control, the chosen plan turned into joint commands at tens of "
    "hertz. All of robot learning lives in the motor-action bar.",
)

timeline('''
   2022  Code as Policies       the language model writes the program that calls the controller
   2022  RT-1                   a transformer maps camera and instruction to discrete actions
   2023  Diffusion Policy · ACT actions as a denoised trajectory; commit to a chunk at a time
   2023  RT-2                   a VLM fine-tuned to emit actions as tokens: the first VLA
   2024  OpenVLA · π₀           an open 7B VLA; a flow-matching action head across bodies
   2025  GR00T N1 · π₀.₅        a slow reasoner over a fast actor; open-world generalization
   2025–26  Genie Envisioner · DreamZero   world action models: predict the video and the action together
''')

bullets(
    "Four branches compete: write the program, denoise the trajectory, emit action tokens "
    "from a VLM, or predict video and action together. No one knows yet which wins.",
    "Diffusion Policy beat the prior state of the art by 46.9% across 12 tasks. OpenVLA "
    "beat RT-2-X by 16.5 points with 7× fewer parameters.",
    "A world action model folds anticipate, decide and act into one network. DreamZero runs "
    "14B parameters closed-loop at 7 Hz and generalizes twice as well as VLAs.",
)

gallery([
    ("act-dp.png",
     "<b>Denoise the trajectory.</b> Diffusion Policy keeps the several right ways to do a "
     "task that a regression head averages away. Chi et al., 2023."),
    ("act-cap.jpg",
     "<b>Write the program.</b> In Code as Policies the plan is Python, so it can be read, "
     "composed and debugged. Liang et al., 2022."),
], cols=2, label="a robot")

gallery([
    ("act-dreamzero.jpg",
     "<b>Predict video and action.</b> DreamZero, a world action model on a video diffusion "
     "backbone, transfers from human video with 10 to 20 minutes of data. 2026."),
], cols=1)

bullets(
    "Each branch is a bet on what a policy should output: code, a trajectory, tokens, or a "
    "future. The bets are still open, and worth exploring.",
    "Push end to end far enough and represent goes in too. V-JEPA 2 plans in its own latent "
    "and never renders a pixel.",
)
box("act")

# ------------------------------------------------------------ 2.6 verify

md("### 2.6 Verify: close the loop on what happened")

gallery([
    ("ver-im.jpg",
     "<b>Feed the outcome back.</b> Inner Monologue hands the planner a success flag, a "
     "scene description or a person's answer after every skill. Huang et al., 2022."),
    ("ver-safe.jpg",
     "<b>Read failure off the policy.</b> SAFE finds a failure zone in a VLA's own features "
     "and alerts before the task is lost. Gu et al., 2025."),
    ("ver-reflect.jpg",
     "<b>Explain it.</b> REFLECT summarizes what the robot sensed and asks a language model "
     "why the task failed, then replans. Liu et al., 2023."),
], cols=3, label="a robot")

bullets(
    "Verify is what makes the next decision rest on what happened rather than on what was "
    "intended. Without it the loop is open, however good the policy.",
    "The robot side has had it since Inner Monologue, a check after every step and a "
    "replan. SAFE detects the failure and REFLECT explains it.",
)

gallery([
    ("ver-prego.png",
     "<b>Detect the mistake.</b> PREGO recognizes the current step, predicts what should "
     "come next, and flags the disagreement, trained on correct runs only. CVPR 2024."),
    ("ver-matt.jpg",
     "<b>Attribute it.</b> Mistake Attribution says which part of the instruction was "
     "violated, the frame of no return, and where in the frame. 2025."),
    ("ver-tpmd.jpg",
     "<b>Explain it.</b> Transparent PMD requires a rationale and scores whether the "
     "rationale entails the verdict. Storks et al., EMNLP 2025."),
], cols=3, label="a person")

bullets(
    "The human side calls it mistake detection. The intervals are longer, a step rather "
    "than a motor command, and the verdict needs a reason the person will accept.",
    "The research has moved from a flag to an account of what was wrong, when it became "
    "irreversible, where in the frame, and why the system thinks so.",
    "The two literatures ask the same question at the same stage and barely cite each other.",
)

code('''
import nbdoc
nbdoc.bar("data/verify_by_embodiment.csv", title="Verify-stage papers, by who moves the atoms",
          note="31 papers verify · the hub on 2026-09-07", ylabel="papers")
''')

code('''
import nbdoc
nbdoc.table("data/embodiment_loop.csv",
            caption="Who closes the loop, in the hub on 2026-09-07. A paper closes the loop "
                    "when it consumes the effect of its own action at run time.")
''')

bullets(
    "21 of the 31 verify papers watch a person. 5 watch a robot.",
    "23 of the 30 robot papers consume the effect of their own action. 14 of the 48 human "
    "ones do. Most guidance systems emit an instruction and stop.",
    "A robot policy that never looked at the result would not get published. A guidance "
    "system that never does is the norm. That gap is a project.",
)
box("verify")

# ------------------------------------------------------------ 2.7 adapt

md("### 2.7 Adapt: better on the next attempt because of the last one")

gallery([
    ("ada-emc.png",
     "<b>In the physical world.</b> Every Mistake Counts keeps a graph of which parts fit "
     "and what must come first, and updates it as it watches. Ding et al., 2023."),
    ("ada-dgm.png",
     "<b>In code.</b> The Darwin Gödel Machine rewrites its own agent code and keeps the "
     "versions that score higher. Zhang et al., 2025."),
], cols=2)

gallery([
    ("ada-rsi.jpg",
     "<b>The map.</b> A July 2026 survey of 1,250 papers sorts self-improvement by what "
     "changes and how closed the loop is. Most of it is bounded self-refinement."),
], cols=1, size="tall")

bullets(
    "The old name is continual learning. The new one is self-evolving AI, and it covers "
    "the harness around the model as well as its weights.",
    "The frontier labs run it on coding agents, where the loop closes cheaply. The Darwin "
    "Gödel Machine and its relatives rewrite their own code and keep what scores.",
    "The same survey finds the open-ended version bounded on every measured axis, and MIT "
    "Technology Review's August 2026 read is that it is not coming quickly.",
    "Physical AI needs it too. A guidance system that changes its next instruction because "
    "of what the last one did is this stage, and the stage is empty.",
)

code('''
import nbdoc
nbdoc.bar("data/loop_stage_counts.csv", title="Papers per loop stage",
          note="the hub on 2026-09-07 · a paper spans several", ylabel="papers")
''')

bullets(
    "7 of 110 papers adapt. The field can tell that something went wrong and almost never "
    "learns from it while running.",
    "The exceptions are from 2023 and 2022. Every Mistake Counts updates its constraints as "
    "it watches, and Inner Monologue feeds the outcome back as text.",
)
box("adapt")

# ============================================================ §3

md("## Toward production and real-world impact")

md("### What gets built, and on which tasks")

code('''
import nbdoc
nbdoc.table("data/contribution_by_domain.csv",
            caption="What a paper contributes, by the domain it works in. "
                    "The hub on 2026-09-07; a paper can carry several of each.")
''')

bullets(
    "81 of 110 papers are methods, 32 datasets, 17 systems, 2 surveys. The community "
    "builds methods.",
    "74 papers touch everyday tasks, 21 industrial, 6 clinical. Daily tasks are the proxy, "
    "because that is where the footage is.",
    "Daily tasks have reached systems tested on people (Vid2Coach, Satori, AROMA). "
    "Professional tasks are still at data and benchmarks (IndustReal, HoloAssist, Ego-EXTRA).",
)
box("what gets built")

md("### The missing part is data")

code('''
import nbdoc
nbdoc.bar("data/hours_by_domain.csv", title="Hours of released first-person video, by domain",
          note="the hub's dataset papers, each paper's own headline count · multi-view sets count every camera",
          ylabel="hours")
''')

code('''
import nbdoc
nbdoc.table("data/dataset_hours.csv",
            caption="The datasets behind the bars, with each paper's own count. "
                    "Assembly101's 513 hours are 12 views of 362 seven-minute sequences.")
''')

bullets(
    "About 4,800 hours of everyday life, 1,286 of skill from one dataset, 735 industrial, "
    "513 of them twelve views of toy assembly, and nothing clinical.",
    "The professional end owns the value and the intellectual property. Hospitals and "
    "factories do not release footage, so the largest record of expert guidance is 50 hours.",
    "Impact in production is a data problem before a method problem. The routes are "
    "one-demonstration learning, synthetic data, or data that never leaves the site.",
)
box("the missing part")

md("### What you can build on today")

gallery([
    ("act-pi07.jpg",
     "<b>For a robot, π₀.₇</b>, Physical Intelligence, April 2026. Follows instructions in "
     "kitchens it never saw and folds laundry on a robot that never trained on it. "
     "<a href='https://www.pi.website/blog/pi07'>blog</a> · "
     "<a href='https://arxiv.org/abs/2604.15483'>arXiv</a>"),
    ("sota-pro2assist.jpg",
     "<b>For a person, Pro²Assist</b>, May 2026. Tracks step progress from AR-glasses "
     "sensing and decides when to help, through a whole procedure. "
     "<a href='https://arxiv.org/abs/2605.04227'>arXiv</a>"),
], cols=2)

bullets(
    "Two links, one per embodiment, to the latest thing you can start from.",
    "Both are stacks of 2.1 to 2.5, and the robot one is a product. Neither adapts.",
)
box("build on today")

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
    f"PACES is Jason's method: Problem, Approach, Claims, Evaluation, Substantiation, asked "
    f"of every paper in that order ([the write-up]({PACES})).",
    "Skip the introduction and the related work on a first read. What is left is the "
    "problem, the method and the experiments, plus the claim and the verdict.",
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
    "Two papers. The sides argue the claim, its substantiation, the method.",
    "Write the five PACES rows for both papers before you pick a side.",
)
box("the format")

debate1(md, flow, bullets, box, gallery)

# ============================================================ §6

md("## Keep the hub alive together")

flow('''
   read a paper ──► PACES + 13 columns ──► a row ──► the counts move ──► a gap closes or opens
                                                            │
   a debate ends ──► a wrong cell · a weak why · a value with no paper ──► an edit
''')

bullets(
    "The hub outlives the course by design, with no schedule, lecture numbers or "
    "assignments in it. What it needs from you is rows and arguments.",
    "A row is a paper read with PACES and tagged on the 13 columns. No cell runs past two "
    "sentences, and no number comes from outside the paper.",
    "A cell is a wrong number, a tldr that names the topic instead of the claim, or a tag "
    "too generous. Every correction counts.",
    "A column is a vocabulary value with no paper in it. Find the paper or delete the "
    "value, because the build fails on an empty one.",
)

md('''
> [C] on the contribution protocol
>
> [C] **ai:** The channel is yours to set: issues, email, or collaborator access to the private repo. Left out of the prose until you decide.
''')
box("a row, a cell, a column")

md('''
That is the whole lecture. The field is a loop whose last two stages are nearly empty, and
the hub is the map of it. PACES reads one paper, the debates read two, and the hub is what
stays after the semester.
''')

# ============================================================ §7

md("## My Research")


if __name__ == "__main__":
    build(force="--force" in sys.argv)
