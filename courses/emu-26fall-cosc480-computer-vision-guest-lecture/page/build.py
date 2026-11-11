#!/usr/bin/env python3
"""build — write the guest lecture's page and its GitHub copy from the talk below.

    python3 build.py          # index.html beside this file, ../README.md one level up

The talk is the first half of ROB 599 Lecture 2, cut to about 40 minutes for EMU's
COSC 480/592 Computer Vision on 2026-11-17. It is written below as one call per
block, in the order the audience sees them:

    title  overview  h2  h3  flow  bullets  gallery  chart  table  box

A unit is one figure, gallery or table, then two to four bullets that each carry one
claim, then box(), which redraws MAP with the finished units in ink and the rest in
grey. To add or drop a unit, change MAP, and every box follows.

Each block keeps the id of the Lecture 2 notebook cell it came from (c005, c010, …),
and each heading keeps a fixed slug. Comments and present-mode steps attach to those
ids, so keep a block's id when you edit it and give a new block a new one.

Both outputs are generated, so edit this file and rebuild. The numbers quote the hub
on 2026-09-07 (110 papers) and are never recounted, which is why the four charts in
assets/charts/ are files drawn that day rather than code.
"""
from __future__ import annotations

import html
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent                  # page/
PAGE = HERE / "index.html"
README = HERE.parent / "README.md"                      # what GitHub shows for the folder
PREFIX = "page/"                                        # README sits one level above the assets
DOC_ID = "emu-guest-lecture"                            # names the comment and present stores
WIDTH = 880                                             # GitHub's README column, roughly

BLOCKS: list[tuple[str, str]] = []                      # (page HTML, README markup), in order


def add(page: str, readme: str) -> None:
    BLOCKS.append((page.strip("\n"), readme.strip("\n")))


# ------------------------------------------------------------------ the map
# The talk's table of contents, drawn under the title and again after every unit with
# what is done in ink and the rest in grey. Unit names are the words in the boxes, so
# keep them short. A section with no units is a heading only.
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
LINE_W = 96           # a longer line scrolls inside its box instead of wrapping


def render_map(done_through: str | None) -> str:
    """The map's lines. `None` draws the overview, everything in ink."""
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
    return "\n".join(lines)


def github_pre(body: str) -> str:
    """GitHub drops class attributes, so ink becomes bold and grey becomes plain."""
    body = re.sub(r'<(span|b) class="done">(.*?)</\1>', r"<b>\2</b>", body)
    body = re.sub(r'<(span|b) class="todo">(.*?)</\1>', r"\2", body)
    body = re.sub(r'<span class="grp">(.*?)</span>', r"<b>\1</b>", body)
    body = re.sub(r'<span class="lbl">(.*?)</span>', r"<i>\1</i>", body)
    body = re.sub(r'<span class="sep">(.*?)</span>', r"\1", body)
    body = re.sub(r'<span class="yr">(.*?)</span>', r"<b>\1</b>", body)
    return "<pre>\n" + body + "\n</pre>"


# ------------------------------------------------------------------ blocks
def title(kicker: str, text: str) -> None:
    add(f'<h1 id="title"><span class="kicker">{kicker}</span>{text}</h1>',
        f"# {text}\n\n{kicker}. This page is generated by [`page/build.py`]({PREFIX}build.py), "
        f"which also writes the page the talk is presented from, "
        f"[`page/index.html`]({PREFIX}index.html).")


def overview(bid: str) -> None:
    body = render_map(None)
    add(f'<pre class="flow map" id="{bid}">\n{body}\n</pre>', github_pre(body))


def box(bid: str, done_through: str) -> None:
    assert done_through in UNITS, done_through
    body = render_map(done_through)
    add(f'<pre class="flow map" id="{bid}">\n{body}\n</pre>', github_pre(body))


def h2(slug: str, text: str) -> None:
    add(f'<h2 id="{slug}">{text}</h2>', f"## {text}")


def h3(slug: str, text: str) -> None:
    add(f'<h3 id="{slug}">{text}</h3>', f"### {text}")


def flow(bid: str, body: str) -> None:
    """A drawing in a monospace box. Write it plain so the columns line up as typed.
    `<b>` sets words in ink and `<span class="yr">` sets a timeline's years in pink."""
    body = body.strip("\n")
    add(f'<pre class="flow" id="{bid}">\n{body}\n</pre>', github_pre(body))


LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")


def bullets(bid: str, *items: str) -> None:
    """Two to four points under a figure, one claim each. `[text](url)` makes a link."""
    assert 1 <= len(items) <= 4, f"{bid}: {len(items)} bullets, and the rule is two to four"
    items = [" ".join(i.split()) for i in items]
    lis = "\n".join("<li>" + LINK.sub(r'<a href="\2">\1</a>', i) + "</li>" for i in items)
    add(f'<ul class="caption" id="{bid}">\n{lis}\n</ul>', "\n".join("- " + i for i in items))


