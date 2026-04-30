# Add query splitting recommendations to EF Core patterns

Source: [Aaronontheweb/dotnet-skills#11](https://github.com/Aaronontheweb/dotnet-skills/pull/11)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/data/efcore-patterns/SKILL.md`

## What to add / change

Closes #8

## What changed
- Add query splitting pattern to EF Core skill (Pattern 6)
- Include global configuration with `UseQuerySplittingBehavior(SplitQuery)`
- Document per-query override with `AsSingleQuery()`
- Add trade-offs and decision criteria
- Update skill description and "When to use" section

## Why
Addresses cartesian explosion when loading multiple navigation collections, as requested in #8.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
