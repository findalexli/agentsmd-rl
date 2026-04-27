# fix(git-commit-push-pr): simplify PR probe pre-resolution

Source: [EveryInc/compound-engineering-plugin#513](https://github.com/EveryInc/compound-engineering-plugin/pull/513)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md`

## What to add / change

## Summary

Replaces `$()` command substitution in the skill's pre-resolution backtick expression with a simple `|| echo 'NO_OPEN_PR'` sentinel pattern. This fixes failures in environments (e.g., Conductor) where complex shell expressions in `!` backtick pre-resolution may not evaluate correctly.

- Removed the "Reusable PR probe" instructional section — pre-resolution handles Claude Code, the context fallback block handles other agents
- Simplified PR check interpretation to single-sentence conditionals using deterministic sentinels
- Normalized sentinel style (`NO_OPEN_PR`, `DEFAULT_BRANCH_UNRESOLVED`) for consistency

## Test plan

- [ ] Run `/git-commit-push-pr` in Claude Code on a branch with an existing PR — verify it detects the open PR
- [ ] Run on a branch with no PR — verify `NO_OPEN_PR` sentinel appears and skill proceeds to create one
- [ ] Run in Conductor workspace — verify no pre-resolution errors

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
