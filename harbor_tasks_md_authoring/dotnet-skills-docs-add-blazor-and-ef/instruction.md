# docs: Add Blazor and EF Core exclusions to crap-analysis skill

Source: [Aaronontheweb/dotnet-skills#38](https://github.com/Aaronontheweb/dotnet-skills/pull/38)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/crap-analysis/SKILL.md`

## What to add / change

## Summary

Add to ExcludeByFile:
- `**/*.razor.g.cs` (Blazor component generated code)
- `**/*.razor.css.g.cs` (Blazor CSS isolation generated code)
- `**/Migrations/**/*` (EF Core migrations)

Add to ExcludeByAttribute:
- `ExcludeFromCodeCoverageAttribute` (explicit developer opt-out)

## Test plan

- [ ] Verify coverage.runsettings example is correct
- [ ] Confirm What Gets Excluded table is updated
- [ ] Run validation script passes

Fixes #6

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
