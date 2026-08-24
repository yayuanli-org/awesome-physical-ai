# Current focus

_Updated [2026-08-24 11:30 PDT]_

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
- Nothing here is a course schedule, and it should stay that way. If reading
  assignments start to leak in as fields, that is the failure mode `mission.md` names.
