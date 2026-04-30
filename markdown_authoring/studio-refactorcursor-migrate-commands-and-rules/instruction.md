# refactor(cursor): migrate commands and rules to skills structure

Source: [decocms/studio#2381](https://github.com/decocms/studio/pull/2381)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/skills/add-mcp-tools/SKILL.md`
- `.cursor/skills/commit/SKILL.md`

## What to add / change

## What is this contribution about?

This PR migrates Cursor's configuration from the deprecated commands and rules structure to the new skills format:

- **From**: `.cursor/commands/commit.md` → **To**: `.cursor/skills/commit/SKILL.md`
- **From**: `.cursor/rules/add-mcp-tools.mdc` → **To**: `.cursor/skills/add-mcp-tools/SKILL.md`

The new skills format adds frontmatter metadata (`name`, `description`, `disable-model-invocation`) for better integration with Cursor's agent system. The functional content remains unchanged - this is purely a structural migration to align with Cursor's latest best practices.

## Screenshots/Demonstration

N/A - Configuration file migration only

## How to Test

1. Open this repository in Cursor
2. Verify that the `/commit` command still works by typing `/commit` in the chat
3. Verify that the `add-mcp-tools` skill is accessible when adding new MCP tools
4. Confirm that both skills appear in Cursor's agent skills list
5. Expected outcome: Both skills function identically to before, with improved metadata support

## Migration Notes

N/A - No database migrations, configuration changes, or runtime setup required

## Review Checklist

- [x] PR title is clear and descriptive
- [x] Changes are tested and working (all quality checks passed: fmt, lint, check:ci, knip, test)
- [x] Documentation is updated (skills now include proper frontmatter metadata)
- [x] No breaking changes (purely structural migration, functionality unchanged)

Made with [Cursor](ht

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
