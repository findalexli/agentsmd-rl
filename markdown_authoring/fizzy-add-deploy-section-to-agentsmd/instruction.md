# Add Deploy section to AGENTS.md

Source: [basecamp/fizzy#2593](https://github.com/basecamp/fizzy/pull/2593)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary
Adds structured Deploy section with default branch (`main`), pre-deploy step (`bin/rails saas:enable`), deploy command, and 7 destinations. Format is parsed by the coworker dev-prelude and `verify-app-registry` drift gate.

## Test plan
- [ ] `bin/verify-app-registry` (in coworker repo) exits 0

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
