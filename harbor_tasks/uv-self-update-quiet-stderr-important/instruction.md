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

## Hints

- Look at how `Printer` maps verbosity levels to `Stderr::Enabled` / `Stderr::Disabled`
- The `Printer` enum already has multiple variants: `Silent`, `Quiet`, `Default`, `Verbose`, `NoProgress`
- Consider adding a new output channel that treats `Quiet` differently from `Silent`
- The test helper in `crates/uv-test/src/lib.rs` may need a version-filtering utility for snapshot tests
