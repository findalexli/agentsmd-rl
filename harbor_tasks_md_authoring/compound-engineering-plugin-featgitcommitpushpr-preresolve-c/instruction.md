# feat(git-commit-push-pr): pre-resolve context to reduce bash calls

Source: [EveryInc/compound-engineering-plugin#488](https://github.com/EveryInc/compound-engineering-plugin/pull/488)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md`
- `plugins/compound-engineering/skills/git-commit/SKILL.md`

## What to add / change

## Summary

Reduces the number of individual bash calls in the `git-commit-push-pr` and `git-commit` skills by pre-resolving read-only context on Claude Code and chaining commands elsewhere.

The screenshot that motivated this: a typical "ship this" invocation was producing 9 separate bash tool calls — the first 4-5 were pure info-gathering (git status, diff, branch, log, default branch, PR check) that could be eliminated or consolidated.

## Approach

**Claude Code path:** A new `## Context` section uses `!` backtick pre-resolution to populate git status, working tree diff, current branch, recent commits, remote default branch, and (for git-commit-push-pr) existing PR check before the skill body executes. The model sees populated data and uses it directly — zero bash calls for context gathering.

**Non-CC path:** The same section gates with "If you are not Claude Code, skip to Context fallback" at the top, directing to a single combined command that gathers all context in one bash call. The fallback section has a reciprocal gate ("If you are Claude Code, skip this section") so CC doesn't redundantly run it.

**Action-phase optimizations (all platforms):**
- Stage + commit chained into one call per commit group (`git add && git commit`)
- Step 6 scope gathering in git-commit-push-pr (verify ref, merge-base, log, diff) consolidated from 4 separate code blocks to 2

| Phase | Before | After (CC) | After (non-CC) |
|-------|--------|------------|-----------------|
| Context gath

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