def gallery(bid: str, items: list[tuple[str, str]], label: str | None = None,
            size: str = "") -> None:
    """A row of figures from assets/img/, each with its caption. `label` names whose row
    it is (a person, a robot, together) and `size` is tall or short. Wide figures want a
    row of one or two, or they shrink past reading."""
    n = len(items)
    cls = f"gal c{n}" + (f" {size}" if size else "")
    kind = "robot" if label and "robot" in label else ("both" if label and "together" in label else "")
    lbl = f'<p class="rowlbl{" " + kind if kind else ""}">{label}</p>\n' if label else ""
    figs = "\n".join(f'<figure><img src="assets/img/{f}" alt=""><figcaption>{c}</figcaption></figure>'
                     for f, c in items)
    w = WIDTH // n
    imgs = "".join(f'<td valign="top" width="{100 // n}%"><img src="{PREFIX}assets/img/{f}" width="{w}"></td>'
                   for f, _ in items)
    caps = "".join(f'<td valign="top"><sub>{c}</sub></td>' for _, c in items)
    add(f'<div class="{cls}" id="{bid}">\n{lbl}{figs}\n</div>',
        (f"<b>{label}</b>\n" if label else "") + f"<table><tr>{imgs}</tr><tr>{caps}</tr></table>")


def chart(bid: str, name: str, alt: str) -> None:
    """A bar chart from assets/charts/, drawn from the hub's counts on 2026-09-07. The
    title and the note are inside the drawing."""
    assert (HERE / "assets" / "charts" / f"{name}.svg").exists(), name
    add(f'<figure class="chart" id="{bid}"><img src="assets/charts/{name}.svg" alt="{html.escape(alt)}"></figure>',
        f'<img src="{PREFIX}assets/charts/{name}.svg" alt="{html.escape(alt)}">')


def _isnum(v: str) -> bool:
    try:
        float(v)
        return True
    except ValueError:
        return False


def table(bid: str, head: list[str], rows: list[list[str]], caption: str = "",
          cls: str = "") -> None:
    """A real table. Columns that hold only numbers are set right-aligned."""
    num = {i for i in range(len(head)) if all(_isnum(r[i]) for r in rows)}

    def cells(tag: str, vals: list[str], styled: bool) -> str:
        return "".join(f'<{tag} class="num">{v}</{tag}>' if styled and i in num else f"<{tag}>{v}</{tag}>"
                       for i, v in enumerate(vals))

    def render(styled: bool) -> str:
        cap = f"<caption>{caption}</caption>" if caption else ""
        body = "\n".join(f"<tr>{cells('td', r, styled)}</tr>" for r in rows)
        return f"{cap}\n<thead><tr>{cells('th', head, styled)}</tr></thead>\n<tbody>\n{body}\n</tbody>"

    attrs = (f' class="{cls}"' if cls else "") + f' id="{bid}"'
    add(f"<table{attrs}>{render(True)}</table>", f"<table>{render(False)}</table>")


# ================================================================== the talk
# ------------------------------------------------------------ title and opening
title('Guest lecture · EMU COSC 480/592 Computer Vision · November 17, 2026 · Yayuan Li, '
        'University of Michigan',
      'Where Physical AI Stands: From First-Person Video to Agents That Act')

overview('c002')

bullets('c003',
    'One pass over the field: what physical AI is, the seven stages people work on, and how '
    'far each is from production.',
    'Broad rather than deep. Every stage names its papers, and the last slide lists keywords '
    'to search later.',
    'Everything here is in [the hub](https://yayuanli-org.github.io/awesome-physical-ai/), '
    'an open database of physical AI papers. These slides are on '
    '[GitHub](https://github.com/yayuanli-org/awesome-physical-ai).',
    'Leave knowing which stage interests you and what to search for next.')

# ----------------------------------------------------- §1 what it is
h2('what-it-is', 'What physical AI is')

flow('c005', """
          the physical world, objects and the changes they undergo
                    │
              sense │                                       ▲
                    ▼                                       │
        ┌─ <b>model it</b> ───────────────────────┐                │  acting changes the world,
        │   represent ──► anticipate       │                │  so what has to be modeled
        └────────────────┬─────────────────┘                │  changes too
                         │ decide                           │
        ┌─ <b>change it</b> ────▼──────────────────┐               │
        │   act ──► verify ──► adapt        ├───────────────┘
        │   through an embodiment: a        │
        │   person wearing glasses, a       │
        │   robot, or the two together      │
        └───────────────────────────────────┘
""")

