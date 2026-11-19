# Debate 11 · Mistake detection

ROB 599 · Lecture 13 · Dec 2, 2026.

Debate 10's scaling study found that agents working side by side with no one checking them let errors grow 17.2 times. This one moves two stages on from Debate 10's decide, to [verify](https://github.com/yayuanli-org/awesome-physical-ai/tree/main/courses/umich-26fall-rob599-physically-grounded-ai-agents/lectures/02-where-the-field-stands#26-verify-close-the-loop-on-what-happened), and checks physical actions. Did a step of a task go wrong, and what went wrong? Research on people calls this mistake detection, and robotics calls it failure detection. Of the hub's 32 verify papers, 21 watch a person and 6 watch a robot. This week takes one paper from each side, MATT on people and AHA on robots, and neither cites the other side's work on the problem. Both say a yes or no is not enough, and both build their training mistakes out of correct data. They differ on what the answer should be: what, when and where, or why. MATT comes from this course's instructors, so challenge it as hard as AHA.

| paper | why |
|---|---|
| Mistake Attribution (MATT). Li, Jain, Bellos and Corso, CVPR 2026. [arXiv](https://arxiv.org/abs/2511.20525) · [code](https://github.com/yayuanli/MATT) | Say what, when and where. The model takes an instruction and a first-person video of someone attempting it. It reports which part of the instruction was broken (the verb or the object), the frame after which the mistake cannot be undone, and a box around the mistake in that frame. It builds training mistakes by pairing an instruction with a video labeled as a different action, which with some correct pairs gives 257,584 samples from Ego4D and 221,094 from EPIC-KITCHENS. On the Ego4D test samples GPT-4o also saw, it finds the broken part at 55.41 F1, against 50.95 for GPT-4o. On EgoPER, a dataset of recorded mistakes, it detects mistakes at 26.78 F1 when trained from scratch, below both existing detectors tested (28.54 and 32.18). Pretrained on its EPIC-KITCHENS samples and then fine-tuned on EgoPER, it passes them at 35.18. |
| AHA. Duan et al., ICLR 2025. [arXiv](https://arxiv.org/abs/2410.00371) · [code](https://github.com/NVlabs/AHA) | Say why. The model takes a description of one step of a robot task and a grid of key frames from the robot's cameras. It answers yes or no, and after a no it writes a sentence saying why the step failed. It is LLaVA fine-tuned on 49,000 image-question pairs from simulated failed runs, plus general image data. The failures come from editing successful demonstrations in seven ways, such as a slip or picking the wrong object. On RoboFail, failures recorded while a person teleoperated a real robot arm, it gets the yes or no right 64.3% of the time, against 57.1% for GPT-4o given five examples. Three simulated robot systems used its feedback for rewards, plans and step checks, and their task success was 21.4% higher on average than with GPT-4o or GPT-4V. |

Prepare the five PACES rows for both.

## Theme debate

Should a person's mistakes and a robot's failures be checked the same way?

Motion: one model trained on people and robots can match a specialist for each.

- Task: a person or a robot arm does one step of a kitchen task, such as putting an apple in a bowl.
- Measure: how often the model is right that the step failed, and right about what went wrong.
- For: both papers ask whether what the camera saw matches the instruction. A wrong object is the same event for a person told to pick up a hammer who picks up a bolt, and for a gripper told to pick the red cup that picks the green one. Both models also cross boundaries already. MATT's single model beats the task-specific baselines on the broken part and on the frame. AHA, fine-tuned in one simulator, beats GPT-4o with five examples in another simulator and on a real arm, where the failures were recorded under a person's control.
- Against: MATT's single model still loses to a box specialist, 59.21 mIoU against SSDA's 64.54, and its frame and box scores improve when its verb-and-object head is removed. Five of AHA's seven failure modes are failures of execution. The gripper never closed, the object slipped, the position was off, the rotation was wrong, or the rotation never happened. They make up about 92% of AHA's training pairs, and a wrong object only 0.4%. For these, MATT could flag the verb and point to a frame and a box, but could not say what went wrong with the motion.
