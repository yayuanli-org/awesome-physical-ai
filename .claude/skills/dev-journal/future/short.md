# Next session (P0, P1)

- **[P0] First lecture notebook.** `courses/umich-26fall-rob599-physically-grounded-ai-agents/lectures/`
  gets the lecture that sums up the hub and shares opinions, as a `doc-jupyter`
  notebook. The maintainer has the prompts.
- **[P1] Publish course pages.** Once a lecture exists, decide how its HTML export
  reaches the site: a copy step in `pages.yml` after `--site`, or a branch in
  `emit_site`. `test_site_artifact_is_minimal` pins the file list and changes either way.
- **[P1] Add a LICENSE.** The page is public with no license on it, which leaves anyone
  who wants to reuse the taxonomy or the JSON guessing. The data and the code want
  different answers — CC BY for `data/`, MIT for `build.py` and the template, is the
  usual split for a curated list.
- **[P1] Second numeric audit over the 27 papers added in the gap-filling pass.**
  The first audit covered the original 83. Recipe is in `../../dev-handbook/dev-setup.md`.
- **[P1] Verify or drop the guessed institutions.** Several entries carry an
  institution inferred from an author list rather than read off the paper. Convention
  says empty beats wrong; these were left in. Either confirm them or clear them.
- **[P0 if it recurs] Watch group balance after the next paper batch.** Adding papers
  shifts which group claims what. Check the counts on the page after each batch.
