# docs: streamline CLAUDE.md with accuracy fixes

Source: [orphan-oss/ognl#542](https://github.com/orphan-oss/ognl/pull/542)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
- Fix inaccuracies: JUnit Jupiter 6.x (not 5), Maven wrapper (`./mvnw`), Java 21 CI testing
- Remove hardcoded test count (607) that drifts over time
- Add Architecture section with evaluation flow and key source file descriptions
- Remove generic coding advice (sections 6-10: error handling, type conversion, null handling, memory, code quality)
- Remove redundant sections (Common Pitfalls, Issue Analysis Process, Testing Strategy)
- Trim SonarCloud section to essentials (remove MCP tools examples and common rules list)
- Net reduction: 262 lines removed, 75 added — more focused and accurate

## Test plan
- [ ] Verify CLAUDE.md renders correctly on GitHub
- [ ] Confirm all commands in Essential Commands section are accurate

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
