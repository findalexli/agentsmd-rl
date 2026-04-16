# Breeze CI Upgrade Command Crashes on Pre-Commit Hook Failures

When running `breeze ci upgrade`, the command fails unrecoverably if pre-commit hooks fail during the automated commit phase.

## Symptom

The `breeze ci upgrade` command creates a branch, stages changes, and attempts to commit with the message `CI: Upgrade important CI environment`. When pre-commit hooks (such as mypy or other linters) fail, the command crashes with a subprocess error and leaves the upgrade incomplete.

This is problematic because automated CI tool upgrades may introduce changes that trigger pre-commit hook failures, and the upgrade process should complete successfully rather than crashing.

## Expected Behavior

When the initial git commit fails due to pre-commit hook errors:

1. The error should be caught and handled gracefully (not crash)
2. The user should be informed via `console_print` that the failure is being handled (message includes the literal string "auto-fixes")
3. Auto-fixed files should be re-staged
4. The commit should be retried with `--no-verify` to bypass pre-commit hooks, using the same commit message `CI: Upgrade important CI environment`

## Requirements Summary

- The commit command should use the `--message` flag (not `-m`)
- When hooks fail, the system should retry the commit with `--no-verify`
- Both the initial and retry commits use the same message format

## File

`dev/breeze/src/airflow_breeze/commands/ci_commands.py` — the `upgrade` function handles CI environment upgrades.