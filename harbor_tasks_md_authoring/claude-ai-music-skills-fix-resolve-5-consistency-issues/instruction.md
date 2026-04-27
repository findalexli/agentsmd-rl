# fix: resolve 5 consistency issues in SKILL.md and CLAUDE.md

Source: [bitwize-music-studio/claude-ai-music-skills#23](https://github.com/bitwize-music-studio/claude-ai-music-skills/pull/23)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`
- `skills/lyric-writer/SKILL.md`

## What to add / change

## Summary
- **Hip-hop outro conflict**: Table said "Flexible" but structural rule said "2-4 lines max". Aligned to "2-4" with spoken word/ad-lib exemption noted
- **Terminology mismatch**: Section header "Phrase Deduplication" renamed to "No Verse-Chorus Echo" to match quality check #11 terminology
- **Syllable tolerance duplication**: Added Tolerance column to Line Length table (±2 pop/rock, ±3 hip-hop, flexible metal/electronic). Flow Checks now references the table instead of restating values
- **Remember section vague**: Item #1 now specifies reading config for overrides path
- **Model Strategy incomplete**: Added missing researchers-legal and researchers-verifier to Opus tier examples

## Test plan
- [ ] Hip-hop outro table shows "2-4" not "Flexible"
- [ ] Section header says "No Verse-Chorus Echo" (no "Phrase Deduplication")
- [ ] Line Length table has Tolerance column with 4 rows
- [ ] Flow check #3 references "Line Length table"
- [ ] Opus examples list all 6 skills

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
