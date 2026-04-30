# Add constraint-enforcing value objects beyond identifiers

Source: [Aaronontheweb/dotnet-skills#60](https://github.com/Aaronontheweb/dotnet-skills/pull/60)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/csharp-coding-standards/value-objects-and-patterns.md`

## What to add / change

## Summary

Fixes #43

- Added new **Constraint-Enforcing Value Objects** section with examples: `AbsoluteUrl` (with Linux `Uri.TryCreate` gotcha in `FromRelative`), `NonEmptyString`, `EmailAddress`, `PositiveAmount`
- Added **TypeConverter support** subsection showing how to make value objects work with `IOptions<T>` and `appsettings.json` binding
- Key teaching point: **validate at construction, trust everywhere else** — once you have a constrained value object, every consumer knows it's valid without re-checking
- Fixed `PhoneNumber` example to use constructor validation instead of the removed generic `Result<T, TError>` pattern (consistency with #57)
- Removed implicit `operator string` from `AbsoluteUrl` to avoid contradicting the "No Implicit Conversions" section

## Test plan

- [ ] Review that new value object examples compile and follow existing conventions
- [ ] Verify `AbsoluteUrl.FromRelative` correctly documents the Linux `file:///path` gotcha
- [ ] Confirm `TypeConverter` example is complete and usable
- [ ] Check that no implicit conversions snuck through

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
