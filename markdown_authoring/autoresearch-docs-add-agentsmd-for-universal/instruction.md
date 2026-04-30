# docs: add AGENTS.md for universal AI agent onboarding

Source: [uditgoenka/autoresearch#67](https://github.com/uditgoenka/autoresearch/pull/67)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary

- Adds `AGENTS.md` — a universal onboarding file that any AI agent (Claude Code, Codex, OpenCode, Gemini CLI) can read to immediately use all 10 autoresearch commands
- Covers installation, command surface, configuration fields, flags, chaining, 8 critical rules, results tracking, and agent-specific notes
- Follows the [AGENTS.md convention](https://docs.github.com/en/copilot/customizing-copilot/adding-repository-instructions-for-github-copilot) for AI agent context

## What's included

| Section | Purpose |
|---------|---------|
| Installation | Claude Code plugin, Codex plugin, manual copy |
| Commands | All 10 commands with usage examples |
| Configuration | Goal, Scope, Metric, Verify, Guard, Iterations |
| Flags | Per-command flag reference |
| Chaining | `--chain` patterns across commands |
| 8 Critical Rules | Core loop invariants |
| Agent-Specific Notes | Claude Code, Codex, OpenCode/Gemini CLI differences |
| Repo Structure | Directory layout pointer |

## Test plan

- [ ] Verify `AGENTS.md` renders correctly on GitHub
- [ ] Confirm all command names and flags match README.md
- [ ] Test that a fresh Claude Code session can discover commands from AGENTS.md

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
