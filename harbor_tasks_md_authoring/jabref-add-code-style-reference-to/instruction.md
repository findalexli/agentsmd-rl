# Add code style reference to AGENTS.md

Source: [JabRef/jabref#14638](https://github.com/JabRef/jabref/pull/14638)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Addresses feedback to include JabRef's code style rules in agent instructions.

## Changes

- Added reference to `docs/getting-into-the-code/guidelines-for-setting-up-a-local-workspace/intellij-13-code-style.md` in the Style section of AGENTS.md
- Agents are now explicitly directed to follow JabRef's documented code style configuration (CheckStyle, auto-formatting, import optimization)

<!-- START COPILOT CODING AGENT TIPS -->
---

💬 We'd love your input! Share your thoughts on Copilot coding agent in our [2 minute survey](https://gh.io/copilot-coding-agent-survey).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
