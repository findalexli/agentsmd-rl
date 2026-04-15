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

## Relevant Files

- `crates/uv/src/printer.rs` — The `Printer` enum controls stderr output based on verbosity level. Currently `stderr()` returns `Disabled` for `Quiet` mode, with no way to distinguish between routine and important messages.
- `crates/uv/src/commands/self_update.rs` — All user-facing messages use `printer.stderr()`, which means they're all suppressed equally under `-q`.

## Technical Requirements

The fix requires:

1. **A new method on `Printer`** that returns `Stderr` and treats `Quiet` mode differently from `Silent` mode. The method must be named `stderr_important` and:
   - Return `Stderr::Enabled` when the printer is in `Quiet` mode (so important messages are shown under `-q`)
   - Return `Stderr::Disabled` when the printer is in `Silent` mode (so `-qq` still suppresses everything)
   - Return `Stderr::Enabled` for all other modes (`Default`, `Verbose`, `NoProgress`)

2. **At least 3 call sites in `self_update.rs`** that use `.stderr_important()` for important messages (update notifications, offline errors, rate-limit warnings, etc.) instead of `.stderr()`.

3. **No regression**: the existing `stderr()` method must continue returning `Disabled` for both `Quiet` and `Silent` modes.
