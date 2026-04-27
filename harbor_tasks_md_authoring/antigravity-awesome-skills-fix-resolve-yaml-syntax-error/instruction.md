# fix: resolve YAML syntax error in database-migrations-sql-migrations (Fixes #116)

Source: [sickn33/antigravity-awesome-skills#119](https://github.com/sickn33/antigravity-awesome-skills/pull/119)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/android-jetpack-compose-expert/SKILL.md`
- `skills/database-migrations-sql-migrations/SKILL.md`
- `skills/kotlin-coroutines-expert/SKILL.md`

## What to add / change

This PR resolves a YAML syntax error in `skills/database-migrations-sql-migrations/SKILL.md` where the `description` field was incorrectly formatted across multiple lines, causing parsing failures for strict YAML parsers.

Changes:
- Unified `description` into a single line.
- Removed non-standard frontmatter keys (`allowed-tools`, `metadata`) to adhere to V4 Quality Standards.
- Standardized section headers (`## When to Use This Skill`) for consistency.

Fixes #116

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
