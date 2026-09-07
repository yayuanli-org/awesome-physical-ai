# Debate 1 · From virtual to physical AI

ROB 599, Fall 2026. Draft 1, 2026-09-07, for discussion. The last section fills in after the session.

## The question

"AI is going from virtual to physical" sounds obvious and is hard to make precise. Where is the line, what does crossing it cost, and how much of what people want from AI sits on the far side? The two core papers run the same loop, think, act, read what came back, on the two sides of the line, so every claim about the boundary can be checked against two sets of numbers. Lecture 2, §2, argues that the body breaks that loop in three places, the state, the act and the check. This debate is whether that argument holds.

```
Bisk 2020    WS2 internet ──────────► WS3 perception ──────────► WS4 embodiment
             "virtual AI"                                        "physical AI"

core         ReAct (ICLR 2023)                                   Inner Monologue (CoRL 2022)
             a house made of text, ALFWorld                      a real kitchen, feedback typed back as text
             0 training, 3 examples per task type                frozen PaLM, one learned success detector
             71% best / 57% average                              50% → 75% with the loop closed
                                                                 12.5% → 33% when a person disturbs the scene

side         SayCan: the body's price list. 551 skills, 68k demos, 84% → 67% without grounding
             Bisk: the ladder · Sutton: why text cannot be enough · RT-2: what crosses over, 9% → 42% → 44%

prompts      R1–R3 on ReAct        I1–I3 on Inner Monologue        F1–F4 on the field
```

ReAct is the control, the loop in a world where the state is handed over, every action works and the game reports success. Inner Monologue is the treatment, the same loop in a kitchen, with the state and the check fed back to the planner as sentences. The two papers already argue with each other, since ReAct's ablation ReAct-IM copies Inner Monologue's feedback style and loses. SayCan sits underneath both as the side reading that itemizes what a body costs. Bisk supplies the vocabulary, Sutton the sharpest case that virtual is not enough, RT-2 the one controlled measurement of how much crosses over. The prompts run from paper-level claims up to the question in the title.

## 1. Reading list

### Core

