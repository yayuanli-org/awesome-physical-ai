"""Debate 1, From virtual to physical AI: the cells that close §5 of Lecture 2.

Imported by build_doc.py (the seed). Three units in the lecture's slide format: the
question (two core papers and three field questions), what to read (the two papers,
one fundamental paper per loop stage, three talks), and the prompts (three motions
per paper on PACES claim, substantiation and approach, then three on the field).
Every number comes from the paper it is attributed to or from the hub's checked copy.
"""
from __future__ import annotations


def debate1(md, flow, bullets, box, gallery) -> None:
    # ---------------------------------------------------------------- the question
    md("### Debate 1 · From virtual to physical AI")

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
        "The loop that changed the virtual world, think, act, read the result, repeat, "
        "breaks in three places once it has a body: the state, the act, the check.",
        "Two core papers, one per side. ReAct runs the loop in a house made of text, and "
        "Ego-Exo4D films 1,286 hours of skilled work to ask what a model must see.",
        "Three questions for the room: why physical AI beyond virtual, when it is needed and "
        "where the boundary sits, and what is technically different.",
    )

    gallery([
        ("deb-react.png", "<b>ReAct</b>, ICLR 2023. A thought, an action and the observation "
                          "alternate in one token stream. Every valid action works."),
        ("deb-egoexo.jpg", "<b>Ego-Exo4D</b>, CVPR 2024. The same skilled activity from the "
                           "doer's eyes and from outside, with an expert narrating the mistakes."),
    ], cols=2)

    bullets(
        "ReAct uses three examples per task type and no training, and reaches 71% on ALFWorld "
        "with its best prompt, 57% on average, 34 points above the trained baseline.",
        "Ego-Exo4D has 5,035 takes from 740 participants in 123 scenes and 13 cities, and four "
        "benchmark families whose baselines the paper calls far from solved.",
        "Write the five PACES rows for both before you pick a side. The prompts below assume "
        "you did.",
    )
    box("debate 1")

    # ---------------------------------------------------------------- what to read
    md("### Debate 1 · What to read")

    md('''
<table class="k wide plain">
<thead><tr><th>core paper</th><th>its role here</th><th>read</th><th>pages</th></tr></thead>
<tbody>
<tr><td>ReAct: Synergizing Reasoning and Acting in Language Models. Yao et al., ICLR 2023.
    <a href="https://arxiv.org/abs/2210.03629">arXiv</a></td>
    <td>The loop with no body, in a house made of text</td>
    <td>Sections 1, 2 and 4, and one ALFWorld trajectory from Appendix D.2</td>
    <td>~8</td></tr>
<tr><td>Ego-Exo4D: Understanding Skilled Human Activity from First- and Third-Person
    Perspectives. Grauman et al., CVPR 2024.
    <a href="https://arxiv.org/abs/2311.18259">arXiv</a> ·
    <a href="http://ego-exo4d-data.org/">site</a></td>
    <td>The body, filmed from inside and outside at once, with an expert's verdict on it</td>
    <td>Section 1, Section 3 up to the participants, Section 4.1 on expert commentary, and
    Section 5 with its result tables</td>
    <td>~9</td></tr>
</tbody></table>
''')

    bullets(
        "ReAct is short and the trajectory in the appendix is the paper. Read one end to end "
        "and count how many observations the environment handed over for free.",
        "Ego-Exo4D is a dataset paper, so the evidence is in Section 5's tables. Read them "
        "asking how far each baseline is from a coach you would use.",
    )

    md('''
<table class="k wide plain">
<thead><tr><th>one paper per stage</th><th>why this one</th><th>read</th></tr></thead>
<tbody>
<tr><td>sense · SAM 2. Ravi et al., ICLR 2025.
    <a href="https://arxiv.org/abs/2408.00714">arXiv</a></td>
    <td>Object identity over time from a stream, the cheapest sensing primitive most
    pipelines in the hub rely on</td>
    <td>The model figure with the streaming memory, and the video results table</td></tr>
<tr><td>represent · DINOv2. Oquab et al., TMLR 2024.
    <a href="https://arxiv.org/abs/2304.07193">arXiv</a></td>
    <td>The frozen features half the hub's world models start from</td>
    <td>The data curation section and the first results table</td></tr>
<tr><td>anticipate · V-JEPA 2. Assran et al., 2025.
    <a href="https://arxiv.org/abs/2506.09985">arXiv</a></td>
    <td>A world model learned from a million hours of video that plans on a robot with
    62 hours of unlabeled robot video</td>
    <td>The overview figure, the action-conditioned section, and the real-robot table</td></tr>
<tr><td>decide · SayCan. Ahn et al., CoRL 2022.
    <a href="https://arxiv.org/abs/2204.01691">arXiv</a></td>
    <td>Language scores what is useful, a value function scores what is possible, and the
    ablation prices the body at 17 points of plan success</td>
    <td>The scoring rule and Table 2</td></tr>
<tr><td>act · π₀. Black et al., RSS 2025.
    <a href="https://arxiv.org/abs/2410.24164">arXiv</a></td>
    <td>The reference robot foundation model, a flow-matching action head on a VLM and one
    policy across single-arm, dual-arm and mobile platforms</td>
    <td>The model section and the laundry-folding evaluation</td></tr>
<tr><td>verify · PREGO. Flaborea et al., CVPR 2024.
    <a href="https://arxiv.org/abs/2404.01933">arXiv</a></td>
    <td>Online mistake detection trained on correct executions only, the setting the human
    side of verify reports against</td>
    <td>The two-branch figure and the online protocol. §4 of this lecture has its PACES</td></tr>
<tr><td>adapt · Inner Monologue. Huang et al., CoRL 2022.
    <a href="https://arxiv.org/abs/2207.05608">arXiv</a></td>
    <td>The outcome fed back to the planner as text, 50% to 75% with the loop closed, and one
    of seven hub papers that adapt at all</td>
    <td>Method, experiments and the limitations paragraph</td></tr>
</tbody></table>
''')

    bullets(
        "Seven papers, one per stage, each the one to cite if you could cite only one. Skim "
        "the figure and the main table of each.",
        "Every one is in the hub with its PACES already written. Disagree with a cell there "
        "and that is a contribution, see §6.",
    )

    md('''
<table class="k wide plain">
<thead><tr><th>talk</th><th>why</th><th>where</th></tr></thead>
<tbody>
<tr><td>Fei-Fei Li, Justin Johnson and Ben Mildenhall with Martin Casado, "The Race to Build
    World Models for AI", The a16z Show, 4 Sep 2026, 45 min</td>
    <td>The day after World Labs launched Atlas: why predicting a new view of a scene might be
    to spatial intelligence what next-token prediction was to language, and why robotics is
    data-bound</td>
    <td><a href="https://podcasts.apple.com/us/podcast/fei-fei-li-the-race-to-build-world-models-for-ai/id842818711?i=1000787830626">Apple Podcasts</a></td></tr>
<tr><td>Karol Hausman, CEO of Physical Intelligence, "Why Robots Still Struggle With Simple
    Tasks", The Generalist, 17 Mar 2026</td>
    <td>The robot side from the company that ships π₀: what a robot foundation model is, and
    what still breaks</td>
    <td><a href="https://www.generalist.com/p/karol-hausman-physical-intelligence">The Generalist</a></td></tr>
<tr><td>Kristen Grauman, keynote at ECCV 2026, Thu 10 Sep 2026, 15:00 CEST</td>
    <td>The human side from Ego-Exo4D's lead: an AI guide that learned from video, anticipates
    the effect of your action, and tells you what to change. If you cannot attend, her 2025
    talk covers the same program</td>
    <td><a href="https://eccv.ecva.net/virtual/2026/invited-talk/6075">ECCV</a> ·
    <a href="https://www.youtube.com/watch?v=ggJOYPdwJt8">2025 talk</a></td></tr>
</tbody></table>
''')

    bullets(
        "Three voices, one per week night. Li for world models, Hausman for the robot, "
        "Grauman for the person.",
        "Listen for the boundary. Each of them says where their approach stops working, and "
        "that sentence is debate material.",
    )
    box("what to read")

    # ---------------------------------------------------------------- the prompts
    md("### Debate 1 · Prompts")

    md('''
Each prompt is a motion one side defends, the evidence either side can reach for from the
readings, and the question that settles it. On each paper the three follow PACES: the claim,
its substantiation, the approach. The last three are about the field.
''')

    def motion(tag, title, motion, for_, against, settle):
        md(f'''
<div class="callout note"><span class="t">{tag} · {title}</span>
<p><b>Motion.</b> {motion}</p></div>
<div class="pair">
<div><span class="t">for</span>{for_}</div>
<div><span class="t">against</span>{against}</div>
</div>

Settle it. {settle}
''')

    motion("R1", "ReAct, the claim",
           "ALFWorld is a physical task with the physics deleted, and that deletion is why "
           "ReAct works.",
           "The environment hands over the three things the figure above says the body "
           "breaks. The state arrives as a sentence, every valid action succeeds, and the "
           "episode ends with a symbolic check. Remove any one and 71% says nothing about a "
           "kitchen.",
           "ALFWorld keeps the part of the problem a language model solves: where a desk lamp "
           "is likely to be and what to do next. SayCan's ablation prices that prior at 17 "
           "points of plan success, and it is the prior every physical planner in the hub "
           "inherits.",
           "Map each free thing to a physical number. The state: SayCan's 84% falls to 67% "
           "without the value function. The act: ACT needs action chunking to reach 80 to 90% "
           "from ten minutes of demonstrations. The check: Inner Monologue's 50% falls to 12.5% "
           "when a person disturbs the scene.")

    motion("R2", "ReAct, the substantiation",
           "The claim rests on the average of six prompts, 57%, and the paper leads with the "
           "best, 71%.",
           "Prompt selection is a hyperparameter the baseline did not get to tune. A trained "
           "agent reports one number, and a prompted one reports the best of six.",
           "Both numbers beat the trained baseline by a wide margin, 34 points on the paper's "
           "own headline, and the average is the number the paper reports in its table.",
           "Rerun the comparisons with the average. Which survive, and does the +34 headline?")

    motion("R3", "ReAct, the approach",
           "Interleaving a thought and an action retrieves a plan from pretraining. It does "
           "not reason.",
           "Three examples per task type and no training. Performance tracks how familiar the "
           "environment's vocabulary is, and a household is the most familiar place on the "
           "internet.",
           "The thoughts change with the observation, which retrieval would not. ReAct-IM, "
           "the variant with Inner Monologue's fixed feedback format and no free-form thought, "
           "does worse.",
           "Design the experiment that separates the two. Swap the object names for nonsense "
           "words and predict whether the loop still closes.")

    motion("E1", "Ego-Exo4D, the claim",
           "Skill is visible only from both views at once: a model trained on the ego view "
           "alone cannot learn what the expert commentary points at.",
           "The commentary talks about posture, force and rhythm, which the head camera "
           "cannot see on its own body. The ego-exo relation family is the least solved of "
           "the four benchmarks.",
           "Every guidance system in the hub runs on one camera at test time, the one on the "
           "head. If the outside view is needed to learn, it has to be distilled away, and "
           "the paper does not show that transfer.",
           "Find the benchmark where the outside view is present at training and absent at "
           "test. If the paper never runs it, say what it would take to.")

    motion("E2", "Ego-Exo4D, the substantiation",
           "1,286 hours substantiate a dataset claim. The skill-learning claim rests on the "
           "baselines, and they are far from usable.",
           "The paper calls itself a foundational dataset and reports its baselines across "
           "four families as far from solved, cross-view tasks least of all.",
           "A dataset paper is substantiated by what gets built on it. ExpertAF and "
           "SkillFormer already estimate proficiency and generate feedback from it, and both "
           "are in the hub.",
           "Take the proficiency-estimation table. Is the best number above a majority-class "
           "guess by more than two annotators disagree with each other?")

    motion("E3", "Ego-Exo4D, the approach",
           "Breadth, eight scenario types in thirteen cities, was the wrong way to spend "
           "1,286 hours. Depth on one skill would have produced a usable coach sooner.",
           "A coach needs many examples of the same mistake. 5,035 takes over eight domains "
           "is a few hundred takes per skill and a handful per mistake type.",
           "Failing to generalize across sites is the failure mode of every earlier egocentric "
           "dataset, and Ego4D's lesson. Depth on one skill in one city would repeat it.",
           "Read the takes-per-scenario distribution in Section 3.2 and decide whether you "
           "would train a bike-repair coach on that count.")

    motion("F1", "why physical AI at all",
           "A virtual agent with a camera feed is already physical AI. The body adds nothing "
           "in kind, only in degree.",
           "The industry definition is sensors plus a model. RT-2 gets web knowledge into a "
           "gripper by writing actions as tokens, the same trick that makes a chatbot.",
           "Sutton's in-principle case: a model with no goal and no ground truth is never "
           "surprised. The check is a second perception problem: 98% on the brick, 40% on "
           "the state of the assembly (LEGO Co-builder).",
           "Name one capability a physical agent can have that no virtual agent can have in "
           "principle, and one that is only a matter of scale.")

    motion("F2", "when it is needed, and where the boundary sits",
           "Most of the time words are enough. The loop earns its cost in three cases and "
           "not otherwise.",
           "A recipe is text, and people cook from it. AR guidance made assemblers 31% faster "
           "and made them make more errors.",
           "When the person cannot read the state: Vid2Coach, blind cooks, 58.5% fewer "
           "errors. When the timing matters: Satori's authors call deciding when to speak the "
           "hard problem. When a mistake is expensive: the professional end of §3.",
           "Draw a two-by-two: the state readable by the person or not, a mistake cheap or "
           "expensive. Place ReAct, Ego-Exo4D's coaching, Vid2Coach and a surgical assistant "
           "in it.")

    motion("F3", "what is technically different",
           "The three breaks, the state, the act, the check, are each a perception problem "
           "in disguise.",
           "The state is seen through a moving camera and third-person detectors collapse "
           "from it (Ego-HOIBench). The check is perception again: 98% against 40%.",
           "The act break is control, not perception. ALOHA's action chunking exists because "
           "errors compound across steps, and a cut does not undo. No camera fixes that.",
           "For each break, name the hub paper that attacks it and the number that says how "
           "far it is from solved.")

    box("prompts")
