# Fix Telemetry Test Error Origin Parsing

## Problem

The telemetry test suite captures error origin information by parsing error
messages. The `ExitError` type defined in `dagql/idtui/exit.go` wraps an
underlying error along with an exit code, but its `Error()` method only
returns generic exit-code text and drops the wrapped error's message. As a
result, telemetry parsing code can no longer recover error origins from the
returned string.

The relevant type has the shape:

```go
type ExitError struct {
    Code     int
    Original error
    // ...
}
```

## Task

1.  **Fix `ExitError.Error()` in `dagql/idtui/exit.go`**

    Update the `Error()` method on `ExitError` so that the string it returns
    includes:

    -   the exit code (e.g. something containing the numeric `Code`), and
    -   the full message from `Original.Error()` whenever `Original` is
        non-nil.

    When `Original` is nil, the returned string must still contain the exit
    code, must not panic, and must not contain the literal text `nil` (so
    callers don't see placeholder garbage for an unset cause).

    The exact formatting of the combined string is up to you, as long as
    both pieces of information appear in the output when `Original` is set.

2.  **Update Skill Documentation**

    Append a new section to `skills/dagger-chores/SKILL.md` with the
    following content (in this order):

    -   A level-2 header: `## Regenerate Golden Tests`
    -   The line: `Use this checklist when asked to regenerate telemetry golden tests.`
    -   A numbered step: `1. From the Dagger repo root, run \`dagger -c 'engine-dev | test-telemetry --update | export .'\``

## Expected Behavior

After the fix:

-   `ExitError{Code: 1, Original: errors.New("parser: unexpected token at line 42")}.Error()`
    returns a string that contains `"parser: unexpected token at line 42"`.
-   `ExitError{Code: 42}.Error()` returns a string that contains `"42"`
    and does not contain `"nil"`.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters.
All modified files must pass:

- `gofmt (Go formatter)`
