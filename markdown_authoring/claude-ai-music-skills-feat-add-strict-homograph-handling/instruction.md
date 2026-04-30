# feat: add strict homograph handling rules for Suno

Source: [bitwize-music-studio/claude-ai-music-skills#14](https://github.com/bitwize-music-studio/claude-ai-music-skills/pull/14)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`
- `skills/lyric-writer/SKILL.md`

## What to add / change

## Summary
- Suno cannot infer pronunciation from context — "context is clear" is never acceptable for homographs
- Added hard process: identify → ASK user → fix with phonetic spelling → document
- Full homograph table with both pronunciations and phonetic spellings (live, read, lead, wound, close, bass, tear, wind)
- Updated both SKILL.md and CLAUDE.md to enforce the same rules

## Test plan
- [ ] Verify lyric-writer flags homographs during pronunciation check
- [ ] Confirm "context is clear" is rejected as resolution
- [ ] Run `/bitwize-music:test all` for regressions

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
