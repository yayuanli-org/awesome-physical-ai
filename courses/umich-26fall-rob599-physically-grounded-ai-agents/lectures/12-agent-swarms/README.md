# Debate 10 · Agent swarms

ROB 599 · Lecture 12 · Nov 18, 2026.

Debate 9's agents all answered the same question, then checked each other's answers. In a swarm, each agent takes a different part of one task, and the parts run at the same time. This moves back two stages of the loop, to [decide](https://github.com/yayuanli-org/awesome-physical-ai/tree/main/courses/umich-26fall-rob599-physically-grounded-ai-agents/lectures/02-where-the-field-stands#24-decide-pick-one-future-and-say-why), because someone has to split the work before anyone acts. It is the second of the two weeks on multi-agent AI. Both papers are digital agents that search the web or write code, and neither uses a robot, so the theme debate asks whether what they found carries over to teams of robots. They differ on who splits the work: a lead agent that hands out the parts, or the workers themselves.

| paper | why |
|---|---|
| Kimi K2.5 Agent Swarm. Kimi Team, preprint 2026. [arXiv](https://arxiv.org/abs/2602.02276) · [code](https://github.com/MoonshotAI/Kimi-K2.5) | A lead splits the work. Read its Agent Swarm sections, §3 and §5.2. A lead agent breaks the task into parts and starts a helper for each, and the helpers run at the same time. The helpers are fixed copies of the model, and reinforcement learning trains only the lead, with an early bonus for starting helpers so it does not slip back into doing everything itself. On BrowseComp's web research questions the swarm scores 78.4%, against 60.6% for the same model working alone, and on WideSearch it reaches the same score 3 to 4.5 times faster. |
| Agensh. Zhan et al., preprint 2026. [arXiv](https://arxiv.org/abs/2609.26781) · [code](https://github.com/microsoft/Agensh) | No lead. Every worker reads what the others have done, claims a part for itself, and merges its finished work into a shared code repository. It names the lead in swarms such as Kimi's as the limit on how big a team can grow. Rebuilding the five hardest programs in ProgramBench from scratch in 6 hours, 128 agents pass 28.8% of the tests, against 19.3% for one agent. On pandoc, 1,024 agents pass 55.1%, against 33.9%. |

Prepare the five PACES rows for both.

## Theme debate

Do this week's conclusions about digital agents carry over to teams of robots?

Motion: a team of robots on one task gets better and faster as it grows, as the digital swarms in both papers do.

- It carries over when one planner directs the whole team. In [RoboBallet](https://arxiv.org/abs/2509.05397), one learned planner gives each robot arm its reaching tasks and plans every arm's motion in a shared work cell. On the same 20 tasks, eight arms finish in about 4.5 seconds, against 7.5 for four. In [LLaMAR](https://arxiv.org/abs/2407.10031), one planner directs simulated household robots, and success rises from 37% with one robot to 70% with three. In [Chen et al.](https://arxiv.org/abs/2309.15943), arms moving boxes succeed in 75% of runs under a lead, against 25% when they settle each move by talking, as Kimi would expect. But RoboBallet only takes tasks that can be done in any order, and cooking or assembly has steps that must wait for others.
- Robots take up room, and digital agents do not. Kimi's helpers each keep their own context, and Agensh's workers fix a clash in the code by merging. Robots share one space, and a collision cannot be merged or undone. In LLaMAR, success fell from 70% with three robots to 62% with five, because they blocked each other in single rooms. A lead also stops scaling, as Agensh warns. In Chen et al., the lead's success fell from 100% with eight arms to 30% with 32, while a lead whose robots checked its orders still reached 50%. But in LLaMAR's roomier search-and-rescue world, success kept rising, to 74% with five robots.
- The motion asks whether robots, which share one space and often one order of steps, gain from a bigger team the way digital agents do, and whether a lead helps them or holds them back.
