# Bug: `uv self update --quiet` suppresses important success/failure messages

## Problem

When running `uv self update` with the `--quiet` (`-q`) flag, **all** stderr output is suppressed — including important messages like update success notifications, version mismatch info, offline errors, and rate-limit warnings.

This is problematic for users running `uv self update` in cron jobs or CI pipelines: they want to suppress routine informational noise (`-q`), but still see output when something actually happens (an update was applied, an error occurred, etc.). Currently, the only options are full verbosity or complete silence — there's no middle ground.

## Expected Behavior

`uv self update -q` should suppress routine informational messages but still show important messages like:
- "Updated uv from vX.Y.Z to vA.B.C"
- "Self-update is not possible because network connectivity is disabled"
- "You're on the latest version of uv"
- Rate-limit / error messages

Only `uv self update -qq` (double quiet / silent mode) should suppress everything.

## Technical Context

The codebase uses a `Printer` enum (defined in `crates/uv/src/printer.rs`) to control stderr output based on verbosity level. The enum has variants including `Silent`, `Quiet`, `Default`, `Verbose`, and `NoProgress`. The current implementation treats both `Silent` and `Quiet` identically for stderr output.

The `self update` command implementation is in `crates/uv/src/commands/self_update.rs` where important user-facing messages are currently being suppressed when `--quiet` is used.

## Requirements

The fix must satisfy the following behavioral requirements that the test suite will verify:

1. **New `stderr_important` method**: The `Printer` enum must have a method named `stderr_important` with signature `fn stderr_important(self) -> Stderr` that distinguishes between `Quiet` and `Silent` modes:
   - Returns `Stderr::Enabled` for `Quiet` mode (allowing important messages through)
   - Returns `Stderr::Disabled` for `Silent` mode (double-quiet suppresses all)
   - Returns `Stderr::Enabled` for `Default`, `Verbose`, and `NoProgress` modes

2. **Adoption in self-update**: The `self_update.rs` file must call `.stderr_important()` at 3 or more sites for important messages (update notifications, offline errors, rate-limit warnings, version info, etc.) so they are visible even with `--quiet`.

3. **No regression**: The existing `stderr()` method must continue to return `Stderr::Disabled` for both `Quiet` and `Silent` modes, ensuring routine informational messages remain suppressed in quiet mode.
