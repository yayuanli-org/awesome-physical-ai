# Dev setup

## Requirements

Python 3 (stdlib only) and a browser. Nothing else. There is no virtualenv, no
`requirements.txt`, no package manager, and adding one would break the property that
someone can clone this and open the page.

## Commands

All from the repo root. `build.py` resolves its own paths, so it runs from anywhere.

```sh
python3 paper-hub/build.py                              # rebuild both pages
python3 paper-hub/build.py --check                      # validate, write nothing
python3 .claude/skills/dev-test/tests/test_database.py  # full test surface
open paper-hub/index.html                               # the deliverable (macOS)
cd paper-hub && python3 serve.py                        # then open review.html to mark up
```

`build.py` prints the paper count, the arc split, and any value used in the data that
is not declared in `data/schema.json`. That last line is a notice, not an error — the
vocabulary is meant to grow — but a value that shows up there and is not intentional is
usually a typo.

## Reviewing the draft

`review.html` is `index.html` plus an in-page comment layer. Select any text or element,
leave a comment, and it threads in a side panel.

```sh
cd paper-hub && python3 serve.py    # localhost:8777, static files + a comment write-back API
```

`serve.py` serves and writes in its cwd, which is why it runs from inside `paper-hub/`.

Comments persist to `physai.comments.json` beside the page, which is what makes them
readable between sessions. Opened over `file://` instead, the layer still works but
falls back to `localStorage`, so nothing reaches disk and no one else can see it.

`serve.py` is also the way to drive either page with browser automation, since the
Chrome extension refuses `file://` URLs. Humans opening `index.html` by hand need
none of this.

## Grounding a new paper against arXiv

The maintainer's captured papers live in `~/fun/enjoy/orgmode/roam/papers/` (~400 org
files, one per paper, with an `:Paper_Link_arxiv_abs:` property on most). To pull real
titles, abstracts, author lists and accepted venues in bulk:

```
http://export.arxiv.org/api/query?id_list=<id>,<id>,...&max_results=100
```

Up to 50 ids per call. The `arxiv:comment` field usually names the accepted venue,
which is where the `venue` column comes from. Title search works when the id is
missing, but verify the returned title actually matches — the API returns a
best-effort result and has silently handed back unrelated papers.

Two environment notes: the Bash sandbox blocks network, so these calls need
`dangerouslyDisableSandbox`; and the API is rate-limited, so sleep ~3 s between calls.

## Git

Single `main` branch, one maintainer, no PR flow. Neither page is committed; CI builds
them on every push. If this ever grows collaborators, the main-only fallback in
`~/.claude/skills/git-for-ai-teams/` is the upgrade path.
