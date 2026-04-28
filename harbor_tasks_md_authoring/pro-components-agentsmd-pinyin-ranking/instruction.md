# Agents.md pinyin ranking

Source: [ant-design/pro-components#9446](https://github.com/ant-design/pro-components/pull/9446)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/AGENTS.md`

## What to add / change

Add API property sorting rules to AGENTS.md to specify pinyin ranking for consistency and readability.

---
<p><a href="https://cursor.com/background-agent?bcId=bc-5c0949b4-2830-41c6-8c9e-92b764cc3d5a"><picture><source media="(prefers-color-scheme: dark)" srcset="https://cursor.com/assets/images/open-in-cursor-dark.png"><source media="(prefers-color-scheme: light)" srcset="https://cursor.com/assets/images/open-in-cursor-light.png"><img alt="Open in Cursor" width="131" height="28" src="https://cursor.com/assets/images/open-in-cursor-dark.png"></picture></a>&nbsp;<a href="https://cursor.com/agents?id=bc-5c0949b4-2830-41c6-8c9e-92b764cc3d5a"><picture><source media="(prefers-color-scheme: dark)" srcset="https://cursor.com/assets/images/open-in-web-dark.png"><source media="(prefers-color-scheme: light)" srcset="https://cursor.com/assets/images/open-in-web-light.png"><img alt="Open in Web" width="114" height="28" src="https://cursor.com/assets/images/open-in-web-dark.png"></picture></a></p>

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
