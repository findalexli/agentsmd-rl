# Add AGENTS.md file

Source: [prometheus/prometheus#18282](https://github.com/prometheus/prometheus/pull/18282)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

Created by AI and tweaked by me; prompt was:

> can you make an AGENTS.md file based on the last 20 PRs that were
> accepted, telling agents what maintainers like

I'm very open to suggestions to make `AGENTS.md` even better, if they come from experience.
Not interested in bike-shedding.

#### Does this PR introduce a user-facing change?
```release-notes
NONE
```

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
