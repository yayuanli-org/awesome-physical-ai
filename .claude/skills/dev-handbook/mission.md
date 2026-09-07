# Mission

## What this exists to achieve

A reference for physical AI that a researcher outside the course would use. The course
is the occasion, not the audience.

ROB 599, Physically-Grounded AI Agents (UMich, Fall 2026) is a paper-reading course.
Its open deliverable is this list. The bet in the project note is that with enough
attention it could become to physical AI what cs231n's reading list was to vision — so
the list is written for someone who has never heard of the course, and carries no
schedule, no lecture numbers, and no assignments. Those live beside it in `courses/`,
one folder per course, which is where the hub gets summed up and debated.

## What makes it different from the lists that already exist

Similar repos exist. The claim here is not coverage, it is taxonomy.

Most awesome-lists are a nested outline: papers filed under headings, one home each.
That shape cannot answer a cross-cutting question, and it forces a false choice for the
many papers that both model the world and act in it. This one is a database with a
view layer, so "show me everything that closes the loop", "show me every paper where
the human is the actuator", and "show me every verify-stage paper regardless of
embodiment" are all one click.

The second difference is the per-paper structure. Every entry carries the paper's
inference-time inputs and outputs with modality and tensor shape, what the training
signal was and how it differed, the method's intuition in one or two sentences, and
what the authors did to their data. That is a reading protocol as much as a schema, and
it is written down in `design-rationale.md` and rendered on the page's third tab.

## Horizon

**Now through Fall 2026.** Framework first, papers second. The framework is done; the
110 papers in it exist to stress-test it and to make it useful on day one. Coverage is
deliberately uneven — dense where the taxonomy needed testing (egocentric procedural
understanding, mistake detection, world models, VLAs), thin elsewhere.

**Next.** Fill out coverage from the ~400 captured papers in the maintainer's org-roam
(`~/fun/enjoy/orgmode/roam/papers/`), and from course reading assignments as they are
made. Publish to GitHub as `awesome-physical-ai`.

**Later.** Course projects feed papers back into the list. The repo stays open and
continuously maintained past the semester.

## What would count as failure

- The list becomes a course syllabus with dates in it.
- Sections drift back into folders and papers get filed in one place each.
- Cells grow into paragraphs and the table stops being scannable.
- Numbers appear that are not in the papers.
