# Debate 2 · Human as the embodiment

ROB 599 · Lecture 4 · Fall 2026. Two papers, both about a person doing skilled work on camera.

Debate 1 ran the loop with a robot as the body: ReAct thinks, acts, reads the result, repeats.
This one swaps the body for a person. The model no longer moves anything. It watches, and the
only channel it has to change the world is telling the human what to do next, at the right moment.

## The two papers

| paper | its role here | read |
|---|---|---|
| Ego-Exo4D: Understanding Skilled Human Activity from First- and Third-Person Perspectives. Grauman et al., CVPR 2024. [arXiv](https://arxiv.org/abs/2311.18259) · [site](http://ego-exo4d-data.org/) | What physical AI is actually looking at: 1,286 hours of skilled work filmed from the doer's eyes and from outside, with an expert narrating the mistakes | Section 1, Section 3 up to the participants, Section 4.1 on expert commentary, Section 5 with its result tables |
| GuideMe: Multi-Domain Task Guidance and Intervention in Streaming Video. Liu et al., ECCV 2026. [arXiv](https://arxiv.org/abs/2607.02991) · [project](https://fawnliu.github.io/project/guideme/) · [code](https://github.com/fawnliu/GuideMe) | The closed loop with a human as the embodiment: 2,458 videos, 223.7 hours, 47,775 interactions where a model has to catch an error mid-stream and say something | The benchmark construction, the three evaluation components, and the results showing where models over- and under-trigger |

Ego-Exo4D came up in Debate 1 and we ran out of time, so it carries over. Read it as the
picture of the situations this field is about, not as a method.

GuideMe is the method side of the same picture. Its finding is that current multimodal models
give instructions well and miss execution errors: aggressive ones fire constantly with false
alarms, conservative ones stay quiet when intervention was required.

## Why these two

- ReAct in Debate 1 was a loop with a robot as the embodiment. GuideMe is the same loop with a person as the embodiment, so the comparison is about what changes when you cannot act yourself.
- Ego-Exo4D is a dataset, and it is the cheapest way to see what situations physical AI is actually talking about.
- Both live in [the hub](https://yayuanli-org.github.io/awesome-physical-ai/), under sensing and guidance.
