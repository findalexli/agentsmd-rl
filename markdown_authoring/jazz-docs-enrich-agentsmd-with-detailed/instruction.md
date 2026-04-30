# docs: enrich AGENTS.md with detailed project overview and add a requirements scan step on the spec skill

Source: [garden-co/jazz#3437](https://github.com/garden-co/jazz/pull/3437)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/skills/spec/SKILL.md`
- `AGENTS.md`

## What to add / change

See the PR for the intended changes to the listed file(s).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
