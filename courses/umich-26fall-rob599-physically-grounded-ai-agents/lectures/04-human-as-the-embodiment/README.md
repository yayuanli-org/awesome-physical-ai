# Debate 2 · Human as the embodiment

ROB 599 · Lecture 4 · Sep 23, 2026.

Debate 1 ran the loop with a robot as the body (ReAct). This one runs it with a person as the body: the model watches and can only say what to do next.

| paper | why |
|---|---|
| Ego-Exo4D. Grauman et al., CVPR 2024. [arXiv](https://arxiv.org/abs/2311.18259) · [site](http://ego-exo4d-data.org/) | Carried over from Debate 1. A dataset that shows what situations physical AI is about. |
| GuideMe. Liu et al., ECCV 2026. [arXiv](https://arxiv.org/abs/2607.02991) · [project](https://fawnliu.github.io/project/guideme/) · [code](https://github.com/fawnliu/GuideMe) | The loop with a human as the embodiment: watch the stream, catch the error, speak in time. |

Prepare the five PACES rows for both.

## Theme debate

Motion: when the body changes from a robot to a person, only the last step, acting, has to change. Perception and planning can be shared.

- Sharing everything but acting is simple but assumes a person follows instructions the way a robot follows commands. Only the output changes, from motor commands to spoken instructions.
- Adapting the earlier steps fits a person but costs a second system. GuideMe found that current models give instructions well but miss the person's errors and barely beat chance at choosing when to speak, and those are deciding and checking, not acting.
- The motion asks whether a new body changes only the last step of the loop.
