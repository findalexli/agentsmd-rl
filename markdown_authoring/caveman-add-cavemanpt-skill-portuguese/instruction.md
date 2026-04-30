# Add caveman-pt skill (Portuguese)

Source: [JuliusBrussee/caveman#41](https://github.com/JuliusBrussee/caveman/pull/41)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `caveman-pt/SKILL.md`
- `skills/caveman-pt/SKILL.md`

## What to add / change

## Summary
- Adds `caveman-pt`, a Portuguese localization of the caveman skill
- Includes SKILL.md in both `caveman-pt/` and `skills/caveman-pt/` directories
- Same structure and intensity levels (lite, full, ultra) as the original, fully translated to Portuguese

## Details
- Maintains all technical accuracy while communicating in Portuguese
- Follows the same pattern as other localized skills (e.g., `caveman-es`, `caveman-cn`)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
