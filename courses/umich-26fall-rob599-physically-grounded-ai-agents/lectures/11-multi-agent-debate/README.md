# Debate 9 · Multi-agent debate

ROB 599 · Lecture 11 · Nov 11, 2026.

Debate 8's agents kept notes from their own attempts. ReasoningBank's agent also judged for itself whether each attempt had worked, and its judge agreed with the true outcome only 72.7% of the time. This one moves back one stage of the loop, to [verify](https://github.com/yayuanli-org/awesome-physical-ai/tree/main/courses/umich-26fall-rob599-physically-grounded-ai-agents/lectures/02-where-the-field-stands#26-verify-close-the-loop-on-what-happened), and hands the check to other agents. It opens two weeks on multi-agent AI. This week several copies of one model answer the same question, read each other's answers, and revise their own over a few rounds. Neither paper uses a robot, since only one of the hub's 42 robot papers puts more than one robot on a task. They differ on where the gain comes from: the talk between the agents, or the count of their answers.

| paper | why |
|---|---|
| Multiagent Debate. Du et al., ICML 2024. [arXiv](https://arxiv.org/abs/2305.14325) · [code](https://github.com/composable-models/llm_multiagent_debate) | The talk helps. Three copies of ChatGPT answer on their own, then read each other's answers and revise their own. On arithmetic, debate reaches 81.8% against 69.0% for a vote over the three first answers, and on grade-school math 85.0% against 81.0%. More agents and more rounds raised arithmetic accuracy, with no gain past four rounds. |
| Debate or Vote. Choi, Zhu and Li, NeurIPS 2025. [arXiv](https://arxiv.org/abs/2508.17536) · [code](https://github.com/deeplearning-wisc/debate-or-vote) | The count does the work. It splits debate into its two parts, several agents and the talk between them. With Qwen2.5-7B, a vote over five agents' first answers averages 76.9% across seven benchmarks, above the best debate setup at 73.8%, and in most setups more rounds make debate worse. Under its model of how agents update their beliefs, it proves that talking leaves each agent's expected chance of being right where it started. |

Prepare the five PACES rows for both.

## Theme debate

What makes a good debate in physical AI?

Motion: in physical AI tasks too, a vote does as well as a debate.

- A vote is enough. Physical tasks run on a clock. A vote takes one round with every agent answering at once, while a debate waits for every agent in every round as the scene keeps changing. Du et al. ran mostly three agents for two rounds because of the compute cost. A debate can also agree on a wrong answer and affirm it with confidence, and in a physical task a robot then acts on it.
- Debate adds what a vote cannot. Debate or Vote's proof that talk adds nothing on average covers agents that all read the same question. Robots and people in one scene each see and reach different things. If only one of three robots sees a person step into the path, a vote says go, 2 to 1, and a debate lets that robot tell the others.
- The motion asks whether a physical task changes what a debate between agents can add over a vote.
