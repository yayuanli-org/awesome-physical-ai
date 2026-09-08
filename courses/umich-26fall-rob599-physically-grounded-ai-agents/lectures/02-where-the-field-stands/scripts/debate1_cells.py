"""Debate 1, From virtual to physical AI: the cells that close §5 of Lecture 2.

Imported by build_doc.py (the seed). One block per cell, in the lecture's slide
format: a table, two to four bullets, and a map box at the end of each of the four
parts (the question, what to read, the recap, the prompts). Every number was checked
against the paper's own text, not the hub's copy of it.
"""
from __future__ import annotations


def debate1(md, flow, bullets, box) -> None:
    # ---------------------------------------------------------------- the question
    md("### Debate 1 · From virtual to physical AI")

    md('''
> [C] on debate 1
>
> [C] **ai:** Four calls are yours: the core pair (Inner Monologue as drafted, or SayCan, whose ablation is cleaner but whose loop is thinner), the podcast (Sutton for the in-principle case, Levine for the practitioner's numbers), the fourth side unit (RT-2 for web-to-robot transfer, HoloAssist for guiding a person), and which four motions to run, with R1, I1, F2 and F3 marked.
''')

    flow('''
     Bisk 2020   WS2 internet ─────────► WS3 perception ─────────► WS4 embodiment
                 "virtual AI"                                      "physical AI"

     core        ReAct (ICLR 2023)                  Inner Monologue (CoRL 2022)
                 a house made of text, ALFWorld     a real kitchen, feedback typed back as text
                 0 training, 3 examples per type    frozen PaLM, one learned success detector
                 71% best / 57% average             50% → 75% with the loop closed
                                                    12.5% → 33% when a person disturbs the scene

     side        SayCan: the body's price list. 551 skills, 68k demos, 84% → 67% without grounding
                 Bisk: the ladder · Sutton: why text is not enough · RT-2: 9% → 42% → 44%

     prompts     R1–R3 on ReAct    I1–I3 on Inner Monologue    F1–F4 on the field
''', bold=("ReAct (ICLR 2023)", "Inner Monologue (CoRL 2022)"))

    bullets(
        '"AI is going from virtual to physical" sounds obvious and is hard to make precise. '
        "Where is the line, and what does crossing it cost?",
        "The two core papers run the same loop on either side of the line, ReAct in a house "
        "made of text and Inner Monologue in a real kitchen.",
        "§2 said the body breaks the loop at the state, the act and the check. This debate is "
        "whether that holds.",
        "Ten motions follow. For one session, run R1, I1, F2 and F3.",
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
    <td>Sections 1, 2, 4, and one ALFWorld trajectory from Appendix D.2</td>
    <td>~8</td></tr>
<tr><td>Inner Monologue: Embodied Reasoning through Planning with Language Models. Huang et
    al., CoRL 2022. <a href="https://arxiv.org/abs/2207.05608">arXiv</a></td>
    <td>The same loop with a body, closed by writing perception down as text</td>
    <td>Method, experiments and the limitations paragraph. Skip the intro and related work</td>
    <td>~9</td></tr>
</tbody></table>
''')

    bullets(
        "ReAct alternates a thought, an action and the observation in one token stream, in a "
        "text house where every valid action works. Three examples per task type, no training.",
        "Inner Monologue keeps the frozen planner and hands the world back as text after each "
        "skill, as a success flag, an object list, and a person's answer.",
        "In simulation every feedback signal is ground truth, and in the kitchen a person "
        "types the object list, so the only learned perception in the headline is the success "
        "detector.",
    )

    md('''
<table class="k wide plain">
<thead><tr><th>side unit</th><th>for</th><th>read</th></tr></thead>
<tbody>
<tr><td>Do As I Can, Not As I Say: Grounding Language in Robotic Affordances. Ahn et al.,
    CoRL 2022. <a href="https://arxiv.org/abs/2204.01691">arXiv</a> ·
    <a href="https://say-can.github.io/">site</a></td>
    <td>The paper Inner Monologue builds on, and the price list for a body. 551 skills from
    68,000 demonstrations, and plan success falls from 84% to 67% when the value function
    is removed</td>
    <td>The scoring rule and Table 2, ~4 pages</td></tr>
<tr><td>Bisk et al., Experience Grounds Language, EMNLP 2020.
    <a href="https://arxiv.org/abs/2004.10151">arXiv</a></td>
    <td>The vocabulary. Five World Scopes: corpus, internet, perception, embodiment, social.
    "Virtual AI" is scope 2 and "physical AI" is scope 4</td>
    <td>All, ~8 pages</td></tr>
<tr><td>Dwarkesh Podcast, "Richard Sutton – Father of RL thinks LLMs are a dead end",
    26 Sep 2025, 66 min. <a href="https://www.dwarkesh.com/p/richard-sutton">link</a></td>
    <td>The case that a virtual model is missing something in kind, not in degree. No goal,
    no ground truth, never surprised</td>
    <td>The whole episode, or the first ten minutes</td></tr>
<tr><td>RT-2: Vision-Language-Action Models Transfer Web Knowledge to Robotic Control.
    Brohan et al., CoRL 2023. <a href="https://arxiv.org/abs/2307.15818">arXiv</a></td>
    <td>The one controlled measurement of how much web knowledge crosses into physical
    action</td>
    <td>Experiments section and Tables 6 to 8, ~5 pages</td></tr>
</tbody></table>
''')

    bullets(
        "Each side unit is there for one reason: the price list, the vocabulary, the "
        "in-principle case, the one controlled transfer measurement.",
        "If the group leans the other way, Levine's episode (Dwarkesh Podcast, 12 Sep 2025) "
        "is the practitioner's version, with its numbers in the recap.",
        "HoloAssist (ICCV 2023), 166 hours of a remote instructor talking a first-person "
        "performer through a task, replaces RT-2 if the group cares more about guiding people.",
        "Cosmos and the CES 2025 keynote are not assigned. The one sentence they add is in "
        "the recap.",
    )

    box("reading")

    # ---------------------------------------------------------------- the recap
    md("### Debate 1 · The recap, ten minutes")

    md('''
<table class="k wide plain">
<thead><tr><th>the definition, by</th><th>what it says</th></tr></thead>
<tbody>
<tr><td>industry: <a href="https://arxiv.org/abs/2501.03575">Cosmos</a>, NVIDIA, Jan 2025</td>
    <td>"Physical AI is an AI system equipped with sensors and actuators: the sensors allow it
    to observe the world, and the actuators allow it to interact with and modify the world."
    Huang at CES 2025 named the eras perception AI, generative AI, now physical AI, and said
    "the ChatGPT moment for general robotics is just around the corner."</td></tr>
<tr><td>the hub</td>
    <td>Physical AI studies how the physical world gets changed in the age of AI. Model the
    world, change it through an embodiment, and since acting changes what has to be modeled,
    the two close into a loop. Virtual, in the hub's columns, is embodiment <code>none</code>
    or <code>sim</code>.</td></tr>
<tr><td>the ladder: Bisk et al. 2020</td>
    <td>WS1 corpus, WS2 internet, WS3 perception, WS4 embodiment, WS5 social. "Most trending
    work in NLP operates in the second." "You can't learn language from the radio."</td></tr>
</tbody></table>
''')

    bullets(
        "Enough to argue from if nobody read anything. Every number comes from the source "
        "beside it.",
        "All three definitions put sensors on the way in and a changed world on the way out. "
        "They differ on where the line is.",
    )

    md('''
<table class="k narrow plain">
<thead><tr><th>who moves the atoms (110 papers, 2026-09-07)</th><th>papers</th><th>of which close the loop</th></tr></thead>
<tbody>
<tr><td>a person, guided or observed</td><td>46</td><td>14</td></tr>
<tr><td>a robot</td><td>23</td><td>19</td></tr>
<tr><td>nothing</td><td>22</td><td>1</td></tr>
<tr><td>a simulated body</td><td>7</td><td>6</td></tr>
<tr><td>person and robot together</td><td>4</td><td>3</td></tr>
<tr><td>mixed tags</td><td>8</td><td>5</td></tr>
</tbody></table>
''')

    bullets(
        "Of the 22 papers with no body, one closes the loop. Of the 23 robot papers, 19 do.",
        "Language is the representation in 56 of the 110. Half of physical AI, as this hub has "
        "it, thinks in words.",
    )

    md('''
<table class="k wide plain">
<thead><tr><th></th><th>ReAct, ALFWorld</th><th>Inner Monologue, real kitchen</th></tr></thead>
<tbody>
<tr><td>world</td><td>134 unseen text games, 6 task types</td>
    <td>8 instructions in 3 families, 120 evaluations in total</td></tr>
<tr><td>state</td><td>a sentence listing what is here</td>
    <td>a list of visible objects, typed by a person</td></tr>
<tr><td>action</td><td>a sentence. Valid ones always work</td>
    <td>one of SayCan's skills, run by a learned policy, replanned after each</td></tr>
<tr><td>success signal</td><td>the game returns it</td>
    <td>a learned success detector reads the before and after images</td></tr>
<tr><td>planner</td><td>PaLM-540B, frozen, 3 example trajectories per task type</td>
    <td>PaLM-540B, frozen, no training</td></tr>
<tr><td>result</td><td>71% best prompt, 57% average, 45% without thoughts, 37% BUTLER</td>
    <td>50.0% open loop, 75.0% closed. Disturbed: 12.5% and 33.3%</td></tr>
<tr><td>the ablation that matters</td>
    <td>the worst ReAct prompt, 48%, still beats the best without thoughts, 45%</td>
    <td>success detection alone gives 62.5% and 25.0%. Adding the object list gives the
    rest</td></tr>
</tbody></table>
''')

    bullets(
        "The same frozen planner on both sides. What differs is where the state, the action "
        "and the success signal come from.",
        "Thoughts are worth 3 to 26 points in the text house. The success detector and the "
        "object list are worth 12.5 points each in the kitchen.",
    )

    md('''
<table class="k wide plain">
<thead><tr><th>source</th><th>the numbers</th></tr></thead>
<tbody>
<tr><td>Inner Monologue in simulation. All feedback is ground truth, 50 episodes per task
    with disturbances</td>
    <td>Pick and place: policy alone 24%, with the object list 80%, plus success detection
    90%, plus a progress description 94%. Stack all blocks: 2%, 4%, 10%, 26%. On the four
    unseen tasks the policy alone scores 0%. Real tabletop, 10 runs each: 45% with the
    object list, 90% with success detection added</td></tr>
<tr><td>SayCan, 101 instructions</td>
    <td>Mock kitchen: plan 84%, execution 74%. Real kitchen: 81% and 60%. Without the value
    function, plan success 67%. Behind the 551 skills: 68,000 teleoperated demonstrations
    over 11 months on 10 robots, plus 12,000 successful autonomous episodes filtered from
    276,000. Weakest family, queries about the robot's own state: 64% plan, 55% execution.
    Two new drawer skills over 21 queries: plan 100%, execution 33%</td></tr>
<tr><td>RT-2, generalization to unseen objects and scenes</td>
    <td>5B model: trained from scratch 9%, web-pretrained then fine-tuned on robot data 42%,
    co-fine-tuned on web and robot data 44%. At 55B, co-fine-tuning 63% against fine-tuning
    52%. Overall unseen 62% against RT-1's 32%, over 6,000 real trials. Robot data from 13
    robots over 17 months</td></tr>
<tr><td>the cost of a body</td>
    <td>Levine, Sep 2025: robot datasets one to two orders of magnitude smaller than
    vision-language corpora, under 100,000 arms in the world of the kind you could train on,
    an arm $400,000 in 2014 and $3,000 now, and his median guess for household autonomy five
    years out. Cosmos: "these actions perturb the physical world and may cause severe damage
    to the system and the world"</td></tr>
<tr><td>guiding a person</td>
    <td>HoloAssist, 166 hours, 2,221 sessions, 222 participants: the remote instructor
    watched the performer's first-person video throughout, and about 6% of fine-grained
    actions were mistakes. Vid2Coach: 58.5% fewer errors for eight blind and low-vision
    cooks against their usual workflow. One AR assembly study: 31% faster and a higher
    error rate</td></tr>
<tr><td>Moravec, 1988</td>
    <td>"It is comparatively easy to make computers exhibit adult level performance on
    intelligence tests or playing checkers, and difficult or impossible to give them the
    skills of a one-year-old when it comes to perception and mobility"</td></tr>
</tbody></table>
''')

    bullets(
        "Every feedback channel added to Inner Monologue adds success, most where the policy "
        "alone is worst: 24% to 94% on pick and place.",
        "The body's price is data, hardware and damage: 68,000 demonstrations for 551 skills, "
        "under 100,000 trainable arms, and an action that does not undo.",
    )

    md('''
<table class="k wide plain">
<thead><tr><th>who, when</th><th>the quote</th></tr></thead>
<tbody>
<tr><td>Richard Sutton, Sep 2025</td>
    <td>"Large language models are about mimicking people, doing what people say you should
    do. They're not about figuring out what to do."</td></tr>
<tr><td>Sutton again</td>
    <td>"There's no ground truth in large language models because you don't have a prediction
    about what will happen next."</td></tr>
<tr><td>Fei-Fei Li, Nov 2025</td>
    <td>Today's models are "eloquent but inexperienced, knowledgeable but ungrounded."</td></tr>
</tbody></table>
''')

    bullets(
        "Sutton's two make the in-principle case, that a virtual model has no goal, no ground "
        "truth, and is never surprised. Li's is the same point, from vision.",
    )

    box("recap")

    # ---------------------------------------------------------------- prompts: ReAct
    md("### Debate 1 · Prompts on ReAct")

    md('''
Each prompt is a motion one side defends, the evidence either side can reach for from the
readings, and the question that settles it. On each paper the first is about the claim and
its substantiation, the second about the approach, the third about the evaluation.
''')

    md('''
<div class="callout note"><span class="t">R1 · claim and substantiation</span>
<p><b>Motion.</b> ALFWorld is a physical task with the physics deleted, and that deletion is
why ReAct works.</p></div>
''')

    md('''
<div class="pair">
<div><span class="t">for</span>The environment hands over the three things §2 says the body
breaks. The state arrives as a sentence, every valid action succeeds, and the task ends with
a symbolic check. Remove any one and the 71% says nothing about a kitchen.</div>
<div><span class="t">against</span>ALFWorld keeps the part of the problem the language model
actually solves. A task can have more than 50 locations and need more than 50 steps, and the
agent has to guess where a desk lamp is likely to be. That prior is what SayCan's planner
contributes, and SayCan's ablation prices it at 67 points of plan success on its own.</div>
</div>
''')

    md('''
Settle it. Of the three free things, which costs the physical papers the most? Map each to a
number: the state to SayCan's 84% falling to 67% without the value function, the act to
SayCan's 84% plan against 74% execution (81% against 60% in the real kitchen), the check to
Inner Monologue's 50.0% falling to 12.5% under disturbance.
''')

    md('''
<div class="callout note"><span class="t">R2 · approach</span>
<p><b>Motion.</b> ReAct's gains are prompt luck, and the six-prompt spread proves it.</p></div>
''')

    md('''
<div class="pair">
<div><span class="t">for</span>Best prompt 71%, average 57%, and the six prompts differ only
in which two of the three annotated examples they include and in what order. On the
question-answering benchmark ReAct loses to plain chain-of-thought, 27.4 to 29.4.</div>
<div><span class="t">against</span>The worst ReAct prompt, 48%, still beats the best
action-only prompt, 45%. The failure analysis shows a change in kind: hallucination is 56%
of chain-of-thought failures and 0% of ReAct's, at the price of reasoning errors rising
from 16% to 47%.</div>
</div>
''')

    md('''
Settle it. Is "acting" in ReAct a grounding mechanism, like SayCan's value function, or a
retrieval mechanism? The 0% hallucination number is the cleanest hint in either paper of what
a world does for a language model. Say what the same effect would look like in a kitchen.
''')

    md('''
<div class="callout note"><span class="t">R3 · evaluation</span>
<p><b>Motion.</b> ReAct-IM settles the format question, and the robot papers picked the wrong
one.</p></div>
''')

    md('''
<div class="pair">
<div><span class="t">for</span>ReAct-IM copies Inner Monologue's style, which the ReAct
authors describe as "limited to observations of the environment state and what needs to be
completed by the agent", and scores 53% against ReAct's 71%. Free-form thought wins on five
of six task types. ReAct-IM "often made mistakes in identifying when subgoals were
finished", the exact job Inner Monologue gives a success detector.</div>
<div><span class="t">against</span>In the kitchen the structured reports are what lifted
Inner Monologue from 12.5% to 33.3% under disturbance. ReAct never met a disturbance,
because ALFWorld has none, and its "observation" is the whole state. The comparison is
between a format and a world.</div>
</div>
''')

    md('''
Settle it. Design the experiment that separates the two. What would ReAct's thoughts look
like if a person removed the object it had just picked up, and what would Inner Monologue's
success detector have to say for the planner to recover?
''')

    # ---------------------------------------------------------------- prompts: Inner Monologue
    md("### Debate 1 · Prompts on Inner Monologue")

    md('''
<div class="callout note"><span class="t">I1 · claim and substantiation</span>
<p><b>Motion.</b> The headline kitchen result is a human-in-the-loop result, and the
closed-loop claim is only shown with perception from the simulator.</p>
<p>The claim under debate: "Closed-loop language feedback significantly improves high-level
instruction completion on three domains, including simulated and real table top
rearrangement tasks and long-horizon mobile manipulation tasks in a kitchen environment in
the real world."</p></div>
''')

    md('''
<div class="pair">
<div><span class="t">for</span>In simulation every feedback signal comes from the simulator,
and the paper says so: "We assume access to oracle scene descriptors." In the kitchen the
object list is human-provided. The one learned module, the success detector, is the paper's
first named failure mode: false negatives cause extra retries and false positives "add
adversarial partial observability." The planner also sometimes "ignored the environment
feedback."</div>
<div><span class="t">against</span>The success detector alone carries the "check" break, and
it alone lifts 50.0% to 62.5% and 12.5% to 25.0%. Human object recognition stands in for a
detector that existed at the time and bounds what perception could give, which is how you
isolate a planner. The claim is about what a planner does with feedback, and the ablations
hold that fixed.</div>
</div>
''')

    md('''
Settle it. The hub's `embodiment` column tags Inner Monologue both `robot` and
`human+robot`. Which tag does the kitchen result earn, given that the perception runs through
a person's eyes? A robot paper, a human-plus-robot paper, or a virtual-AI paper with an
excellent sensor?
''')

    md('''
<div class="callout note"><span class="t">I2 · approach</span>
<p><b>Motion.</b> Writing every feedback signal down as a sentence is the right interface
between a virtual brain and a physical body.</p></div>
''')

    md('''
<div class="pair">
<div><span class="t">for</span>Nothing in the planner is trained. The same frozen model runs
the tabletop and the kitchen, and each added channel adds success in simulation: 80%, 90%,
94% on pick and place. The behaviors the paper calls emergent, asking a person a question,
proposing a new goal when the old one is infeasible, taking instructions in another
language, come free because the channel is language.</div>
<div><span class="t">against</span>A sentence drops geometry. "Stack all blocks" stays at 4%,
10%, 26% with simulator feedback, because "the red block is on the blue block" carries no
pose and no tolerance. ReAct shows the report format costs reasoning, 53% against 71%. And
the paper's own failure list ends with the planner ignoring what it was told, which no
channel can prevent.</div>
</div>
''')

    md('''
Settle it. Name the first feedback signal that cannot be written as a sentence without losing
what the planner needs. Force, pose, timing, contact? Wherever that is, virtual AI plus a
text channel stops and physical AI starts.
''')

    md('''
<div class="callout note"><span class="t">I3 · evaluation</span>
<p><b>Motion.</b> The disturbance protocol is the only physical-AI evaluation in these
readings, and every paper in the hub's change arc should be required to run one.</p></div>
''')

    md('''
<div class="pair">
<div><span class="t">for</span>Without disturbances the open and closed loops differ by 25
points, 50.0% against 75.0%. With them the open loop collapses to 12.5% and the closed loop
keeps 33.3%. The disturbance is what reveals whether a loop is closed. ReAct's ALFWorld has
none, so its 71% cannot tell an open loop from a closed one. SayCan reported 84% and 74%
without one. RT-2's 6,000 trials test generalization, not recovery.</div>
<div><span class="t">against</span>The disturbances were applied by the experimenters during
skill execution to make skills fail, so the protocol measures recovery from failures the
authors chose. 33.3% under disturbance is still two failures in three, and 120 evaluations
spread over 8 instructions and six conditions is a small sample for a headline.</div>
</div>
''')

    md('''
Settle it. How were the disturbances chosen and how often applied? If the paper does not
say, write the disturbance protocol you would require of the next vision-language-action
paper, and say what success rate would count as a closed loop.
''')

    # ---------------------------------------------------------------- prompts: the field
    md("### Debate 1 · Prompts on the field")

    md('''
<div class="callout note"><span class="t">F1 · why is physical AI needed at all</span>
<p><b>Motion.</b> Physical AI is agentic AI with an expensive sensor and an expensive
actuator bolted on, and nothing new is learned by crossing the line.</p></div>
''')

    md('''
<div class="pair">
<div><span class="t">for</span>The industry definition is literally sensors plus actuators.
RT-2 is a vision-language model with actions written as text, and it works. Inner
Monologue's planner is the same frozen model that runs ReAct, fed sentences.</div>
<div><span class="t">against</span>Sutton's argument is about kind. A virtual model predicts
what a person would say next and is never surprised, so it has no ground truth and no goal.
A physical agent predicts what will happen and finds out. Moravec's line says the hard half
of intelligence is perception and mobility, the half a virtual agent skips. The hub agrees
in its own way: 48 of 110 papers close the loop, and 1 of the 22 with no body does.</div>
</div>
''')

    md('''
Settle it. Name one capability a physical agent can have that no virtual agent can have in
principle. If nobody can, the motion carries. If someone can, say whether it is worth the
data (one to two orders of magnitude less), the hardware (under 100,000 arms) and the damage
(Cosmos' sentence).
''')

    md('''
<div class="callout note"><span class="t">F2 · where is the boundary</span>
<p><b>Motion.</b> A task is physical when the state has to be perceived, and whether the
output is a motor command is beside the point.</p></div>
''')

    md('''
<div class="pair">
<div><span class="t">for</span>What breaks SayCan without its value function, and what breaks
Inner Monologue under disturbance, is state, not actuation. ALFWorld hands the state over
and becomes solvable by a prompt.</div>
<div><span class="t">against</span>What makes a mistake matter is the action. You can retry
a search and you cannot un-crack an egg. The loop has to be closed because acting is
irreversible.</div>
</div>
''')

    md('''
Settle it. Draw a two-by-two: state given or perceived, output words or motor commands.
Place ReAct, Inner Monologue, RT-2, a voice chatbot reading a recipe to a cook, Vid2Coach
(camera on smart glasses, speech out), and HoloAssist's remote instructor (watches
first-person video, speaks). Which quadrant is virtual, which is physical, and which is
over-engineered?
''')

    md('''
<div class="callout note"><span class="t">F3 · when is text enough</span>
<p><b>Motion.</b> For guiding a person, a recipe and a chat window cover most of the need,
and a camera adds cost without value.</p></div>
''')

    md('''
<div class="pair">
<div><span class="t">for</span>People can describe their own state. Twelve hub papers reach
the person through language. A phone call has always been able to talk someone through a
task.</div>
<div><span class="t">against</span>HoloAssist's instructors watched the performer's
first-person video the whole time, and two of their six utterance types, correcting a
mistake and confirming the last action, are hard to produce without it. About 6% of
fine-grained actions in HoloAssist were mistakes. Vid2Coach's camera monitoring cut errors
58.5% for eight blind and low-vision cooks. On the other side of the same coin, AR visual
guidance in one assembly study made people 31% faster and raised their error rate.</div>
</div>
''')

    md('''
Settle it. Rank HoloAssist's six utterance types by whether they need the video. Then decide
whether the camera is there for the 6% or for the 94%, and what that says about how much of
assistance is physical AI.
''')

    md('''
<div class="callout note"><span class="t">F4 · what is technically different</span>
<p><b>Motion.</b> The technical difference between virtual and physical AI is the data
pipeline, and the model is the same.</p></div>
''')

    md('''
<div class="pair">
<div><span class="t">for</span>RT-2 is a vision-language model with its architecture
unchanged. SayCan's and Inner Monologue's planners are frozen. RT-2's generalization goes
from 9% trained from scratch to 42% with web pretraining, and keeping web data in the
fine-tuning mix adds 2 points at 5B and 11 at 55B.</div>
<div><span class="t">against</span>Something got added in every physical paper. SayCan added
551 value functions. Inner Monologue added a success detector. RT-2 added an action
tokenizer and 17 months of robot data from 13 robots. V-JEPA 2 added an action-conditioned
predictor on top of a frozen video encoder. The pipeline is the model once a model is
defined by what it is trained on.</div>
</div>
''')

    md('''
<table class="k wide plain">
<thead><tr><th></th><th>ReAct</th><th>SayCan, then Inner Monologue</th><th>RT-2</th></tr></thead>
<tbody>
<tr><td>state</td><td>text, given</td>
    <td>camera, via 551 value functions, then a typed object list</td>
    <td>camera, via VLM tokens</td></tr>
<tr><td>action</td><td>a sentence</td><td>one of 551 skills</td>
    <td>7-DoF deltas as text tokens</td></tr>
<tr><td>success signal</td><td>the game</td>
    <td>3 raters watch video, then a learned detector</td><td>raters, 6,000 trials</td></tr>
<tr><td>cost of error</td><td>retry</td>
    <td>74% → 60% mock to real, 75% → 33% under disturbance</td><td>not reported</td></tr>
<tr><td>training data</td><td>0</td>
    <td>68k demos + 276k episodes, plus the detector's offline data</td>
    <td>13 robots × 17 months, plus web</td></tr>
<tr><td>what crossed from virtual</td><td>the whole planner</td><td>the frozen planner</td>
    <td>9% → 42% of generalization</td></tr>
</tbody></table>
''')

    md('''
Settle it. Argue from this table, and contest any cell.
''')

    md('''
What came out. Filled in after the session: the sides, the strongest argument each way,
where the room landed, and which prompts to reuse.
''')

    box("prompts")
