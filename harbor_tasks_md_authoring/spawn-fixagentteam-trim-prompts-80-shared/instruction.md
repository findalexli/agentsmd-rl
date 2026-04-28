# fix(agent-team): trim prompts 80% — shared rules + teammate micro-prompts

Source: [OpenRouterTeam/spawn#3315](https://github.com/OpenRouterTeam/spawn/pull/3315)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/setup-agent-team/_shared-rules.md`
- `.claude/skills/setup-agent-team/discovery-team-prompt.md`
- `.claude/skills/setup-agent-team/qa-quality-prompt.md`
- `.claude/skills/setup-agent-team/refactor-team-prompt.md`
- `.claude/skills/setup-agent-team/security-review-all-prompt.md`
- `.claude/skills/setup-agent-team/teammates/qa-code-quality.md`
- `.claude/skills/setup-agent-team/teammates/qa-dedup-scanner.md`
- `.claude/skills/setup-agent-team/teammates/qa-e2e-tester.md`
- `.claude/skills/setup-agent-team/teammates/qa-record-keeper.md`
- `.claude/skills/setup-agent-team/teammates/qa-test-runner.md`
- `.claude/skills/setup-agent-team/teammates/refactor-code-health.md`
- `.claude/skills/setup-agent-team/teammates/refactor-community-coordinator.md`
- `.claude/skills/setup-agent-team/teammates/refactor-complexity-hunter.md`
- `.claude/skills/setup-agent-team/teammates/refactor-pr-maintainer.md`
- `.claude/skills/setup-agent-team/teammates/refactor-security-auditor.md`
- `.claude/skills/setup-agent-team/teammates/refactor-style-reviewer.md`
- `.claude/skills/setup-agent-team/teammates/refactor-test-engineer.md`
- `.claude/skills/setup-agent-team/teammates/refactor-ux-engineer.md`
- `.claude/skills/setup-agent-team/teammates/security-issue-checker.md`
- `.claude/skills/setup-agent-team/teammates/security-pr-reviewer.md`
- `.claude/skills/setup-agent-team/teammates/security-scanner.md`

## What to add / change

## Summary

Phase 2+3 of the token-savings plan. Follows #3310 (cron + Sonnet leads, already merged).

Extracts duplicated rules into a shared file and moves teammate protocols into individual micro-prompts. Team leads read them on-demand via Read tool instead of carrying 300+ lines in every monitoring-loop turn.

## Changes

**New: \`_shared-rules.md\`** (72 lines) — Off-Limits, Diminishing Returns, Dedup, PR Justification, Worktrees, Commit Markers, Monitor Loop, Shutdown Protocol, Comment Dedup, Sign-off. Referenced by all 4 team prompts.

**New: \`teammates/\`** (16 files, 246 lines total) — one per role:
- \`refactor-*\`: security-auditor, ux-engineer, complexity-hunter, test-engineer, code-health, pr-maintainer, style-reviewer, community-coordinator
- \`security-*\`: pr-reviewer, issue-checker, scanner (merged shell+code into one)
- \`qa-*\`: test-runner, dedup-scanner, code-quality, e2e-tester, record-keeper

**Rewritten prompts:**

| File | Before | After | Reduction |
|---|---|---|---|
| refactor-team-prompt.md | 319 | 67 | 79% |
| security-review-all-prompt.md | 245 | 64 | 74% |
| qa-quality-prompt.md | 302 | 43 | 86% |
| discovery-team-prompt.md | 333 | 69 | 79% |
| **Total** | **1,199** | **243** | **80%** |

## Why this doesn't regress agent quality

Rules and protocols are identical — moved, not rewritten. Each teammate gets the same instructions via Read tool at spawn time. The team lead's monitoring loop carries 67 lines instead of 319, which is cheaper per tu

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
