# Current focus

_Updated [2026-09-07 14:25 PDT]_

**The repo is two parts now, and the course part is empty.** `paper-hub/` is the list
and its page, unchanged. `courses/umich-26fall-rob599-physically-grounded-ai-agents/`
is where the semester's material goes. The first thing due there is a lecture notebook
that sums up the hub and shares opinions, built with `doc-jupyter` from prompts the
maintainer has ready. Debate sessions follow.

**Framework is done; coverage is the next axis.** The taxonomy held up against 110
papers spanning egocentric procedural understanding, world models, VLAs, mistake
detection, HOI, 3D/4D, and guidance systems. Two things bent under load and were fixed
(the objects group, the group-priority mechanism); nothing broke. That is the signal
the framework was the right thing to spend the first pass on.

What the repo is now: a JSON database of 110 papers, a schema that documents its own
columns, one self-contained HTML page over it, and a 21-check validator that keeps the
conventions from rotting into folklore.

**Not yet done, and deliberately so.** Coverage is uneven by design — dense where the
taxonomy needed stress-testing, thin elsewhere. Filling it out is mechanical now that
the framework and the add-a-paper flow are written down.

**A review loop now exists.** `review.html` carries an in-page comment layer and
`serve.py` persists the threads to disk, so the draft can be marked up and the marks
read back between sessions. The deliverable is unaffected — the scaffolding is stripped
from `index.html` and a test keeps it that way.

**Open questions worth revisiting before the semester:**

- Does the `Scenes, 3D and 4D` group earn its place, or should geometry fold into the
  representation filter? It currently holds 7 papers, several of which are background
  reading rather than physical-AI papers.
- The loop view is honest but passive — it filters and lists. Something that showed
  *where* each system closes its loop, rather than just that it does, would use the
  `loop_stage` column harder.
- `loop_stage: adapt` reads "change the policy or the model from the outcome", which
  admits offline fine-tuning on collected rollouts (EnvHarness carries it) as well as
  learning at run time. If the tag is meant to single out online learning, the help
  text has to say so and the tagged papers need a re-read. Raised 2026-09-07.
- Course material has its own folder now. The failure mode `mission.md` names is still
  worth watching: reading assignments must not leak into the hub as fields.
