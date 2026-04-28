# docs: Add actor logging and CancellationToken guidance to Akka best practices

Source: [Aaronontheweb/dotnet-skills#36](https://github.com/Aaronontheweb/dotnet-skills/pull/36)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/akka-best-practices/SKILL.md`

## What to add / change

## Summary

- Add Section 9: Actor Logging - use `ILoggingAdapter` from `Context.GetLogger()` instead of DI-injected `ILogger<T>`, semantic logging support in v1.5.59+
- Add Section 10: Managing Async Operations with `CancellationToken` - actor-scoped CTS in PostStop(), linked CTS for per-operation timeouts, graceful handling

## Test plan

- [ ] Verify new sections render correctly
- [ ] Confirm code examples are syntactically correct
- [ ] Run validation script passes

Fixes #29, #31

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
