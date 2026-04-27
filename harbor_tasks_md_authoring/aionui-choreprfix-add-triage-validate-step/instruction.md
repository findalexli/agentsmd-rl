# chore(pr-fix): add triage & validate step before fixing review issues

Source: [iOfficeAI/AionUi#2244](https://github.com/iOfficeAI/AionUi/pull/2244)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/pr-fix/SKILL.md`

## What to add / change

## Summary

- Add **Step 4 — Triage & Validate** to `pr-fix` skill: independently verify each review issue before fixing (3-layer check: is issue real → is fix reasonable → is there a better alternative)
- CRITICAL issues cannot be auto-dismissed in automation mode — escalates to `bot:needs-human-review` for human confirmation
- Verification report now includes a **Triage 决策** section showing dismissed and alternative-fix decisions with reasoning

## Test plan

- [ ] Run `/pr-fix` on a PR with known false-positive review issues — verify triage correctly dismisses them
- [ ] Run `/pr-fix --automation` on a PR with a CRITICAL false-positive — verify it escalates to `bot:needs-human-review` instead of dismissing
- [ ] Run `/pr-fix` on a PR with suboptimal review suggestions — verify triage proposes better alternatives within scope
- [ ] Verify the verification report comment includes the Triage 决策 table

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
