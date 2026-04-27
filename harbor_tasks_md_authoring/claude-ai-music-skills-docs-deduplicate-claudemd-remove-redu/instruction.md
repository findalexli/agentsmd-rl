# docs: deduplicate CLAUDE.md, remove redundant sections

Source: [bitwize-music-studio/claude-ai-music-skills#20](https://github.com/bitwize-music-studio/claude-ai-music-skills/pull/20)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
- Removed 5 areas of duplication identified in CLAUDE.md sanity check review
- **Quick Reference: Lyric Writing** — all 5 points already covered by the 12 quality checks in Automatic Lyrics Review
- **Using Skills for Research** — a 5-row subset of the full 10-row Specialized Researchers table
- **Standalone Watch Your Rhymes** — fully covered by quality check #1 and pitfalls checklist
- **Pronunciation check #3 sub-items** — now references the standalone Pronunciation section instead of re-listing 7 items
- **Session Start config loading** — now references Path Resolution section instead of re-explaining paths
- Net reduction: 90 lines removed with no loss of information

## Test plan
- [ ] Verify no broken internal references in CLAUDE.md
- [ ] Confirm all removed content exists elsewhere in the document
- [ ] Session start still references config loading correctly

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
