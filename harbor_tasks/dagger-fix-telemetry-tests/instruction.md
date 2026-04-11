# Fix Telemetry Test Error Origin Parsing

## Problem

The telemetry test suite relies on `ParseErrorOrigins` to extract error origin information from error messages. However, `ExitError` in `dagql/idtui/exit.go` only returns a generic "exit code N" message from its `Error()` method — it never includes the message from its `Original` error field. This means when an `ExitError` wraps an underlying error, `ParseErrorOrigins` cannot find or extract the original error details, causing telemetry tests to miss error origin data.

## Expected Behavior

`ExitError.Error()` should include the original error's message (when one is set) so that code parsing error messages — like `ParseErrorOrigins` — can still find the underlying error information. Since this message is noted as "not actually printed anywhere", including the original error is safe and does not change user-visible output.

After fixing the code, update the relevant skill documentation to include instructions for regenerating telemetry golden tests. The `skills/dagger-chores/SKILL.md` file documents repeatable chore workflows and should cover this regeneration process.

## Files to Look At

- `dagql/idtui/exit.go` — defines `ExitError` and its `Error()` method
- `skills/dagger-chores/SKILL.md` — chore checklists for common maintenance tasks
