# AGENTS.md skill references

Source: [rorkai/App-Store-Connect-CLI#190](https://github.com/rorkai/App-Store-Connect-CLI/pull/190)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agent/skills/asc-cli-usage/SKILL.md`
- `Agents.md`

## What to add / change

Move references from `asc-cli-usage` skill to `Agents.md` to centralize documentation.

---
<a href="https://cursor.com/background-agent?bcId=bc-eb7b22d6-40ca-440b-b58f-a26651480a1b"><picture><source media="(prefers-color-scheme: dark)" srcset="https://cursor.com/open-in-cursor-dark.svg"><source media="(prefers-color-scheme: light)" srcset="https://cursor.com/open-in-cursor-light.svg"><img alt="Open in Cursor" src="https://cursor.com/open-in-cursor.svg"></picture></a>&nbsp;<a href="https://cursor.com/agents?id=bc-eb7b22d6-40ca-440b-b58f-a26651480a1b"><picture><source media="(prefers-color-scheme: dark)" srcset="https://cursor.com/open-in-web-dark.svg"><source media="(prefers-color-scheme: light)" srcset="https://cursor.com/open-in-web-light.svg"><img alt="Open in Web" src="https://cursor.com/open-in-web.svg"></picture></a>

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
