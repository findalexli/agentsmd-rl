# feat(skills): add skill-upstream-pr for contributing improvements to public skills

Source: [luongnv89/asm#244](https://github.com/luongnv89/asm/pull/244)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/skill-upstream-pr/SKILL.md`
- `skills/skill-upstream-pr/docs/README.md`
- `skills/skill-upstream-pr/references/pr-template.md`
- `skills/skill-upstream-pr/references/tone-guide.md`

## What to add / change

## Summary
- Adds the `skill-upstream-pr` skill: a workflow for forking a public skill repo, running `skill-auto-improver`, and opening a friendly suggestion PR back to the upstream maintainer.
- Ships with references: a PR body template (`references/pr-template.md`) and a tone guide (`references/tone-guide.md`) so the generated PR stays polite and suggestion-shaped.
- Adds a human-only `docs/README.md` (not auto-loaded into agent context).

## Context
Split from #243 — that PR now only contains the `author`/`creator` evaluator rename. This PR carries the skill addition that was accidentally bundled in the same branch.

The underlying commit (`d12aac7`) is unchanged and already passed CI on the combined branch.

## Test plan
- [x] Pre-commit hooks pass (prettier + typecheck + unit tests)
- [x] Pre-push hooks pass (build + e2e)
- [ ] CI green on this branch

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
