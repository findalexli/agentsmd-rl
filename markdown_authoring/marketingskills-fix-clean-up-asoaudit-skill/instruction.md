# fix: clean up aso-audit skill for cross-agent compatibility

Source: [coreyhaines31/marketingskills#221](https://github.com/coreyhaines31/marketingskills/pull/221)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/aso-audit/SKILL.md`

## What to add / change

## Summary
- Removes Playwright-specific tool references (`browser_navigate`, `browser_take_screenshot`) for cross-agent compatibility
- Converts description from YAML `>` multiline to quoted string
- Adds Task-Specific Questions and Related Skills sections

Content-only portion of the aso-audit cleanup (rename deferred to v2.0.0).

## Test plan
- [ ] Verify SKILL.md frontmatter is valid
- [ ] Confirm no agent-specific tool references remain

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
