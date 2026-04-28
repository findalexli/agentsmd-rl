# Add Windows Command Line Best Practices to AGENTS.md

Source: [DataDog/dd-trace-dotnet#7980](https://github.com/DataDog/dd-trace-dotnet/pull/7980)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary of changes

Added clear guidelines to AGENTS.md about avoiding `>nul` and `2>nul` redirections on Windows, which can create literal "nul" files that are extremely difficult to delete.

## Reason for change

On Windows, redirecting to `nul` (e.g., `command 2>nul`) can create a literal file named "nul" in the current directory instead of properly redirecting to the NUL device. These files are problematic because:
- They cannot be deleted using standard Windows commands
- They cause repository hygiene issues
- They're confusing and frustrating to deal with

This issue was documented in https://github.com/anthropics/claude-code/issues/4928

## Implementation details

1. **Added new section**: "Windows Command Line Best Practices" in AGENTS.md after the Coding Standards section
2. **Provided clear examples** of problematic commands (including `findstr` with `2>nul`)
3. **Documented safe alternatives**:
   - Let error output show naturally (don't suppress)
   - Use full device path `\\.\NUL` if suppression is essential
   - Prefer PowerShell or dedicated tools over piped bash commands

## Test coverage

## Other details
<!-- Fixes #{issue} -->


<!--  ⚠️ Note:

Where possible, please obtain 2 approvals prior to merging. Unless CODEOWNERS specifies otherwise, for external teams it is typically best to have one review from a team member, and one review from apm-dotnet. Trivial changes do not require 2 reviews.

MergeQueue is NOT enabled in t

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
