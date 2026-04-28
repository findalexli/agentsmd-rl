# Fix API design: optional params are binary incompatible

Source: [Aaronontheweb/dotnet-skills#59](https://github.com/Aaronontheweb/dotnet-skills/pull/59)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/csharp-api-design/SKILL.md`

## What to add / change

## Summary

Fixes #56

- Corrected the "Safe Changes" section: adding optional parameters to existing methods is **not** binary compatible — the IL method signature changes and callers compiled against the old signature get `MissingMethodException` at runtime
- Replaced incorrect examples with the correct pattern: add NEW overload methods that delegate to existing methods
- Moved the optional parameter anti-pattern to the "Unsafe Changes" section with an explanation of why it breaks (optional defaults are baked into the caller's assembly at compile time)

## Test plan

- [ ] Review that the Safe Changes section shows correct overload patterns
- [ ] Verify the Unsafe Changes section clearly explains the binary incompatibility
- [ ] Confirm the guidance matches real .NET binary compatibility behavior

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