| Paper | Its role here | Read | Pages |
|---|---|---|---|
| ReAct: Synergizing Reasoning and Acting in Language Models. Yao et al., ICLR 2023. [arXiv](https://arxiv.org/abs/2210.03629) | The loop with no body, in a house made of text | Sections 1, 2, 4, and one ALFWorld trajectory from Appendix D.2 | ~8 |
| Inner Monologue: Embodied Reasoning through Planning with Language Models. Huang et al., CoRL 2022. [arXiv](https://arxiv.org/abs/2207.05608) | The same loop with a body, closed by writing perception down as text | Method, experiments and the limitations paragraph. Skip the intro and related work, as the hub's reading protocol says | ~9 |

ReAct. Prompt a language model to alternate a thought, an action, and the observation the environment returns, all in one token stream. ALFWorld is a text version of a house. The observation is a sentence listing what is at your location, the action is a sentence, and a valid action always works. With three annotated example trajectories per task type and no training, the best ReAct prompt solves 71% of 134 unseen tasks, and 57% averaged over six prompts. The same prompts without thoughts reach 45%. BUTLER, an imitation learner trained on 100,000 expert trajectories per task type, reaches 37%. Read it as the control condition, what the brain does when the world is free.

Inner Monologue. Keep the frozen planner and give it the world back as text. After each skill a success detector says whether it worked, an object recognizer says what is in view, and a person can answer a question the planner asks. All of it is appended to the prompt and the planner picks the next skill. In a real kitchen, on 8 instructions over 120 evaluations, the open-loop baseline (SayCan) completes 50.0% and the closed loop 75.0%. When a person disturbs the scene during execution, the baseline drops to 12.5% and the closed loop keeps 33.3%. Read the fine print with it. In simulation every feedback signal is ground truth from the simulator, and in the kitchen the object recognition is human-provided, so the only learned perception in the headline result is the success detector.

### Side readings

Four units, in reading order. Each is there for one reason.

| Unit | For | Read |
|---|---|---|
| Do As I Can, Not As I Say: Grounding Language in Robotic Affordances. Ahn et al., CoRL 2022. [arXiv](https://arxiv.org/abs/2204.01691) · [site](https://say-can.github.io/) | The paper Inner Monologue builds on, and the price list for a body. 551 skills from 68,000 demonstrations, and plan success falls from 84% to 67% when the value function is removed | The scoring rule and Table 2, ~4 pages |
| Bisk et al., Experience Grounds Language, EMNLP 2020. [arXiv](https://arxiv.org/abs/2004.10151) | The vocabulary. Five World Scopes: corpus, internet, perception, embodiment, social. "Virtual AI" is scope 2 and "physical AI" is scope 4 | All, ~8 pages |
| Dwarkesh Podcast, "Richard Sutton – Father of RL thinks LLMs are a dead end", 26 Sep 2025, 66 min. [link](https://www.dwarkesh.com/p/richard-sutton) | The case that a virtual model is missing something in kind, not in degree. No goal, no ground truth, never surprised | The whole episode, or the first ten minutes |
| RT-2: Vision-Language-Action Models Transfer Web Knowledge to Robotic Control. Brohan et al., CoRL 2023. [arXiv](https://arxiv.org/abs/2307.15818) | The one controlled measurement of how much web knowledge crosses into physical action | Experiments section and Tables 6 to 8, ~5 pages |

Alternates, if the group leans a different way. For the podcast, "Fully autonomous robots are much closer than you think – Sergey Levine" (Dwarkesh Podcast, 12 Sep 2025) is the practitioner's version with numbers. Robot datasets are one to two orders of magnitude smaller than vision-language corpora, an arm cost $400,000 in 2014 and $3,000 now, and his median guess for household autonomy is five years out. For the fourth unit, HoloAssist (ICCV 2023) replaces RT-2 if the group cares more about guiding people than about robots. It holds 166 hours of a remote instructor watching a performer's first-person video and talking them through a task.

Not assigned. NVIDIA's Cosmos paper and Jensen Huang's CES 2025 keynote supply the industry definition, which is one sentence and sits in the recap with a link.

That is the reading. The recap below reduces it to the numbers the room needs in hand.

## 2. Recap, the first ten minutes

Enough to argue from if nobody read anything. Every number comes from the source named on its line.

Three definitions.

- Industry. "Physical AI is an AI system equipped with sensors and actuators: the sensors allow it to observe the world, and the actuators allow it to interact with and modify the world." ([Cosmos](https://arxiv.org/abs/2501.03575), NVIDIA, Jan 2025.) Huang at CES 2025 named the eras as perception AI, then generative AI, now physical AI, and said "the ChatGPT moment for general robotics is just around the corner."
- The hub. Physical AI studies how the physical world gets changed in the age of AI. Model the world, change it through an embodiment, and since acting changes what has to be modeled, the two close into a loop. Virtual, in the hub's columns, is embodiment `none` or `sim`.
- The ladder. Bisk et al. 2020: WS1 corpus, WS2 internet, WS3 perception, WS4 embodiment, WS5 social. "Most trending work in NLP operates in the second." "You can't learn language from the radio."

What the hub holds, 110 papers as of 2026-09-07.

| Who moves the atoms | Papers | Of which close the loop |
|---|---|---|
| A person, guided or observed | 46 | 14 |
| A robot | 23 | 19 |
| Nothing | 22 | 1 |
| A simulated body | 7 | 6 |
| Person and robot together | 4 | 3 |
| Mixed tags | 8 | 5 |

Language is the representation in 56 of the 110. Half of physical AI, as this hub has it, thinks in words.

The two core papers, side by side.

| | ReAct, ALFWorld | Inner Monologue, real kitchen |
|---|---|---|
| World | 134 unseen text games, 6 task types | 8 instructions in 3 families, 120 evaluations in total |
| State | A sentence listing what is here | A list of visible objects, typed by a person |
| Action | A sentence. Valid ones always work | One of SayCan's skills, run by a learned policy, replanned after each |
| Success signal | The game returns it | A learned success detector reads the before and after images |
| Planner | PaLM-540B, frozen, 3 example trajectories per task type | PaLM-540B, frozen, no training |
| Result | 71% best prompt, 57% average, 45% without thoughts, 37% BUTLER | 50.0% open loop, 75.0% closed. Disturbed: 12.5% and 33.3% |
| The ablation that matters | The worst ReAct prompt, 48%, still beats the best without thoughts, 45% | Success detection alone gives 62.5% and 25.0%. Adding the object list gives the rest |

Six more numbers.

- Inner Monologue in simulation, where all feedback is ground truth, 50 episodes per task with disturbances. Pick and place: policy alone 24%, with the object list 80%, plus success detection 90%, plus a progress description 94%. Stack all blocks: 2%, 4%, 10%, 26%. On the four unseen tasks the policy alone scores 0%. Real tabletop, 10 runs each: 45% with the object list, 90% with success detection added.
- SayCan, 101 instructions in a mock kitchen. Plan 84%, execution 74%. Real kitchen 81% and 60%. Without the value function, plan success 67%. Behind the 551 skills: 68,000 teleoperated demonstrations over 11 months on 10 robots, plus 12,000 successful autonomous episodes filtered from 276,000. Weakest instruction family: Embodiment, the queries about the robot's own state, 64% plan and 55% execution. Two new drawer skills over 21 queries: plan 100%, execution 33%.
- RT-2, 5B model, generalization to unseen objects and scenes. Trained from scratch 9%. Web-pretrained, then fine-tuned on robot data only, 42%. Co-fine-tuned on web and robot data, 44%. At 55B, co-fine-tuning 63% against fine-tuning 52%. Overall unseen 62% against RT-1's 32%, over 6,000 real trials. Robot data from 13 robots over 17 months.
- Cost of a body. Levine, Sep 2025: robot datasets one to two orders of magnitude smaller than vision-language corpora, and his guess is under 100,000 arms in the world of the kind you could train on. Cosmos: "these actions perturb the physical world and may cause severe damage to the system and the world."
- Guiding a person. HoloAssist, 166 hours, 2,221 sessions, 222 participants: the remote instructor watched the performer's first-person video throughout, and about 6% of fine-grained actions were mistakes. Vid2Coach: 58.5% fewer errors for eight blind and low-vision cooks against their usual workflow. One AR assembly study: 31% faster and a higher error rate.
- Moravec, 1988: "it is comparatively easy to make computers exhibit adult level performance on intelligence tests or playing checkers, and difficult or impossible to give them the skills of a one-year-old when it comes to perception and mobility."

Three quotes for a slide.

- Sutton, Sep 2025: "Large language models are about mimicking people, doing what people say you should do. They're not about figuring out what to do."
- Sutton again: "There's no ground truth in large language models because you don't have a prediction about what will happen next."
- Fei-Fei Li, Nov 2025: today's models are "eloquent but inexperienced, knowledgeable but ungrounded."

That is the recap. The prompts below spend those numbers.

## 3. Debate prompts

Each prompt is a motion one side defends, the evidence either side can reach for from the readings, and the question that settles it. The paper prompts follow PACES. The first on each paper is about the claim and whether the evaluation substantiates it, the second about the approach, the third about the evaluation itself. Ten are here so the group can choose. The recommended four for one session are R1, I1, F2 and F3.

### On ReAct

R1. Motion: ALFWorld is a physical task with the physics deleted, and that deletion is why ReAct works.

For. The environment hands over the three things Lecture 2 says the body breaks. The state arrives as a sentence. Every valid action succeeds. The task ends with a symbolic check. Remove any one and the 71% says nothing about a kitchen.

Against. ALFWorld keeps the part of the problem the language model actually solves. A task can have more than 50 locations and need more than 50 steps, and the agent has to guess where a desk lamp is likely to be. That prior is the same thing SayCan's planner contributes, and SayCan's ablation prices it at 67 points of plan success on its own.

Settle it. Of the three free things, which costs the physical papers the most? Map each to a number. The state to SayCan's 84% to 67% without the value function. The act to SayCan's 84% plan against 74% execution, and 81% against 60% in the real kitchen. The check to Inner Monologue's 50.0% falling to 12.5% under disturbance.

R2. Motion: ReAct's gains are prompt luck, and the six-prompt spread proves it.

For. Best prompt 71%, average 57%, and the six prompts differ only in which two of the three annotated examples they include and in what order. On the question-answering benchmark ReAct loses to plain chain-of-thought, 27.4 to 29.4.

Against. The paper's own defense is that the worst ReAct prompt, 48%, still beats the best action-only prompt, 45%. The failure analysis shows a change in kind. Hallucination accounts for 56% of chain-of-thought failures and 0% of ReAct's, at the price of reasoning errors rising from 16% to 47%.

Settle it. Is "acting" in ReAct a grounding mechanism, like SayCan's value function, or a retrieval mechanism? The 0% hallucination number is the cleanest hint in either paper of what a world does for a language model. Say what the same effect would look like in a kitchen.

R3. Motion: ReAct-IM settles the format question, and the robot papers picked the wrong one.

For. ReAct-IM copies Inner Monologue's style, which the ReAct authors describe as "limited to observations of the environment state and what needs to be completed by the agent", and scores 53% against ReAct's 71%. Free-form thought beats structured reports on five of six task types. ReAct-IM "often made mistakes in identifying when subgoals were finished", the exact job Inner Monologue gives a success detector.

Against. In the kitchen the structured reports are what lifted Inner Monologue from 12.5% to 33.3% under disturbance. ReAct never met a disturbance, because ALFWorld has none, and its "observation" is the whole state. The comparison is between a format and a world.

Settle it. Design the experiment that separates the two. What would ReAct's thoughts look like if a person removed the object it had just picked up, and what would Inner Monologue's success detector have to say for the planner to recover?

### On Inner Monologue

I1. Motion: the headline kitchen result is a human-in-the-loop result, and the closed-loop claim is only shown with oracle perception.

The claim under debate: "Closed-loop language feedback significantly improves high-level instruction completion on three domains, including simulated and real table top rearrangement tasks and long-horizon mobile manipulation tasks in a kitchen environment in the real world."

For. In simulation every feedback signal comes from the simulator, and the paper says so: "We assume access to oracle scene descriptors." In the kitchen the object list is human-provided. The one learned perception module is the success detector, and the paper names its errors as the first failure mode: false negatives cause extra retries and false positives "add adversarial partial observability." The planner also sometimes "ignored the environment feedback and still proposed policy skills involving objects not present in the scene."

Against. The success detector alone carries the "check" break, and it alone lifts 50.0% to 62.5% and 12.5% to 25.0%. Human object recognition stands in for a detector that existed at the time and bounds what perception could give, which is how you isolate a planner. The claim is about what a planner does with feedback, and the ablations hold that fixed.

Settle it. The hub's `embodiment` column tags Inner Monologue both `robot` and `human+robot`. Which tag does the kitchen result earn, given that the perception runs through a person's eyes? Is it a robot paper, a human-plus-robot paper, or a virtual-AI paper with an excellent sensor?

I2. Motion: writing every feedback signal down as a sentence is the right interface between a virtual brain and a physical body.

For. Nothing in the planner is trained. The same frozen model runs the tabletop and the kitchen, and each added channel adds success in simulation: 80%, 90%, 94% on pick and place. The behaviors the paper calls emergent, asking a person a question, proposing a new goal when the old one is infeasible, taking instructions in another language, come free because the channel is language.

Against. A sentence drops geometry. "Stack all blocks" stays at 4%, 10%, 26% with oracle feedback, because "the red block is on the blue block" carries no pose and no tolerance. ReAct shows the report format costs reasoning, 53% against 71%. And the paper's own failure list ends with the planner ignoring what it was told, which no channel can prevent.

Settle it. Name the first feedback signal that cannot be written as a sentence without losing what the planner needs. Force, pose, timing, contact? Wherever that is, virtual AI plus a text channel stops and physical AI starts.

I3. Motion: the disturbance protocol is the only physical-AI evaluation in these readings, and every paper in the hub's change arc should be required to run one.

For. Without disturbances the open and closed loops differ by 25 points, 50.0% against 75.0%. With them the open loop collapses to 12.5% and the closed loop keeps 33.3%. The disturbance is what reveals whether a loop is closed. ReAct's ALFWorld has none, so its 71% cannot tell an open loop from a closed one. SayCan reported 84% and 74% without one. RT-2's 6,000 trials test generalization, not recovery.

Against. The disturbances were applied by the experimenters during skill execution to make skills fail, so the protocol measures recovery from failures the authors chose. A result of 33.3% under disturbance is still two failures in three, and 120 evaluations spread over 8 instructions and six conditions is a small sample for a headline.

Settle it. How were the disturbances chosen and how often applied? If the paper does not say, write the disturbance protocol you would require of the next vision-language-action paper, and say what success rate would count as a closed loop.

### On the field

F1. Motion: physical AI is agentic AI with an expensive sensor and an expensive actuator bolted on, and nothing new is learned by crossing the line.

For. The industry definition is literally sensors plus actuators. RT-2 is a vision-language model with actions written as text, and it works. Inner Monologue's planner is the same frozen model that runs ReAct, fed sentences.

Against. Sutton's argument is about kind. A virtual model predicts what a person would say next and is never surprised, so it has no ground truth and no goal. A physical agent predicts what will happen and finds out. Moravec's line says the hard half of intelligence is perception and mobility, the half a virtual agent skips. The hub agrees in its own way: 48 of 110 papers close the loop, and 1 of the 22 with no body does.

Settle it. Name one capability a physical agent can have that no virtual agent can have in principle. If nobody can, the motion carries. If someone can, say whether it is worth the data (one to two orders of magnitude less), the hardware (under 100,000 arms) and the damage (Cosmos' sentence).

F2. Motion: a task is physical when the state has to be perceived, and whether the output is a motor command is beside the point.

For. What breaks SayCan without its value function, and what breaks Inner Monologue under disturbance, is state, not actuation. ALFWorld hands the state over and becomes solvable by a prompt.

Against. What makes a mistake matter is the action. You can retry a search and you cannot un-crack an egg. The loop has to be closed because acting is irreversible.

Settle it. Draw a two-by-two: state given or perceived, output words or motor commands. Place ReAct, Inner Monologue, RT-2, a voice chatbot reading a recipe to a cook, Vid2Coach (camera on smart glasses, speech out), and HoloAssist's remote instructor (watches first-person video, speaks). Which quadrant is virtual, which is physical, and which is over-engineered?

F3. Motion: for guiding a person, a recipe and a chat window cover most of the need, and a camera adds cost without value.

For. People can describe their own state. Twelve hub papers reach the person through language. A phone call has always been able to talk someone through a task.

Against. HoloAssist's instructors watched the performer's first-person video the whole time, and two of their six utterance types, correcting a mistake and confirming the last action, are hard to produce without it. About 6% of fine-grained actions in HoloAssist were mistakes. Vid2Coach's camera monitoring cut errors 58.5% for eight blind and low-vision cooks against their usual workflow. On the other side of the same coin, AR visual guidance in one assembly study made people 31% faster and raised their error rate.

Settle it. Rank HoloAssist's six utterance types by whether they need the video. Then decide whether the camera is there for the 6% or for the 94%, and what that says about how much of assistance is physical AI.

F4. Motion: the technical difference between virtual and physical AI is the data pipeline, and the model is the same.

For. RT-2 is a vision-language model with its architecture unchanged. SayCan's and Inner Monologue's planners are frozen. RT-2's generalization goes from 9% trained from scratch to 42% with web pretraining, and keeping web data in the fine-tuning mix adds 2 points at 5B and 11 at 55B.

Against. Something got added in every physical paper. SayCan added 551 value functions. Inner Monologue added a success detector. RT-2 added an action tokenizer and 17 months of robot data from 13 robots. V-JEPA 2 added an action-conditioned predictor on top of a frozen video encoder. The pipeline is the model once a model is defined by what it is trained on.

Settle it. Argue from this table, and contest any cell.

| | ReAct | SayCan, then Inner Monologue | RT-2 |
|---|---|---|---|
| State | text, given | camera, via 551 value functions, then a typed object list | camera, via VLM tokens |
| Action | a sentence | one of 551 skills | 7-DoF deltas as text tokens |
| Success signal | the game | 3 raters watch video, then a learned detector | raters, 6,000 trials |
| Cost of error | retry | 74% → 60% mock to real, 75% → 33% under disturbance | not reported |
| Training data | 0 | 68k demos + 276k episodes, plus the detector's offline data | 13 robots × 17 months, plus web |
| What crossed from virtual | the whole planner | the frozen planner | 9% → 42% of generalization |

## 4. What came out

Filled in after the session: the sides, the strongest argument each way, where the room landed, and which prompts to reuse.
