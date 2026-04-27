# harden code review skill for async state and default-resolution bugs

Source: [block/goose#8740](https://github.com/aaif-goose/goose/pull/8740)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/code-review/SKILL.md`

## What to add / change

## Overview

**Category:** improvement
**User Impact:** The code review skill now catches async state, default-resolution, and UI/backend drift bugs that would otherwise slip past review.

**Problem:** Recent bugs (provider/model selections drifting from the backend, sticky defaults overriding explicit user choices, stale dependent state lingering after a parent change) were not being flagged by the code review skill because its checklist had no language for async state, persistence, or fallback-authority issues. The skill also referenced `just ci`, which is not the correct gate command in this repo.

**Solution:** Added a new "Async State, Defaults & Persistence" checklist section, an explicit end-to-end tracing step for stateful UI/async flow changes, and a third self-check pass focused on UI/persisted-state/backend disagreement after failures or handoffs. Replaced the outdated `just ci` references with `just check-everything` and softened the language so the skill defers to whatever the repo's actual pre-push/CI gate is.

<details>
<summary>File changes</summary>

**.agents/skills/code-review/SKILL.md**
Added an "Async State, Defaults & Persistence" checklist covering optimistic updates without rollback, requested-vs-fallback authority, dependent state invalidation, persisted preference validation, fallback compatibility across providers, best-effort lookup degradation, and draft/Home/handoff session paths. Added an end-to-end tracing step (selection -> local state -> pers

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
