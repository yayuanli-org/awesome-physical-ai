# Debate 10 · Agent swarms

ROB 599 · Lecture 12 · Nov 18, 2026.

Debate 9's agents all answered the same question, then checked each other's answers. In a swarm, each agent takes a different part of one task, and the parts run at the same time. This moves back two stages of the loop, to [decide](https://github.com/yayuanli-org/awesome-physical-ai/tree/main/courses/umich-26fall-rob599-physically-grounded-ai-agents/lectures/02-where-the-field-stands#24-decide-pick-one-future-and-say-why), because someone has to split the work before anyone acts. It is the second of the two weeks on multi-agent AI. Both papers are digital agents that search the web or write code, and neither uses a robot, so the theme debate asks whether what they found carries over to teams of robots. They differ on who splits the work: a lead agent that hands out the parts, or the workers themselves.

| paper | why |
|---|---|
| Kimi K2.5 Agent Swarm. Kimi Team, preprint 2026. [arXiv](https://arxiv.org/abs/2602.02276) · [code](https://github.com/MoonshotAI/Kimi-K2.5) | A lead splits the work. Read its Agent Swarm sections, §3 and §5.2. A lead agent breaks the task into parts and starts a helper for each, and the helpers run at the same time. The helpers are fixed copies of the model, and reinforcement learning trains only the lead, with an early bonus for starting helpers so it does not slip back into doing everything itself. On BrowseComp's web research questions the swarm scores 78.4%, against 60.6% for the same model working alone, and on WideSearch it reaches the same score 3 to 4.5 times faster. |
| Agensh. Zhan et al., preprint 2026. [arXiv](https://arxiv.org/abs/2609.26781) · [code](https://github.com/microsoft/Agensh) | No lead. Every worker reads what the others have done, claims a part for itself, and merges its finished work into a shared code repository. It names the lead in swarms such as Kimi's as the limit on how big a team can grow. Rebuilding the five hardest programs in ProgramBench from scratch in 6 hours, 128 agents pass 28.8% of the tests, against 19.3% for one agent. On pandoc, 1,024 agents pass 55.1%, against 33.9%. |

Prepare the five PACES rows for both.

## Theme debate

Do this week's conclusions about digital agents carry over to a team of robots?

Motion: a swarm needs no lead.

- Task: several robots share one kitchen and cook a meal together.
- Measure: how often the meal is done right within a set time, as in Agensh's 6-hour runs. Cost does not count.
- For: Agensh's workers each read the shared state, claim a part, check it and merge it, and the team kept improving up to 1,024 workers with no lead. Kimi's lead sees only the short results its helpers send back. A robot at the stove sees the pot itself, so it can take the next step there without waiting for an order.
- Against: Agensh's workers clash only in code, and they fix a clash afterwards by merging. Even there it had to start its workers seconds apart so they would not claim the same parts, and two robots that grab the same pan collide with nothing to merge. Kimi's lead learns when to split the work and when not to, so a lead can keep robots off the same pan and keep the steps in order.
