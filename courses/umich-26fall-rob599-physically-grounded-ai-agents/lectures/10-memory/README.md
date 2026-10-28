# Debate 8 · Memory

ROB 599 · Lecture 10 · Nov 4, 2026.

Debate 7 changed a model's weights so it could keep learning after training. This one stays at the same stage of the loop, [adapt](https://github.com/yayuanli-org/awesome-physical-ai/tree/main/courses/umich-26fall-rob599-physically-grounded-ai-agents/lectures/02-where-the-field-stands#27-adapt-better-on-the-next-attempt-because-of-the-last-one), and leaves the weights alone. The agent writes down what it learned and reads it back on the next task. It is the second of the two weeks on self-evolving AI. Debate 7's Self-Distillation paper points this way. Given the right article in its prompt, the model answered 91% of questions about new facts, above the 89% it reached by training the facts into its weights. Both papers are language-model agents that keep notes from their own attempts. Neither uses a robot, since only 2 of the hub's 42 robot papers adapt. They differ in whether a note should hold every detail or a short lesson.

| paper | why |
|---|---|
| ACE (Agentic Context Engineering). Zhang et al., ICLR 2026. [arXiv](https://arxiv.org/abs/2510.04618) · [code](https://github.com/ace-agent/ace) | Keeps the details. The agent's notes are one playbook of short bullets, each a strategy, a fact about the domain or a common mistake. After each task it adds or edits a few bullets and never rewrites the whole. On AppWorld's agent tasks it raises the score from 42.4 to 59.4, within a point of the leaderboard's top agent while running on an open model. |
| ReasoningBank. Ouyang et al., ICLR 2026. [arXiv](https://arxiv.org/abs/2509.25140) · [code](https://github.com/google-research/reasoning-bank) | Keeps short lessons. After each task the agent judges whether it succeeded, then writes a few general strategies, from its failures as well as its successes. On WebArena's web tasks it raises success from 40.5% to 48.8% and cuts the average from 9.7 steps to 8.3. |

Prepare the five PACES rows for both.

## Theme debate

Motion: an agent should keep what it learns in full detail, rather than as a few short lessons.

- Full detail keeps the specifics a task turns on. When ACE rewrote its notes in full instead of editing them, its AppWorld average fell from 70.3 to 56.9. But detail is only as good as the feedback behind it. With no correct answers to learn from, ACE lowered a finance task from 70.7 to 67.3.
- Short lessons travel to new tasks, and they let an agent learn from its failures. Adding failed attempts raised ReasoningBank's success from 46.5% to 49.7%, while the same change lowered a memory of whole routines from 44.4% to 42.2%. But the agent writes its lessons from its own verdicts, and its judge agreed with the true outcome only 72.7% of the time.
- The motion asks whether an agent's memory should hold the specifics of past tasks or the general rule drawn from them.
