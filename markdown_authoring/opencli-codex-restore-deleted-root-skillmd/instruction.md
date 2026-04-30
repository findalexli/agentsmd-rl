# [codex] restore deleted root SKILL.md

Source: [jackwener/OpenCLI#609](https://github.com/jackwener/OpenCLI/pull/609)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `SKILL.md`

## What to add / change

## What changed
Restored the deleted root `SKILL.md` file to the repository and aligned its frontmatter version to `1.5.6`.

## Why
`SKILL.md` was removed in PR #386 as part of unrelated ONES adapter work, which left the root skill guide missing from `main`. This PR brings it back as an isolated follow-up fix.

## Impact
The repository once again includes the root `SKILL.md` guidance file for agents and contributors.

## Validation
- `npm run typecheck`
- `npm test`

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
