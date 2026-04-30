# Simplify Result type pattern in C# coding standards

Source: [Aaronontheweb/dotnet-skills#58](https://github.com/Aaronontheweb/dotnet-skills/pull/58)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/csharp-coding-standards/composition-and-error-handling.md`

## What to add / change

## Summary

Fixes #57

- Replaced over-engineered `readonly record struct Result<TValue, TError>` with a simple `IResult<T>` interface plus `Success<T>` and `Failure<T>` classes
- Replaced magic string error codes (`"VALIDATION_ERROR"`) with an `OrderError` enum for type safety and space efficiency
- Removed functional combinators (`Map`, `Bind`, `Match`, `GetValueOr`) — callers use standard C# `is` pattern matching instead
- Added note that discriminated unions will eventually replace this pattern in C#

## Test plan

- [ ] Review that the simplified Result pattern compiles and is idiomatic C#
- [ ] Verify enum-based error codes are used consistently
- [ ] Confirm `is` pattern matching replaces `.Match()` lambdas in usage examples

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