bullets('c006',
    'The subject is the change. Who carries it is a variable: a person wearing glasses, a '
    'robot, or both.',
    "Model the world, then change it through an embodiment, the hub's word for who moves the "
    'atoms. Acting changes the model, so the two close into a loop.',
    'Every hub paper is tagged with the stages it touches, so the loop can be counted. §2 '
    'walks it one stage at a time.')

box('c007', 'the loop')

# ----------------------------------------------------- §1 embodiment
h3('embodiment', 'Embodiment: who moves the atoms')

flow('c009', """
                      <b>a person</b>                     <b>a robot</b>                    <b>the two together</b>
                      ────────                     ───────                    ────────────────
   the AI's job       teach the person to do       do the task itself         share one task
   what it is good    harder tasks than <b>a robot</b>    narrow tasks, full         a couch through
   for today          can do, with <b>a person</b>'s      automation, no one         a doorway. Not in
                      hands and judgment           in the loop                the hub yet
   in the hub         48 papers                    30 papers                  6 papers
""")

gallery('c010', [
    ('emb-hololens-topside.jpg',
     '<b>A person.</b> An expert at a laptop circles the switch a crew member wearing a '
     'headset should flip. NASA NEEMO, 2015.'),
    ('emb-pi0-robots.jpg',
     '<b>A robot.</b> The seven platforms one π₀ policy drives, from a single arm to a mobile '
     'bimanual base. Black et al., 2024.'),
    ('emb-spoton.jpg',
     '<b>Together.</b> A person in mixed reality directs a team of quadrupeds through doors, '
     'drawers and light switches. Spot-On, 2025.'),
])

bullets('c011',
    'The AI either teaches a person or is the robot. A person brings hands and judgment, and '
    'a robot brings full automation on a narrow task.',
    'People handle harder tasks than robots today, so a human-side system deploys earlier, '
    'and its footage trains the robot later. EgoDex, EgoVLA and DexUMI already do this.',
    'A person and a robot on one task is the smallest branch, 6 of 110 papers, and the one '
    'the next decade needs.',
    'Both embodiments change the world, so every stage in §2 keeps two rows, a person above '
    'and a robot below.')

box('c012', 'embodiment')

# -------------------------------------- §2 the anatomy: seven stages
h2('anatomy', 'The anatomy of the field: seven stages')

flow('c014', """
          the physical world, objects and the changes they undergo
                    │
          <b>2.1 sense</b> │                                       ▲
                    ▼                                       │
        ┌─ model it ───────────────────────────────┐        │
        │   <b>2.2 represent</b> ──► <b>2.3 anticipate</b>       │        │  the loop of §1, with the
        └────────────────────────┬─────────────────┘        │  stage each subsection
                                 │ <b>2.4 decide</b>               │  walks written onto it
        ┌─ change it ────────────▼─────────────────┐        │
        │   <b>2.5 act</b> ──► <b>2.6 verify</b> ──► <b>2.7 adapt</b>   ├────────┘
        └──────────────────────────────────────────┘
""")

bullets('c015',
    'The research topics of the field are the seven stages of the loop in §1. Each gets a '
    'subsection: what it is, what people build, where it stands.',
    'Every subsection keeps the two rows of embodiment, because the same stage is a '
    'different problem for a person and for a robot.',
    'Two stages, 2.6 verify and 2.7 adapt, are where the hub is thinnest, and the lecture '
    'ends up there.')

table('c016', ['stage', 'the question it answers', 'papers that live there'], [
    ['2.1 sense', 'turn sensors into observations', 'SAM 2, HOT3D'],
    ['2.2 represent', 'turn observations into a state you can act on', 'DINOv2, 3D Gaussian Splatting'],
    ['2.3 anticipate', 'predict what the world does next', 'V-JEPA 2, Genie'],
    ['2.4 decide', 'choose the next step or the plan', 'SayCan, VLaMP'],
    ['2.5 act', 'emit the action: a motor command, an instruction, an overlay', 'π₀, ShowHowTo'],
    ['2.6 verify', 'check whether the intended change happened', 'PREGO, SAFE'],
    ['2.7 adapt', 'change the policy or the model from the outcome', 'Every Mistake Counts, Inner Monologue'],
], cls="k")

bullets('c017',
    'A paper touches two or three stages as a rule. 81 of the 110 do.',
    'A vision-language-action policy (camera and instruction in, joint commands out) is '
    'sense, decide, act. A task assistant on glasses is sense, decide, act, verify.',
    'A person skipping a step and a robot policy failing are the same verify stage, and the '
    'two literatures barely cite each other.')

box('c018', 'seven stages')

