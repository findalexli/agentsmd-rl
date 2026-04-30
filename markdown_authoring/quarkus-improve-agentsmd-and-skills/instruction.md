# Improve AGENTS.md and skills

Source: [quarkusio/quarkus#53672](https://github.com/quarkusio/quarkus/pull/53672)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/building-and-testing/SKILL.md`
- `.agents/skills/coding-style/SKILL.md`
- `.agents/skills/writing-tests/SKILL.md`
- `AGENTS.md`

## What to add / change

I'm still unsure if Claude Code actually consumes the skills when going through a basic coding workflow.

Personally, I think the basic rules for coding/building/testing should all live in the `AGENTS.md`.

For now, I edited the skills anyway:

- we should use -Dstart-containers -Dtest-containers by default for testing
- we should never use -Dno-format, which Claude Code just did for me
- we should never remove existing comments that are still valid, which Claude Code just did

But I think we need to discuss this. /cc @Sanne @maxandersen

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
