---
name: dev-test
description: >
  The validation surface for awesome-physical-ai. One dependency-free script,
  tests/test_database.py, that enforces every mechanizable rule in
  dev-handbook/conventions.md: schema conformance, vocabulary coverage, view-filter
  integrity, prose voice, and build freshness. TRIGGER when: about to commit, after
  adding or editing a paper, after changing data/schema.json or src/template.html,
  when the user asks "run the tests", "is the data valid", "did I break anything",
  when a build notice mentions an undeclared value, or after touching the review
  comment layer. Do NOT trigger for: what a
  column means or why the taxonomy is shaped this way (→ dev-handbook), what shipped
  or what is next (→ dev-journal).
---

# dev-test

## Run it

```sh
python3 .claude/skills/dev-test/tests/test_database.py
```

Stdlib only, no pytest required, exits nonzero on failure. It also collects under
`pytest .claude/skills/dev-test/` if pytest happens to be installed.

Prints one line per check, then `N/M passed`. Currently 23 checks. `python3
paper-hub/build.py --check` is the faster subset when you only want the paper count
and the undeclared-value notice. Every path in the script hangs off `HUB`, which is
`paper-hub/` under the repo root.

## What it covers, and why each check exists

Every check maps to a rule in `../dev-handbook/conventions.md`. Adding a convention
without adding a check leaves the convention as folklore.

| Group | Checks | The rule being enforced |
|---|---|---|
| Data shape | `ids_unique_and_slugged`, `required_fields`, `dates_consistent`, `confidence_declared`, `links_are_urls`, `cells_are_short` | ids are stable deep-link anchors; short cells |
| No folders | `no_grouping_fields` | sections are filters over columns, so a paper never names its own section |
| Schema conformance | `values_declared`, `modalities_declared`, `dataset_roles_declared` | a value enters the schema before it enters the data |
| Coverage | `no_empty_vocabulary_values` | an axis with no members is an untested claim about the field |
| View integrity | `view_filters_reference_real_columns`, `every_group_claims_something`, `group_priorities_are_unique` | a filter on a typo'd column silently matches nothing; a group nobody lands in is dead weight |
| Prose voice | `no_clause_welding`, `no_antithesis`, `no_blacklist_words`, `schema_prose_is_clean` | the `Plain` style, applied to everything user-visible including the schema's own blurbs |
| Build health | `build_is_current`, `page_is_self_contained`, `embedded_json_parses`, `review_scaffolding_is_stripped` | both pages are generated from one template, and the review layer must never reach the deliverable |
| Publishing | `site_artifact_is_minimal` | Pages deploys `build.py --site`, not the repo tree, so this check is what keeps `build.py`, `serve.py` and `.claude/` off the public site |

## What it does not cover

- **Whether the numbers are true.** `experiments.headline` figures must come from the
  paper's abstract. The check is a human one: pull the abstract from the arXiv API and
  diff. See `../dev-handbook/dev-setup.md` for the recipe. A pass over 110 papers found
  two paraphrases carrying figures the abstract did not state.
- **Whether a `tldr` states a claim rather than a topic.** Judgment.
- **Whether an institution is correct.** Left empty when uncertain, by convention.
- **Whether the page looks right.** Open it.

## Editing the prose checks

`test_no_clause_welding` has one subtlety worth knowing before you loosen it: a *pair*
of em-dashes brackets an appositive and is legitimate, while a *lone* em-dash followed
by a finite clause is a weld. The check counts occurrences to tell them apart. Two
earlier versions of this check produced a wall of false positives on legitimate
parentheticals.

`test_no_blacklist_words` exempts a word when it appears in the paper's own title,
because titles are quotations and stay verbatim. That is why "Learning **Robust**
Visual Features" passes and a headline calling a trajectory "robust" does not.

## Adding a check

1. Write the convention in `../dev-handbook/conventions.md` first, in "use X, not Y" form.
2. Add a `test_*` function here. It is picked up automatically by name.
3. Note the enforcement in the conventions entry (`*Enforced:* test_name`).
4. If the rule cannot be mechanized, say so in the conventions entry instead. A
   documented why-not is better than a silent gap.