# --------------------------------------------------------- 2.1 sense
h3('sense', '2.1 Sense: what the hardware sees, and where the signal stops')

gallery('c020', [
    ('sense-aria-blowup.png',
     '<b>Research glasses.</b> Project Aria carries two scene cameras, an RGB camera, two eye '
     'cameras, seven microphones and two IMUs. Meta, 2023.'),
    ('sense-hololens-neemo.jpg',
     '<b>A headset with a display.</b> HoloLens adds a depth camera, hand tracking, and '
     "holograms drawn in the wearer's view. NASA NEEMO 21."),
    ('sense-rayban-meta.jpg',
     '<b>Consumer glasses.</b> Ray-Ban Meta has one camera, microphones and speakers, and '
     'since September 2025 a display in the lens, for $799.'),
    ('sense-sketchmehow.jpg',
     '<b>Projector and camera.</b> The instruction is drawn onto the workspace itself, and no '
     'one wears anything. SketchMeHow, 2021.'),
], label='a person')

bullets('c021',
    'A camera on the head sees what the person sees. 51 of the 110 papers start from that '
    'stream, more than from any other sensor.',
    'The return channel is the second half of the hardware, a display in the lens, a '
    'speaker, or a projector that draws on the table.',
    'The view is partial, hidden by the hands, and moving. All-day glasses with a display '
    'are arriving at consumer prices from three vendors in 2026.')

gallery('c022', [
    ('sense-umi.jpg',
     "<b>A camera on the wrist.</b> UMI's gripper carries a wide-angle camera, side mirrors "
     'for stereo and an IMU, and is held by a person or bolted to an arm. Chi et al., 2024.'),
    ('sense-sparsh.jpg',
     '<b>Touch.</b> Vision-based tactile pads (DIGIT, GelSight) film a gel as it deforms. '
     'Sparsh learns from 460k such images. Meta, 2024.'),
], label='a robot')

gallery('c023', [
    ('sense-realsense.jpg',
     '<b>Depth.</b> A stereo depth camera returns a point cloud, the usual source of the '
     "hub's 3D. Intel RealSense D435."),
    ('sense-velodyne.jpg',
     '<b>Range.</b> LiDAR sweeps a laser and returns distance, standard on mobile robots and '
     'rare on arms. Velodyne.'),
    ('sense-aloha.jpg',
     '<b>The whole rig.</b> ALOHA puts two cameras over the table and one on each wrist, and '
     'a person moves the leader arms to teach it. Zhao et al., 2023.'),
])

bullets('c024',
    "A robot's cameras sit on the wrist and over the table. Depth and LiDAR add range, and a "
    'tactile pad on the fingertip adds contact.',
    'Touch is where the hub is thinnest. 2 of 110 papers sense it, and 8 hold force, mass or '
    'friction in their state.',
    'Every sensor is calibrated and priced per arm. Hand-held grippers (UMI, DexUMI) are the '
    'way around it, because the data arrives with no robot in the room.')

box('c029', 'sense')

# ----------------------------------------------------- 2.2 represent
h3('represent', '2.2 Represent: there is no best representation, only the one for the job')

flow('c031', """
   <span class="yr">2012</span>  AlexNet                supervised features from a labeled corpus
   <span class="yr">2017</span>  Transformer            attention, built to train in parallel on GPUs
   <span class="yr">2020</span>  ViT · NeRF             an image as patches; a scene as a neural field
   <span class="yr">2021</span>  CLIP · MAE · DINO      image and text in one space; masked and self-distilled features
   <span class="yr">2022</span>  latent diffusion       generate; the representation is what a denoiser learns
   <span class="yr">2023</span>  I-JEPA · DINOv2 · 3DGS predict in latent space; frozen features; explicit geometry
   <span class="yr">2024</span>  V-JEPA                 the same prediction over video
   <span class="yr">2025</span>  V-JEPA 2 · DINOv3      video → latent world model → robot planning
""")

bullets('c032',
    'Representation learning is this stage. Each milestone changed what a downstream model '
    'can read off an image, from labels to language to geometry to the future.',
    'The transformer won on parallel training, not accuracy. A ViT trails a ResNet on '
    'mid-sized data and only wins past 14M images (Dosovitskiy et al., 2020).',
    'When compute stops binding, other designs come back. All-MLP (MLP-Mixer, 2021) and '
    'recurrent (Mamba, 2023) models both match transformers on their benchmarks.')

gallery('c033', [
    ('rep-clip.png',
     '<b>Language-aligned.</b> CLIP puts an image and its caption in one space, so a class '
     'can be named instead of labeled. Radford et al., 2021.'),
    ('rep-dinov2.jpg',
     "<b>Self-supervised.</b> The first three components of DINOv2's features, with no "
     'labels, already separate parts. Oquab et al., 2023.'),
], size='short')

