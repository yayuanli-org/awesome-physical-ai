# Debate 9 · Multi-agent debate

ROB 599 · Lecture 11 · Nov 11, 2026.

Debate 8's agents kept notes from their own attempts. ReasoningBank's agent also judged for itself whether each attempt had worked, and its judge agreed with the true outcome only 72.7% of the time. This one moves back one stage of the loop, to [verify](https://github.com/yayuanli-org/awesome-physical-ai/tree/main/courses/umich-26fall-rob599-physically-grounded-ai-agents/lectures/02-where-the-field-stands#26-verify-close-the-loop-on-what-happened), and hands the check to other agents. It opens two weeks on multi-agent AI. This week several copies of one model answer the same question, read each other's answers, and revise their own over a few rounds. Neither paper uses a robot, since only one of the hub's 42 robot papers puts more than one robot on a task. They differ on where the gain comes from: the talk between the agents, or the count of their answers.

| paper | why |
|---|---|
| Multiagent Debate. Du et al., ICML 2024. [arXiv](https://arxiv.org/abs/2305.14325) · [code](https://github.com/composable-models/llm_multiagent_debate) | The talk helps. Three copies of ChatGPT answer on their own, then read each other's answers and revise their own. On arithmetic, debate reaches 81.8% against 69.0% for a vote over the three first answers, and on grade-school math 85.0% against 81.0%. More agents and more rounds raised arithmetic accuracy, with no gain past four rounds. |
| Debate or Vote. Choi, Zhu and Li, NeurIPS 2025. [arXiv](https://arxiv.org/abs/2508.17536) · [code](https://github.com/deeplearning-wisc/debate-or-vote) | The count does the work. It splits debate into its two parts, several agents and the talk between them. With Qwen2.5-7B, a vote over five agents' first answers averages 76.9% across seven benchmarks, above the best debate setup at 73.8%, and in most setups more rounds make debate worse. Under its model of how agents update their beliefs, it proves that talking leaves each agent's expected chance of being right where it started. |

Prepare the five PACES rows for both.

## Theme debate

Motion: agents that act in the physical world should debate before they act, rather than act and let the world check them.

- Debate fixes a plan while it is still words. This week's agents all read the same question, so their talk only passes answers around. Robots see and reach different things, so they have facts to share. In [RoCo](https://arxiv.org/abs/2307.04738), robot arms each run their own model and talk until they agree on a plan, and a simulator checks it for collisions before any arm moves. Sorting cubes, the arms succeeded in 93% of runs, against 70% for one model that saw everything. But that model did better on four of RoCo's six tasks, and when the simulator stopped saying why a plan failed, sorting fell to 53%.
- Acting first suits a world that does not wait. This week's agents revise their answers while the question holds still. A robot's scene, or the person it helps, changes during every round of talk, and even RoCo's authors call the wait for each model reply a problem when speed matters or the scene changes. In [Chen et al.](https://arxiv.org/abs/2309.15943), robots that each ran a model and talked in rounds succeeded in 25% of runs on a box-moving task, against 75% for one central model, with about eight times the model calls. But the world checks a move only after it is made, too late for one that cannot be undone. The best setup there talked only as a check: one model proposed a plan and each robot's model checked its own part, for 82.5%.
- The motion asks whether a physical agent's next move should be checked by other agents before it acts, or by the world after it acts.
