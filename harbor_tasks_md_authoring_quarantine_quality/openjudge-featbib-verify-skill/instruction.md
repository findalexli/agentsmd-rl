# Feat/bib verify skill

Source: [agentscope-ai/OpenJudge#140](https://github.com/agentscope-ai/OpenJudge/pull/140)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/bib-verify/SKILL.md`

## What to add / change

## OpenJudge Version

[The version of OpenJudge you are working on, e.g. `import openjudge; print(openjudge.__version__)`]

## Description

[Please describe the background, purpose, changes made, and how to test this PR]

## Checklist

Please check the following items before code is ready to be reviewed.

- [ ]  Code has been formatted with `pre-commit run --all-files` command
- [ ]  All tests are passing
- [ ]  Docstrings are in Google style
- [ ]  Related documentation has been updated (e.g. links, examples, etc.)
- [ ]  Code is ready for review

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
