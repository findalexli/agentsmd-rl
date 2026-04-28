# fix: add how to write a skill to agent.md

Source: [supabase/agent-skills#16](https://github.com/supabase/agent-skills/pull/16)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Adds instructions and good practices on how to write agent skills to the Agents.md. These instructions and good practices were written based on the open standard [agent skills spec](https://agentskills.io/spec) and the Anthropic's [skill-creator skill](https://github.com/anthropics/skills/tree/main/skills/skill-creator)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
