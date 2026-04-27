# feat(skill): add pr-ship end-to-end PR lifecycle skill

Source: [iOfficeAI/AionUi#2623](https://github.com/iOfficeAI/AionUi/pull/2623)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/pr-ship/SKILL.md`
- `AGENTS.md`

## What to add / change

## Summary

- Add new `pr-ship` skill (`.claude/skills/pr-ship/SKILL.md`) that shepherds a PR from creation to merge in a single invocation
- Orchestrates existing skills (`oss-pr`, `pr-review`, `pr-fix`) with ScheduleWakeup-based CI polling (270s intervals)
- Supports `--no-auto-merge` flag for manual merge confirmation and `pr_number` argument for session recovery
- Register `pr-ship` in the AGENTS.md skills index table

## Test plan

- [ ] Invoke `/pr-ship` on a feature branch with pending changes — verify full lifecycle (create PR, CI wait, review, merge)
- [ ] Invoke `/pr-ship <pr_number>` on an existing PR — verify resume path initializes state correctly
- [ ] Verify CI failure handler respects retry limit (max 3)
- [ ] Verify `--no-auto-merge` flag shows summary and waits for user confirmation

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
