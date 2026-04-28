# chore: optimize SKILL.md description for ClawHub

Source: [HuangYuChuh/ComfyUI_Skills_OpenClaw#101](https://github.com/HuangYuChuh/ComfyUI_Skills_OpenClaw/pull/101)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `SKILL.md`

## What to add / change

## Summary
- Replaced verbose technical description in SKILL.md frontmatter with a concise, search-friendly summary
- Highlights supported agent platforms (Claude Code, OpenClaw, Codex) and key capabilities (CLI, multi-server, dependency management)
- Already published as `comfyui-skill-openclaw@1.0.1` on ClawHub

## Context
The SKILL.md frontmatter `description` field is indexed by ClawHub's vector search. The new description is optimized for discoverability without affecting the agent instruction body.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
