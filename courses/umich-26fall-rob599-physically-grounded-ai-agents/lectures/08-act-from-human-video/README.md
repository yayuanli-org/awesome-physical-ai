# Debate 6 · Act from human video

ROB 599 · Lecture 8 · Oct 21, 2026.

Debate 5 asked how a robot should choose its next step. This one moves to the next stage of the loop, [act](https://github.com/yayuanli-org/awesome-physical-ai/tree/main/courses/umich-26fall-rob599-physically-grounded-ai-agents/lectures/02-where-the-field-stands#25-act-a-person-just-acts-a-robot-has-to-be-controlled): turn the step into joint commands. Both papers learn those commands mostly from video of people doing tasks, then fit them to the robot with far less robot data. They differ in how they read an action out of a video with no robot in it.

| paper | why |
|---|---|
| EgoScale. Zheng et al., preprint 2026. [arXiv](https://arxiv.org/abs/2602.16710) · [project](https://research.nvidia.com/labs/gear/egoscale/) | Reads the actions off the person's hand. It turns the wrist and finger motion in 20,854 hours of first-person video, over 20 times earlier efforts, into commands for a robot hand with 22 degrees of freedom. Its error falls log-linearly with hours and tracks real-robot success. |
| LAPT-Scale. Xiang et al., CoRL 2026. [arXiv](https://arxiv.org/abs/2610.13732) | Infers the actions from how the frames change, with no hand tracking. A model trained on 23.3K hours of video turns each pair of frames into a latent action, a vector for whatever moved. Real-robot success rises from 63.3% to 85.0% as the pretraining video grows from 1K to 5K hours. |

Prepare the five PACES rows for both.

## Theme debate

Motion: a robot should learn to act mainly from video of people, rather than from demonstrations recorded on robots.

- Video of people is plentiful but holds no robot actions, and reading them out is fragile. In LAPT-Scale's test, 5K hours with hand-tracked actions left real-robot success at 55.0%, the same as with no human video, while latent actions from the same video reached 85.0%.
- Robot demonstrations hold the exact actions but are scarce. Both papers still need them to fit the robot's body: about 4 hours of robot play plus up to 100 demonstrations per task in EgoScale, 250 hours in LAPT-Scale.
- The motion asks which of these should carry most of what a robot learns.
