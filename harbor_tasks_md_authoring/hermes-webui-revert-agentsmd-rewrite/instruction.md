# revert: AGENTS.md rewrite

Source: [nesquena/hermes-webui#114](https://github.com/nesquena/hermes-webui/pull/114)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Revert PR #113.

The AGENTS.md rewrite contained a lot of repo-internal operational context that does not belong in the public repo:
- absolute paths
- private repo name / sync instructions
- server ports and runtime locations
- internal file inventory and workflow details

This revert restores the prior, minimal AGENTS.md.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
