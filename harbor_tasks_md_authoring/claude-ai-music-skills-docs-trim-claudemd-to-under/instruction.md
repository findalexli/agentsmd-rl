# docs: trim CLAUDE.md to under 40KB target

Source: [bitwize-music-studio/claude-ai-music-skills#21](https://github.com/bitwize-music-studio/claude-ai-music-skills/pull/21)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
- Consolidated 4 checkpoint sections (Ready to Generate, Generation Complete, Ready to Master, Ready to Release) into single table referencing checkpoint-scripts.md
- Slimmed Model Strategy from per-skill listings to table format with reference to `/reference/model-strategy.md`
- Condensed Lessons Learned Protocol subsections (What Qualifies + Rule Format + Key Principle → 3 lines)
- Removed redundant CORRECT APPROACH block (restated the mandatory steps above it)
- **42.3KB → 39.9KB** (-2.4KB), no information lost

## Test plan
- [ ] All checkpoint triggers/actions still documented (now in table)
- [ ] Model strategy tiers still clear
- [ ] No broken internal references

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
