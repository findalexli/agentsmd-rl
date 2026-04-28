# docs: Add async local functions guidance to concurrency patterns

Source: [Aaronontheweb/dotnet-skills#37](https://github.com/Aaronontheweb/dotnet-skills/pull/37)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/csharp-concurrency-patterns/SKILL.md`

## What to add / change

## Summary

Add guidance to prefer async local functions over `Task.Run(async () => ...)` and `ContinueWith()`:

- Better stack traces for debugging
- Cleaner exception handling (no AggregateException unwrapping)
- Self-documenting code with named functions
- Includes Akka.NET PipeTo example

## Test plan

- [ ] Verify new section renders correctly
- [ ] Confirm code examples are syntactically correct
- [ ] Run validation script passes

Fixes #30

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
