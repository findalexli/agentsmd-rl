# docs: add agent-friendly design principles to add-command skill

Source: [Doist/todoist-cli#244](https://github.com/Doist/todoist-cli/pull/244)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/add-command/SKILL.md`

## What to add / change

## Summary
- Adds a new "Agent-Friendly Design Checklist" section (section 4) to the `add-command` skill, encoding the [7 Principles for Agent-Friendly CLIs](https://trevinsays.com/p/7-principles-for-agent-friendly-clis) with concrete guidance referencing existing codebase patterns
- Augments the flag conventions table with list command flags and `--quiet` note
- Augments error handling guidance with actionable-error best practices for agents
- Augments subcommand registration with help text quality guidance

## Test plan
- [ ] Review rendered SKILL.md for correctness and readability
- [ ] Verify all referenced utilities (`paginate()`, `formatNextCursorFooter()`, `pickFields()`, `readStdin()`, `isQuiet()`, `CliError`) exist in the codebase

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