gallery('c034', [
    ('rep-ijepa.png',
     '<b>Predictive.</b> I-JEPA predicts the representation of a masked region, never the '
     'pixels. Assran et al., 2023.'),
    ('rep-3dgs.jpg',
     '<b>Geometric.</b> 3D Gaussian Splatting holds a scene as explicit primitives that '
     'render in real time. Kerbl et al., 2023.'),
], size='short')

bullets('c035',
    "There is no best one. Half the hub's world models start from a frozen DINOv2 because "
    'freezing it is cheap, not because it fits their task.',
    'The choice follows the need and the budget. Language-aligned to follow instructions, '
    'geometric to plan a grasp, predictive to anticipate, and a convnet when production data '
    'is small.',
    'Read a representation paper for the downstream task it was tested on. That is the job '
    'it is good for, and often the only one.')

box('c036', 'represent')

# ---------------------------------------------------- 2.3 anticipate
h3('anticipate', '2.3 Anticipate: think before you move')

gallery('c038', [
    ('ant-peva.jpg',
     "<b>A body's world model.</b> PEVA predicts first-person video from the wearer's own 3D "
     'pose, and can render the counterfactual move. Bai et al., 2025.'),
    ('ant-worldprediction.jpg',
     '<b>The semantic side.</b> WorldPrediction tests whether a model can say which action '
     'took a scene from state A to state B, and in which order. 2025.'),
])

bullets('c039',
    'People think before they move, and often run the counterfactual first: what fails if I '
    'slice the potato instead of dicing it. Physical AI needs the same stage.',
    'The text side reasons over steps and effects. Procedural reasoning and counterfactual '
    'reasoning are the search terms, and WorldPrediction benchmarks both.',
    'The vision side is the world model, a video generator rendering the action and its '
    "effect from the actor's viewpoint. PEVA for a body, V-JEPA 2 for a robot.",
    'A person and a robot follow the prediction differently. That difference is 2.4 and 2.5.')

gallery('c042', [
    ('ant-vjepa2-flow.png',
     '<b>Video in, robot out.</b> V-JEPA 2 learns from a million hours of internet video, '
     'then 62 hours of unlabeled robot video, then picks and places on an arm in a lab it '
     'never saw. Meta, 2025.'),
], size='short')

bullets('c043',
    'Only the last 62 hours involve a robot. The planner samples actions and keeps the one '
    'whose predicted latent lands nearest the goal.',
    'Predicted futures still break physics where it can be measured. Text-to-video models '
    "fail most of PhyGenBench's 27 laws, and scale does not close the gap.")

box('c044', 'anticipate')

# -------------------------------------------------------- 2.4 decide
h3('decide', '2.4 Decide: pick one future, and say why')

gallery('c048', [
    ('dec-vlp-tree.jpg',
     '<b>Sample, score, choose.</b> Video Language Planning grows a tree of generated video '
     'futures and keeps the branch a value model scores highest. Du et al., 2023.'),
], size='short')

bullets('c049',
    'Selection is a search over imagined outcomes. Video Language Planning searches a tree '
    'of generated clips, and V-JEPA 2 samples actions and picks by predicted cost.',
    'More compute buys a better plan in both, which is the argument for keeping anticipate '
    'and decide separable even when one network does both.')

gallery('c050', [
    ('dec-satori.jpg',
     '<b>When to speak.</b> Satori models what the person believes, wants and intends, and '
     'decides on its own when to show guidance. Li et al., 2024.'),
    ('dec-vid2coach.jpg',
     '<b>What to say.</b> Vid2Coach turns a how-to video into instructions a blind cook can '
     'act on, with a completion check per step. Huh et al., 2025.'),
], label='a person')

gallery('c051', [
    ('dec-arguidance.jpg',
     '<b>How much to show.</b> AR guidance for assembly made workers 31% faster, and they '
     'made more errors. 2025.'),
], size='short')

bullets('c052',
    "For a person, deciding includes what to say and when. Satori's authors call timing the "
    'hard problem, and the AR study shows more guidance is not better.',
    "Too much and the person is overwhelmed, too little and they distrust it. A chatbot's "
    'essay followed by three options is the virtual version of the same failure.',
    'The physical version has stakes. A step near fire, electricity or a patient needs a '
    'decision the person can check before acting, with the reason attached.')

box('c053', 'decide')

# ----------------------------------------------------------- 2.5 act
h3('act', '2.5 Act: a person just acts, a robot has to be controlled')

chart('c055', 'act_by_channel', 'What the act-stage papers emit')

