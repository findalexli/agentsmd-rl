# feat(run): add interactive context protection guide before polling

Source: [Q00/ouroboros#146](https://github.com/Q00/ouroboros/pull/146)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/run/SKILL.md`

## What to add / change

## Summary
- Adds an interactive `AskUserQuestion` step to the run skill after execution starts, letting users choose their monitoring strategy before entering the polling loop
- Polling interval options: per-level completion (recommended), every 10 minutes, or every 20 minutes
- Users who opt out of polling get clear guidance on monitoring via separate terminal (`ooo status`) or `/clone`
- Prevents unintended context window exhaustion from rapid `job_wait` loop iterations

## Test plan
- [ ] Run `ooo run` with a seed and verify `AskUserQuestion` appears after job starts
- [ ] Select "Poll here" → verify interval question follows
- [ ] Select "Don't poll" → verify monitoring guidance is displayed and polling does not start
- [ ] Verify step numbering (5→6→7→8→9) is sequential and correct

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
