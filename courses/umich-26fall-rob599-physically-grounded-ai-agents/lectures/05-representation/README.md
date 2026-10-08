# Debate 3 · Representation

ROB 599 · Lecture 5 · Sep 30, 2026.

Debates 1 and 2 were about the body, a robot and then a person. This one is about how the agent represents what it sees: predict every pixel (diffusion) or predict an embedding (JEPA).

| paper | why |
|---|---|
| I-JEPA. Assran et al., CVPR 2023. [arXiv](https://arxiv.org/abs/2301.08243) · [code](https://github.com/facebookresearch/ijepa) | The original JEPA. It learns by predicting the embeddings of hidden image regions and never reconstructs a pixel. |
| DDPM. Ho et al., NeurIPS 2020. [arXiv](https://arxiv.org/abs/2006.11239) · [site](https://hojonathanho.github.io/diffusion/) · [code](https://github.com/hojonathanho/diffusion) | The paper that made diffusion work. It learns by predicting the noise on every pixel, so it models every detail of the image. |

Prepare the five PACES rows for both.

## Theme debate

Motion: physical AI, with either a robot or a person as the body, should learn its perception representation by predicting embeddings rather than pixels.

- I-JEPA is cheap but lossy by design. It trains with over 10 times less compute than MAE, and the paper credits its gain to dropping pixel detail, some of which an agent might need.
- DDPM keeps everything but pays for it. The last 100 of its 1,000 steps use 1.66 of 1.78 bits per dimension just to cut pixel error from 12 to 0.95 out of 255 (Tab. 4), and every image takes 1,000 network passes.
- Neither paper tests acting. The motion asks what an agent's representation must keep.
