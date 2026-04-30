# feat: add Lessons Learned Protocol

Source: [bitwize-music-studio/claude-ai-music-skills#15](https://github.com/bitwize-music-studio/claude-ai-music-skills/pull/15)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
- Adds a Lessons Learned Protocol section to CLAUDE.md (after Mid-Session Workflow Updates)
- 5-step process: fix issue → sweep album → draft rule → present to user → log the lesson
- Covers what qualifies (pronunciation errors, rhyme violations, formatting, assumptions, manual corrections)
- Includes rule format template (what went wrong, why it matters, the rule, examples)
- Key principle: proactively propose rules when issues are corrected, don't wait to be asked

## Test plan
- [ ] Verify section appears after "Mid-Session Workflow Updates" and before "Core Principles"
- [ ] Verify markdown renders correctly
- [ ] Verify no existing content was altered

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
