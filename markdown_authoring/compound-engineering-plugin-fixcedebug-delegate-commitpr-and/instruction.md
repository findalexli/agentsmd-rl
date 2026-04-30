# fix(ce-debug): delegate commit/PR and add branch check

Source: [EveryInc/compound-engineering-plugin#683](https://github.com/EveryInc/compound-engineering-plugin/pull/683)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `plugins/compound-engineering/skills/ce-commit-push-pr/SKILL.md`
- `plugins/compound-engineering/skills/ce-commit/SKILL.md`
- `plugins/compound-engineering/skills/ce-debug/SKILL.md`
- `plugins/compound-engineering/skills/ce-pr-description/SKILL.md`

## What to add / change

## Summary

Bug fixes through ce-debug now offer "save locally" or "commit, push, and PR" as distinct handoff actions, routing to `/ce-commit` and `/ce-commit-push-pr` instead of a hand-rolled stage-and-commit step. The dedicated skills already encode convention detection, default-branch guards, and conventional-commit fallback, so debug fixes inherit any future commit-hygiene improvements. Phase 4 also separates additive options (`/ce-compound`, issue-tracker reply) from terminal ones; the additive ones re-prompt after running so the user still gets to commit or ship. Phase 3 gains an upfront default-branch check so fixes do not accidentally land on main; the same guard already exists inside the commit skills but fires after the fix is edited.

## Commit conventions update

Writing this PR's title surfaced a recurring agent failure mode: a defect remedy that adds code (a new check, a new option, restored missing behavior) gets labeled `feat:` because the diff shape looks feature-like. The fix lives on two surfaces:

- **Repo `AGENTS.md`** (loaded for contributors) gains a fix-vs-feat disambiguation bullet with a regression-test heuristic, plus a separate bullet requiring explicit user confirmation before applying `!` or `BREAKING CHANGE:` (which release-please reads as an automatic major version bump). The prior "must be explicit" framing actively invited the marker; the replacement defaults to surfacing suspected breakage to the user instead.
- **`ce-commit`, `ce-commit-pus

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
