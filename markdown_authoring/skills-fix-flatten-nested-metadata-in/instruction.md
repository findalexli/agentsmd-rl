# fix: flatten nested metadata in nookplot SKILL.md frontmatter

Source: [BankrBot/skills#326](https://github.com/BankrBot/skills/pull/326)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `nookplot/SKILL.md`

## What to add / change

## Summary
- Fix YAML parse error: `mapping values are not allowed in this context at line 4 column 296`
- Move `author` and `version` from nested `metadata:` block to top-level frontmatter fields

## Test plan
- [ ] Verify SKILL.md renders without YAML errors

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
