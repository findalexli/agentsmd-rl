# Remove curl from allowed tools

Source: [apollographql/skills#38](https://github.com/apollographql/skills/pull/38)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/apollo-connectors/SKILL.md`
- `skills/apollo-mcp-server/SKILL.md`
- `skills/rover/SKILL.md`
- `skills/skill-creator/SKILL.md`

## What to add / change

<!-- https://apollographql.atlassian.net/browse/AMS-418 -->

A security audit identified three skills (`apollo-connectors`, `apollo-mcp-server`, `rover`) that allow unrestricted `curl` access via `Bash(curl:*)` in their `allowed-tools` frontmatter. This permission lets an AI agent make any HTTP requests without user approval, including running the `curl | sh` remote code execution pattern found in the installation instructions for `rover` and `apollo-mcp-server`.

This PR removes `Bash(curl:*)` from all three skills. They will still work fully, but now `curl` commands will need explicit user confirmation before running. This gives users a chance to review network requests.

Also, the `skill-creator` skill has been updated to prevent `Bash(curl:*)` in new skills moving forward, both in the frontmatter documentation and as a clear ground rule.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
