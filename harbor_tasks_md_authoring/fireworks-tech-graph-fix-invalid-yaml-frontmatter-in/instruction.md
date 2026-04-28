# Fix invalid YAML frontmatter in SKILL.md

Source: [yizhiyanhua-ai/fireworks-tech-graph#2](https://github.com/yizhiyanhua-ai/fireworks-tech-graph/pull/2)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `SKILL.md`

## What to add / change

This fixes the YAML frontmatter in `SKILL.md` so `npx skills add` can detect and install the skill correctly.

The previous `description` value contained `Trigger on:` inside an unquoted scalar, which caused parsing to fail in the skills CLI.

Verification:
- `npx -y skills add /tmp/fireworks-tech-graph-pr --list --full-depth` now finds the skill successfully.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