bullets('c056',
    "For a person, act is the easy stage. Given a good decision, they do it. The system's "
    'act is an instruction, an image or an overlay.',
    'For a robot, act is control, the chosen plan turned into joint commands at tens of '
    'hertz. All of robot learning lives in the motor-action bar.')

flow('c057', """
   <span class="yr">2022</span>  Code as Policies       the language model writes the program that calls the controller
   <span class="yr">2022</span>  RT-1                   a transformer maps camera and instruction to discrete actions
   <span class="yr">2023</span>  Diffusion Policy · ACT actions as a denoised trajectory; commit to a chunk at a time
   <span class="yr">2023</span>  RT-2                   a VLM fine-tuned to emit actions as tokens: the first VLA
   <span class="yr">2024</span>  OpenVLA · π₀           an open 7B VLA; a flow-matching action head across bodies
   <span class="yr">2025</span>  GR00T N1 · π₀.₅        a slow reasoner over a fast actor; open-world generalization
   <span class="yr">2025–26</span>  Genie Envisioner · DreamZero   world action models: predict the video and the action together
""")

bullets('c058',
    'Four branches compete: write the program, denoise the trajectory, emit action tokens '
    'from a VLM, or predict video and action together. No one knows yet which wins.',
    'Diffusion Policy beat the prior state of the art by 46.9% across 12 tasks. OpenVLA beat '
    'RT-2-X by 16.5 points with 7× fewer parameters.',
    'A world action model folds anticipate, decide and act into one network. DreamZero runs '
    '14B parameters closed-loop at 7 Hz and generalizes twice as well as VLAs.')

box('c062', 'act')

# -------------------------------------------------------- 2.6 verify
h3('verify', '2.6 Verify: close the loop on what happened')

gallery('c064', [
    ('ver-im.jpg',
     '<b>Feed the outcome back.</b> Inner Monologue hands the planner a success flag, a scene '
     "description or a person's answer after every skill. Huang et al., 2022."),
    ('ver-safe.jpg',
     "<b>Read failure off the policy.</b> SAFE finds a failure zone in a VLA's own features "
     'and alerts before the task is lost. Gu et al., 2025.'),
    ('ver-reflect.jpg',
     '<b>Explain it.</b> REFLECT summarizes what the robot sensed and asks a language model '
     'why the task failed, then replans. Liu et al., 2023.'),
], label='a robot')

bullets('c065',
    'Verify is what makes the next decision rest on what happened rather than on what was '
    'intended. Without it the loop is open, however good the policy.',
    'The robot side has had it since Inner Monologue, a check after every step and a replan. '
    'SAFE detects the failure and REFLECT explains it.')

gallery('c066', [
    ('ver-prego.png',
     '<b>Detect the mistake.</b> PREGO recognizes the current step, predicts what should come '
     'next, and flags the disagreement, trained on correct runs only. CVPR 2024.'),
    ('ver-matt.jpg',
     '<b>Attribute it.</b> Mistake Attribution says which part of the instruction was '
     'violated, the frame of no return, and where in the frame. 2025.'),
    ('ver-tpmd.jpg',
     '<b>Explain it.</b> Transparent PMD requires a rationale and scores whether the '
     'rationale entails the verdict. Storks et al., EMNLP 2025.'),
], label='a person')

bullets('c067',
    'The human side calls it mistake detection. The intervals are longer, a step rather than '
    'a motor command, and the verdict needs a reason the person will accept.',
    'The research has moved from a flag to an account of what was wrong, when it became '
    'irreversible, where in the frame, and why the system thinks so.',
    'The two literatures ask the same question at the same stage and barely cite each other.')

chart('c068', 'verify_by_embodiment', 'Verify-stage papers, by who moves the atoms')

table('c069', ['embodiment', 'papers', 'close the loop', '%'], [
    ['Human', '48', '14', '29'],
    ['Robot', '30', '23', '77'],
    ['Human+Robot', '6', '5', '83'],
    ['None', '23', '2', '9'],
    ['Simulated', '11', '9', '82'],
], caption=(
        'Who closes the loop, in the hub on 2026-09-07. A paper closes the loop when it consumes '
        'the effect of its own action at run time.'))

bullets('c070',
    '21 of the 31 verify papers watch a person. 5 watch a robot.',
    '23 of the 30 robot papers consume the effect of their own action. 14 of the 48 human '
    'ones do. Most guidance systems emit an instruction and stop.',
    'A robot policy that never looked at the result would not get published. A guidance '
    'system that never does is the norm. That gap is a project.')

box('c071', 'verify')

# --------------------------------------------------------- 2.7 adapt
h3('adapt', '2.7 Adapt: better on the next attempt because of the last one')

