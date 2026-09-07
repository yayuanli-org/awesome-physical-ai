# Committed but not urgent (P2)

- **[P2] Coverage pass from the captured-papers KB.** ~400 papers in
  `~/fun/enjoy/orgmode/roam/papers/`, of which roughly 110 are in the list. The
  add-a-paper flow and the arXiv batch recipe make this mechanical. Likely the first
  theme worth a `present/themes/` file.
- **[P2] Thin axes that are honest but sparse.** `change_channel: fabrication` has one
  paper, `sensing: tactile` has two, `contribution: survey` has two. Each is a real
  category with a real literature behind it; the list just has not reached it yet.
- **[P2] Sub-taxonomy for the robot arc.** "Robot as the embodiment" holds 21 papers
  and is the largest group. The VLA survey's action-token axis (language / code /
  affordance / trajectory / goal state / latent / raw action / reasoning) is a ready-made
  split if it grows further.
- **[P2] A "read next" edge between papers.** Several `why` fields already say "read
  next to X". Making that a real column would give the page a reading-path view.
- **[P2] Re-vendor `src/comment-layer.{css,js}` from the `commentable-html` skill.**
  The page forked the copy on 2026-08-24 (markers on the anchor's left edge, scroll-aware
  placement) and the skill moved on independently on 2026-08-30 (comments chip in place
  of the floating button, comment-mode switch inside the panel, timezone-safe
  timestamps). Neither side has the other's fixes. Port the marker work upstream first,
  then re-copy, then re-check `template.html`'s palette overrides against the new class
  names.
