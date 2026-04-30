# [AutoWS] Add docs-first skill for AutoWS development

Source: [facebookexperimental/triton#1125](https://github.com/facebookexperimental/triton/pull/1125)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/autows-docs/SKILL.md`

## What to add / change

Adds a Claude skill that ensures AutoWS documentation is consulted before exploring source code and updated after non-trivial code changes.

Authored with Claude.


I noticed that Claude seemed to still be spending too much time reviewing all the source code, so I'm hoping this will guide it to reuse our docs.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