gallery('c073', [
    ('ada-emc.png',
     '<b>In the physical world.</b> Every Mistake Counts keeps a graph of which parts fit and '
     'what must come first, and updates it as it watches. Ding et al., 2023.'),
    ('ada-dgm.png',
     '<b>In code.</b> The Darwin Gödel Machine rewrites its own agent code and keeps the '
     'versions that score higher. Zhang et al., 2025.'),
])

gallery('c074', [
    ('ada-rsi.jpg',
     '<b>The map.</b> A July 2026 survey of 1,250 papers sorts self-improvement by what '
     'changes and how closed the loop is. Most of it is bounded self-refinement.'),
], size='tall')

bullets('c075',
    'The old name is continual learning. The new one is self-evolving AI, and it covers the '
    'harness around the model as well as its weights.',
    'The frontier labs run it on coding agents, where the loop closes cheaply. The Darwin '
    'Gödel Machine and its relatives rewrite their own code and keep what scores.',
    'The same survey finds the open-ended version bounded on every measured axis, and MIT '
    "Technology Review's August 2026 read is that it is not coming quickly.",
    'Physical AI needs it too. A guidance system that changes its next instruction because '
    'of what the last one did is this stage, and the stage is empty.')

chart('c076', 'loop_stage_counts', 'Papers per loop stage')

bullets('c077',
    '7 of 110 papers adapt. The field can tell that something went wrong and almost never '
    'learns from it while running.',
    'The exceptions are from 2023 and 2022. Every Mistake Counts updates its constraints as '
    'it watches, and Inner Monologue feeds the outcome back as text.')

box('c078', 'adapt')

flow('c014-again', """
          the physical world, objects and the changes they undergo
                    │
          <b>2.1 sense</b> │                                       ▲
                    ▼                                       │
        ┌─ model it ───────────────────────────────┐        │
        │   <b>2.2 represent</b> ──► <b>2.3 anticipate</b>       │        │  the loop of §1, with the
        └────────────────────────┬─────────────────┘        │  stage each subsection
                                 │ <b>2.4 decide</b>               │  walks written onto it
        ┌─ change it ────────────▼─────────────────┐        │
        │   <b>2.5 act</b> ──► <b>2.6 verify</b> ──► <b>2.7 adapt</b>   ├────────┘
        └──────────────────────────────────────────┘
""")

# ---------------------------------------------- §3 toward production
h2('production', 'Toward production and real-world impact')

# ----------------------------------------------- §3 the missing part
h3('missing-part', 'The missing part is data')

chart('c085', 'hours_by_domain', 'Hours of released first-person video, by domain')

table('c086', ['dataset', 'hours', 'tier', 'note', 'source'], [
    ['Ego4D', '3670', 'everyday', 'unscripted daily life', 'arXiv 2110.07058'],
    ['EgoDex', '829', 'everyday', 'tabletop manipulation with hand tracking', 'arXiv 2505.11709'],
    ['EPIC-KITCHENS-100', '100', 'everyday', 'kitchens', 'arXiv 2006.13256'],
    ['CaptainCook4D', '94.5', 'everyday', 'recipes with induced errors', 'arXiv 2312.14556'],
    ['HD-EPIC', '41', 'everyday', 'kitchens with a digital twin', 'arXiv 2502.04144'],
    ['HowToDIV', '24', 'everyday', 'clips behind generated dialogues', 'arXiv 2508.11192'],
    ['HOT3D', '13.9', 'everyday', '833 minutes of hand and object tracking', 'arXiv 2411.19167'],
    ['EgoOops', '6.8', 'everyday', 'text-following tasks with mistakes', 'arXiv 2410.05343'],
    ['HUMOTO', '2.2', 'everyday', 'mocap human-object interaction', 'arXiv 2504.10414'],
    ['Ego-Exo4D', '1286', 'skill', 'ego and exo cameras combined; 5035 takes', 'arXiv 2311.18259'],
    ['Assembly101', '513', 'industrial', '12 views of toy-vehicle assembly; 362 sequences of 7 min', 'arXiv 2203.14712'],
    ['HoloAssist', '166', 'industrial', 'instructor talks a performer through a task', 'arXiv 2309.17024'],
    ['Ego-EXTRA', '50', 'industrial', 'expert plays the assistant', 'arXiv 2512.13238'],
    ['IndustReal', '5.8', 'industrial', '84 assembly and maintenance sequences', 'arXiv 2310.17323'],
], caption=(
        "The datasets behind the bars, with each paper's own count. Assembly101's 513 hours are "
        '12 views of 362 seven-minute sequences.'))

