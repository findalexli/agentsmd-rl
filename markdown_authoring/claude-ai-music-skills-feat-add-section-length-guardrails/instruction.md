# feat: add section length guardrails by genre

Source: [bitwize-music-studio/claude-ai-music-skills#12](https://github.com/bitwize-music-studio/claude-ai-music-skills/pull/12)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`
- `skills/lyric-writer/SKILL.md`

## What to add / change

## Summary
- Adds per-section line limits for 12 genre families covering all 67 documented genres to the lyric-writer skill
- Long sections cause Suno to rush vocals, compress music, and skip lyrics — these are now hard-enforced limits
- Section length check added as item #7 in the Automatic Quality Check (both SKILL.md and CLAUDE.md)
- Added to the Lyric Pitfalls Checklist as a checkable item

## Genre families covered
Hip-Hop/Rap, Pop, Rock, Punk/Hardcore, Metal, Country/Folk, Electronic/EDM, Ambient/Lo-Fi, R&B/Soul, Jazz, Reggae/Dancehall, Ballad (cross-genre)

## Test plan
- [ ] Verify lyric-writer skill loads and parses the new tables
- [ ] Write test lyrics for hip-hop (verse >8 lines should trigger trim)
- [ ] Write test lyrics for electronic (verse >6 lines should trigger trim)
- [ ] Confirm quality check #7 fires during automatic review
- [ ] Run `/bitwize-music:test all` to verify no regressions

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
