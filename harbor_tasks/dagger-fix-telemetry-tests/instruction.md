# Fix Telemetry Test Error Origin Parsing

## Problem

The telemetry test suite captures error origin information by parsing error messages. However, when errors are wrapped in a type that only returns generic exit code information, the original error details are lost. This causes telemetry tests to miss error origin data because the underlying error message is not preserved in the wrapped error's string representation.

## Task

1.  **Fix Error Message Propagation**

    Locate the error type that wraps underlying errors with an exit code but fails to include the wrapped error's message in its `Error()` string representation. Modify the code so that when this error type wraps an original error, the original error's message is included in the returned string from `Error()`. The fix should handle the case where no original error is set (to avoid nil pointer issues) and must not change behavior for errors without an original cause.

2.  **Update Skill Documentation**

    Add a new section to the skill documentation file at `skills/dagger-chores/SKILL.md` with the following exact content:

    -   Section header: `## Regenerate Golden Tests`
    -   Followed by two blank lines
    -   Then the text: `Use this checklist when asked to regenerate telemetry golden tests.`
    -   Followed by two blank lines
    -   Then a numbered step: `1. From the Dagger repo root, run \`dagger -c 'engine-dev | test-telemetry --update | export .'\``

    The exact format (including spacing and command) must match for the test to pass.

## Expected Behavior

After the fix, error messages should contain both the exit code information and the original underlying error message (when present), allowing telemetry parsing code to extract error origins. The separator between the exit code and original message should be two newline characters (`\n\n`).
