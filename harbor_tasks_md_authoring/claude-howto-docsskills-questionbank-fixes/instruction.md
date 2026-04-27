# docs(skills): question-bank fixes

Source: [luongnv89/claude-howto#97](https://github.com/luongnv89/claude-howto/pull/97)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/lesson-quiz/references/question-bank.md`

## What to add / change

## Description
Fixes incorrect question options in a question-bank for lessons `Lesson 03: Skills`,  `Lesson 04: Subagents`

## Type of Change
- [ ] New example or template
- [X] Documentation improvement
- [ ] Bug fix
- [ ] Feature guide
- [ ] Other (please describe)

## Related Issues
None

## Changes Made
- Changed question options to be aligned with lessons README.md

## Files Changed
- `.claude/skills/lesson-quiz/references/question-bank.md`

## Testing
How have you tested this?
- [ ] Tested locally with Claude Code
- [ ] Verified examples work
- [ ] Checked links and references
- [X] Reviewed for typos and clarity

## Checklist
- [X] Follows project structure and conventions
- [X] Includes clear documentation/examples
- [X] Code/examples are copy-paste ready
- [X] All links are verified and working
- [X] No sensitive information included (keys, tokens, credentials)
- [X] Updated relevant README files
- [X] Commit message follows conventional commit format
- [X] No large files (>1MB) added

## Screenshots or Examples
None

## Breaking Changes
Does this change any existing content or behavior?
- [X] No breaking changes
- [ ] Yes, and it's documented below

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