bullets('c087',
    'About 4,800 hours of everyday life, 1,286 of skill from one dataset, 735 industrial, '
    '513 of them twelve views of toy assembly, and nothing clinical.',
    'The professional end owns the value and the intellectual property. Hospitals and '
    'factories do not release footage, so the largest record of expert guidance is 50 hours.',
    'Impact in production is a data problem before a method problem. The routes are '
    'one-demonstration learning, synthetic data, or data that never leaves the site.')

box('c088', 'the missing part')

# ------------------------------------------------- §3 build on today
h3('build-on-today', 'What you can build on today')

gallery('c090', [
    ('act-pi07.jpg',
     '<b>For a robot, π₀.₇</b>, Physical Intelligence, April 2026. Follows instructions in '
     'kitchens it never saw and folds laundry on a robot that never trained on it. '
     "<a href='https://www.pi.website/blog/pi07'>blog</a> · "
     "<a href='https://arxiv.org/abs/2604.15483'>arXiv</a>"),
    ('sota-pro2assist.jpg',
     '<b>For a person, Pro²Assist</b>, May 2026. Tracks step progress from AR-glasses sensing '
     'and decides when to help, through a whole procedure. '
     "<a href='https://arxiv.org/abs/2605.04227'>arXiv</a>"),
])

bullets('c091',
    'Two links, one per embodiment, to the latest thing you can start from.',
    'Both are stacks of 2.1 to 2.5, and the robot one is a product. Neither adapts.')

box('c092', 'build on today')

# --------------------------------------------- §4 where to look next
h2('look-next', 'Where to look next')

table('g001', ['stage', 'search for', 'start with'], [
    ['2.1 sense', 'egocentric video, smart glasses, tactile sensing', 'SAM 2, HOT3D'],
    ['2.2 represent', 'representation learning, self-supervised learning, JEPA', 'DINOv2, 3D Gaussian Splatting'],
    ['2.3 anticipate', 'world models, procedural reasoning, counterfactual reasoning', 'V-JEPA 2, Genie'],
    ['2.4 decide', 'task planning with language models, video language planning, proactive AR assistants', 'SayCan, VLaMP'],
    ['2.5 act', 'vision-language-action models, diffusion policy, world action models', 'π₀, ShowHowTo'],
    ['2.6 verify', 'mistake detection, failure detection', 'PREGO, SAFE'],
    ['2.7 adapt', 'continual learning, self-evolving AI', 'Every Mistake Counts, Inner Monologue'],
], cls="k")

bullets('g002',
    'Each row is one stage: the words to search for, and two papers to start with.',
    'Resource hub and these slides: '
    '[github.com/yayuanli-org/awesome-physical-ai](https://github.com/yayuanli-org/awesome-physical-ai).',
    "New to the field? The hub's "
    '[must-read list for students](https://yayuanli-org.github.io/awesome-physical-ai/#must-read/student) '
    'is four papers, each one part of a vision-language-action model.')


# ================================================================== write
HEAD = """<!doctype html>
<html lang="en" data-comment-doc="{doc}" data-comment-root="#content">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Where Physical AI Stands · EMU guest lecture</title>
<link rel="stylesheet" href="comment-layer.css">
<link rel="stylesheet" href="toc-layer.css">
<link rel="stylesheet" href="cite-layer.css">
<link rel="stylesheet" href="present-layer.css">
<link rel="stylesheet" href="page.css">
</head>
<body>
<!-- Built by build.py. Edit build.py and rebuild: edits made here are overwritten. -->
<main id="content">
"""

TAIL = """
</main>
<script src="comment-layer.js"></script>
<script src="toc-layer.js"></script>
<script src="cite-layer.js"></script>
<script src="present-layer.js"></script>
</body>
</html>
"""

NOTE = "<!-- Generated by page/build.py. Edit that file and rebuild, not this one. -->"


def main() -> None:
    page = "\n\n".join(p for p, _ in BLOCKS)
    ids = re.findall(r' id="([^"]+)"', page)
    dup = sorted({i for i in ids if ids.count(i) > 1})
    assert not dup, f"two blocks share an id, and comments would attach to the wrong one: {dup}"
    missing = [s for s in re.findall(r'src="(assets/[^"]+)"', page) if not (HERE / s).exists()]
    assert not missing, f"files the page shows but this folder lacks: {missing}"

    PAGE.write_text(HEAD.format(doc=DOC_ID) + page + TAIL, encoding="utf-8")
    README.write_text(NOTE + "\n\n" + "\n\n".join(r for _, r in BLOCKS) + "\n", encoding="utf-8")
    print(f"wrote {PAGE.name} ({PAGE.stat().st_size // 1024} KB) and ../{README.name} "
          f"({README.stat().st_size // 1024} KB): {len(BLOCKS)} blocks, {len(UNITS)} units in the map")


if __name__ == "__main__":
    main()
