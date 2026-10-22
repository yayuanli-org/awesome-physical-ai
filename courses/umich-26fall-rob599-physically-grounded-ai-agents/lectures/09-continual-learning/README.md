# Debate 7 · Continual learning

ROB 599 · Lecture 9 · Oct 28, 2026.

Debate 6's robots learn from human video once, then stay fixed after deployment. This one moves to the last stage of the loop, [adapt](https://github.com/yayuanli-org/awesome-physical-ai/tree/main/courses/umich-26fall-rob599-physically-grounded-ai-agents/lectures/02-where-the-field-stands#27-adapt-better-on-the-next-attempt-because-of-the-last-one): get better on the next attempt because of the last one. It opens two weeks on self-evolving AI, where a model keeps changing after training. This week the weights change. Both papers teach a language model new skills or facts without erasing old ones. Neither uses a robot, since only 7 of the hub's 110 papers adapt at all. They differ in what has to change: how today's models are trained, or how models are built.

| paper | why |
|---|---|
| Self-Distillation Enables Continual Learning. Shenfeld et al., preprint 2026. [arXiv](https://arxiv.org/abs/2601.19897) · [code](https://www.idanshenfeld.com/SDFT/) | Keeps today's model and changes how it trains. A copy of the model that sees a demonstration in its prompt acts as the teacher, and the model learns on its own answers. On a chemistry task, plain fine-tuning drops the model's other skills from 65.5 to 53.4 on average, while this method keeps them at 64.5 and scores higher on the new task. |
| Nested Learning. Behrouz et al., NeurIPS 2025. [arXiv](https://arxiv.org/abs/2512.24695) · [blog](https://research.google/blog/introducing-nested-learning-a-new-ml-paradigm-for-continual-learning/) | Changes how the model is built. It treats a network as parts that learn at different speeds, from fast memory to slow knowledge, and builds Hope, a model whose memory keeps updating as it runs. Hope learns new text categories one after another better than three baselines, and at 1.3B parameters it beats a Transformer on language modeling. |

Prepare the five PACES rows for both.

## Theme debate

Motion: a model that keeps learning needs a new architecture, rather than a better way to train the models we have.

- A new architecture builds the learning in. Nested Learning's model has parts that update at different speeds, and at 1.3B parameters it beat a standard Transformer on average accuracy, 58.0 to 53.4. But its continual-learning tests are all on text, and the paper takes its baselines from results other papers reported.
- A better training method keeps today's models. Self-Distillation taught a 7B model facts from 2025 at 89% accuracy, against 80% for plain fine-tuning, and it learned three skills in a row without losing the earlier ones. But it only works if the model can already learn from an example in its prompt. At 3B it trailed plain fine-tuning by 3.3 points.
- The motion asks whether forgetting comes from how models are built or from how they are trained.
