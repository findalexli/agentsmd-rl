# docs: improve CLAUDE.md with progressive disclosure (VM-342)

Source: [mbailey/voicemode#169](https://github.com/mbailey/voicemode/pull/169)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`
- `agents.md`

## What to add / change

## Summary
- Improves CLAUDE.md structure with progressive disclosure
- Adds skill loading guidance
- Enhances correctness of documentation

## Test plan
- [ ] Review CLAUDE.md is clear and accurate
- [ ] Verify skill loading instructions work
- [ ] Check progressive disclosure aids understanding

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
