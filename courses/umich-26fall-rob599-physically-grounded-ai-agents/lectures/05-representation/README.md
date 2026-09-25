# Debate 3 · Representation

ROB 599 · Lecture 5 · Sep 30, 2026.

Debates 1 and 2 were about the body, a robot and then a person. This one is about how the agent represents what it sees: predict every pixel (diffusion) or predict an embedding (JEPA).

| paper | why |
|---|---|
| I-JEPA. Assran et al., CVPR 2023. [arXiv](https://arxiv.org/abs/2301.08243) · [code](https://github.com/facebookresearch/ijepa) | The original JEPA. It learns by predicting the embeddings of hidden image regions and never reconstructs a pixel. |
| DDPM. Ho et al., NeurIPS 2020. [arXiv](https://arxiv.org/abs/2006.11239) · [site](https://hojonathanho.github.io/diffusion/) · [code](https://github.com/hojonathanho/diffusion) | The paper that made diffusion work. It learns by predicting the noise on every pixel, so it models every detail of the image. |

Prepare the five PACES rows for both.
