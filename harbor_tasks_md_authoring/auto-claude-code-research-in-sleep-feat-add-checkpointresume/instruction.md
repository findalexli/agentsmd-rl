# feat: add checkpoint/resume to research-refine skill

Source: [wanshuiyin/Auto-claude-code-research-in-sleep#61](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep/pull/61)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/research-refine/SKILL.md`

## What to add / change

Add REFINE_STATE.json checkpoint mechanism so that research-refine can recover from mid-run failures (API timeout, context compaction, session interruption) without losing completed phases.

Changes:
- Add State Persistence section with JSON schema and field definitions
- Add Initialization section with fresh-start vs resume logic (24h expiry)
- Add checkpoint writes after each phase boundary (Phase 0-5)
- Add REFINE_STATE.json to Output Structure

Follows the same pattern as auto-review-loop's REVIEW_STATE.json.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
