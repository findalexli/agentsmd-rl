# feat: verse-chorus echo check (phrase deduplication)

Source: [bitwize-music-studio/claude-ai-music-skills#19](https://github.com/bitwize-music-studio/claude-ai-music-skills/pull/19)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`
- `skills/lyric-writer/SKILL.md`

## What to add / change

## Summary
- **Replaces Chorus Lead-In Rule** with comprehensive **No Verse-Chorus Echo** check
- Expanded scope: compares last 2 lines of every verse (not just last line) against first 2 lines of chorus
- Flags 4 overlap types: exact phrases, shared rhyme words, restated hooks, shared signature imagery
- Applies to ALL transitions: verse-to-chorus AND bridge-to-chorus
- Quality check #11 updated from "chorus lead-in" to "verse-chorus echo"
- Pitfalls checklist item updated to match

## Test plan
- [ ] Verify "No Verse-Chorus Echo" section in SKILL.md under Verse/Chorus Contrast
- [ ] Verify quality check #11 updated in both SKILL.md and CLAUDE.md
- [ ] Verify pitfalls checklist item updated
- [ ] Verify example (bad/good) still present

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
