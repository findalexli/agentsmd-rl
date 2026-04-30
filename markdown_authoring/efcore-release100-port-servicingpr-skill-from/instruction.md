# [release/10.0] Port servicing-pr skill from main

Source: [dotnet/efcore#37990](https://github.com/dotnet/efcore/pull/37990)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/servicing-pr/SKILL.md`

## What to add / change

Adds the `servicing-pr` agent skill to the `release/10.0` branch, porting it from `main`.

## Changes
- Added `.agents/skills/servicing-pr/SKILL.md` — provides guidance for:
  - Targeting the correct `release/XX.0` branch
  - Required PR title format (`[release/XX.0] <title>`)
  - Mandatory PR description template (description, customer impact, how found, regression, testing, risk)
  - When and how to add a quirk (AppContext switch) to allow opting out of fixes at runtime

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
