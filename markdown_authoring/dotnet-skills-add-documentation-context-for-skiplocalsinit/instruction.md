# Add documentation context for SkipLocalsInit

Source: [Aaronontheweb/dotnet-skills#18](https://github.com/Aaronontheweb/dotnet-skills/pull/18)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/csharp/coding-standards/SKILL.md`

## What to add / change

## Summary

Adds explanatory context to the `[SkipLocalsInit]` example from #16:

- Explains what the attribute does (skips `.locals init` zero-initialization)
- When to use it (write-before-read scenarios, profiling shows benefit)
- Warning about reading uninitialized memory
- Project requirement (`AllowUnsafeBlocks`)
- Link to official Microsoft documentation

## Changes

Enhanced the code comments in the `SkipLocalsInit` example to help developers understand the tradeoffs before using this optimization.

## References

- Microsoft Docs: https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/attributes/general#skiplocalsinit-attribute
- Follow-up to #16

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
