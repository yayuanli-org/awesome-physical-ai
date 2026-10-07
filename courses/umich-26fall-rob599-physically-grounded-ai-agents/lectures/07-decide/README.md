# Debate 5 · Decide

ROB 599 · Lecture 7 · Oct 14, 2026.

Debate 4 asked whether a robot should predict what happens next before it acts. This one moves to the next stage of the loop, [decide](https://github.com/yayuanli-org/awesome-physical-ai/tree/main/courses/umich-26fall-rob599-physically-grounded-ai-agents/lectures/02-where-the-field-stands#24-decide-pick-one-future-and-say-why): choose the robot's next step. In both papers a language model makes the choice. One picks among skills the robot already has, and the other writes new code for it.

| paper | why |
|---|---|
| SayCan. Ahn et al., CoRL 2022. [arXiv](https://arxiv.org/abs/2204.01691) · [project](https://say-can.github.io/) · [code](https://github.com/google-research/google-research/tree/master/saycan) | Grounds a language model in what a real robot can do. It scores each of the robot's 551 learned skills by how useful it is for the instruction and how likely it is to succeed right now, then runs the best one. |
| Code as Policies. Liang et al., ICRA 2023. [arXiv](https://arxiv.org/abs/2209.07753) · [project](https://code-as-policies.github.io/) · [code](https://github.com/google-research/google-research/tree/master/code_as_policies) | Has a language model write the robot's behavior as code. It turns an instruction into Python that calls perception and motion functions, so it can do things no single skill covers. |

Prepare the five PACES rows for both.
