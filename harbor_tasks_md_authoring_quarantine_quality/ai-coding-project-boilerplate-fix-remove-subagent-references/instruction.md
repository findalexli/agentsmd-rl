# fix: remove subagent references from CLAUDE.md to prevent recursion

Source: [shinpr/ai-coding-project-boilerplate#7](https://github.com/shinpr/ai-coding-project-boilerplate/pull/7)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

Remove all subagent-related content from CLAUDE.md to prevent recursive calls when subagents read the CLAUDE.md file. This includes:
- Removed "Sub-agent" from the project description
- Removed the entire subagent list from the tool utilization section
- Removed point 5 about subagent delegation from behavior principles

🤖 Generated with [Claude Code](https://claude.ai/code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
