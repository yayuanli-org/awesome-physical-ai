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

Motion: a vote among agents is as accurate as a debate.

- Task: several AI agents check whether a step of a cooking or assembly task was done right.
- Measure: performance only, meaning how often the verdict is right. Speed and cost do not count.
- For: agents that watch the same video are the setting where Debate or Vote proves talk adds nothing on average. A debate can also agree on a wrong verdict with confidence, as Du et al. saw on written questions.
- Against: give the agents different views or roles, such as a head camera, a wall camera and the recipe. If only the head camera saw the salt go in twice, a vote misses it 2 to 1, and a debate lets that agent tell the others. In Debate or Vote, agents with different roles beat the vote on medical questions by debating, 84.2% to 82.4%.
