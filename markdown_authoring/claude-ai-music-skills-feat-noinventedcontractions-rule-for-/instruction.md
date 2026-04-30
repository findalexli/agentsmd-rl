# feat: no-invented-contractions rule for Suno

Source: [bitwize-music-studio/claude-ai-music-skills#18](https://github.com/bitwize-music-studio/claude-ai-music-skills/pull/18)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`
- `skills/lyric-writer/SKILL.md`

## What to add / change

## Summary
- **No Invented Contractions rule** added to Pronunciation section in lyric-writer SKILL.md — Suno only handles standard pronoun/auxiliary contractions (they'd, wouldn't), not noun'd/brand'd forms (signal'd, TV'd)
- Pronunciation quality check (#3) updated to include invented contractions
- New pitfalls checklist item for invented contractions
- CLAUDE.md pronunciation check updated with the rule

## Test plan
- [ ] Verify rule appears in SKILL.md Pronunciation section after Homograph Handling
- [ ] Verify quality check #3 mentions invented contractions
- [ ] Verify pitfalls checklist includes invented contractions item
- [ ] Verify CLAUDE.md pronunciation check includes the rule

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
