# Add table structure guidelines to CLAUDE.md

Source: [trailofbits/publications#647](https://github.com/trailofbits/publications/pull/647)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
- Add explicit column structure for security review tables (`| Product | Date | Effort | Announcement | Report |`) with pipe count requirement
- Clarify that truncated rows must be padded with empty cells and extra trailing pipes must be removed
- Generalize the row completeness rule in General Formatting Guidelines to apply to all tables

These gaps were identified while fixing malformed rows (Zama, Dfinity ckBTC, ParaSpace, Aave V3, etc.) in #646.

## Test plan
- [x] Verify CLAUDE.md renders correctly
- [x] Confirm no existing guidelines were removed or contradicted

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
