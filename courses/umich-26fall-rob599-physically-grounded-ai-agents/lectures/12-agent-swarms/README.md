# Debate 10 · Agent swarms

ROB 599 · Lecture 12 · Nov 18, 2026.

Debate 9's agents all answered the same question, then checked each other's answers. In a swarm, each agent takes a different part of one task, and the parts run at the same time. This moves back two stages of the loop, to [decide](https://github.com/yayuanli-org/awesome-physical-ai/tree/main/courses/umich-26fall-rob599-physically-grounded-ai-agents/lectures/02-where-the-field-stands#24-decide-pick-one-future-and-say-why), because someone has to split the work before anyone acts. It is the second of the two weeks on multi-agent AI. Both papers test digital agents on tasks such as web research, finance and coding, and neither uses a robot, so the theme debate asks whether what they found carries over to teams of robots. They differ on what makes a swarm pay off: a lead trained to split the work, or a team design that fits the task.

| paper | why |
|---|---|
| Kimi K2.5 Agent Swarm. Kimi Team, preprint 2026. [arXiv](https://arxiv.org/abs/2602.02276) · [code](https://github.com/MoonshotAI/Kimi-K2.5) | A lead splits the work. Read its Agent Swarm sections, §3 and §5.2. A lead agent breaks the task into parts and starts a helper for each, and the helpers run at the same time. The helpers are fixed copies of the model, and reinforcement learning trains only the lead, with an early bonus for starting helpers so it does not slip back into doing everything itself. On BrowseComp's web research questions the swarm scores 78.4%, against 60.6% for the same model working alone, and on WideSearch it reaches the same score 3 to 4.5 times faster. |
| Towards a Science of Scaling Agent Systems. Kim et al., preprint 2025. [arXiv](https://arxiv.org/abs/2512.08296) · [blog](https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/) | It depends on the task. With the same tools, prompts and token budget, it compares one agent with four team designs, from a lead that hands out the parts to peers who debate with no lead, as in Debate 9. It runs them on six benchmarks with models from OpenAI, Google and Anthropic. A lead adds 80.8% over one agent on financial analysis, while on web browsing peers with no lead add 9.2% and a lead adds 0.2%. On PlanCraft, a crafting game whose steps must come in order, every team does worse than one agent, by 39% to 70%. |

Prepare the five PACES rows for both.

## Theme debate

Do this week's conclusions about digital agents carry over to a team of robots?

Motion: a swarm needs no lead.

- Task: several robots share one kitchen and cook a meal together.
- Measure: performance only, meaning how often the meal is done right. Speed and cost do not count.
- For: in Google's study, peers with no lead beat a lead on web browsing, 9.2% to 0.2% over one agent. On PlanCraft, whose crafting steps must come in order, they also lost less, 41.5% against 50.3%. Kimi's lead sees only the short results its helpers send back, while a robot at the stove sees the pot itself and can take the next step without waiting for an order.
- Against: in the same study, agents working side by side with no one checking them let errors grow 17.2 times, against 4.4 times when a lead checked their work. A lead also beat peers on financial analysis, 80.8% to 74.5% over one agent. In a kitchen an error is a spilled pan, and nothing undoes it. Kimi's lead learns when to split the work and when not to, so it could keep two robots off the same pan and keep the steps in order.
