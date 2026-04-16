# CI Upgrade Command Fails When Pre-commit Hooks Reject Changes

## Context

The file `dev/breeze/src/airflow_breeze/commands/ci_commands.py` contains the
`upgrade` function that automates CI environment upgrades in the Airflow Breeze
tooling. The codebase uses these utility functions:

- `run_command(...)` — executes shell commands
- `console_print(...)` — prints user-facing informational messages

## Symptom

During the upgrade flow, after creating a branch and staging changes, the
function commits with:

```python
run_command(["git", "commit", "-m", f"[{target_branch}] CI: Upgrade important CI environment"])
```

When pre-commit hooks (mypy, ruff, etc.) auto-fix files during the commit, the
`git commit` exits non-zero, raising `subprocess.CalledProcessError`. This
exception is uncaught, so the entire CI upgrade automation aborts.

## Expected Behavior

The upgrade command should complete successfully even when pre-commit hooks
auto-fix files and cause the initial commit to fail. The corrected code must
satisfy all of the following:

- The commit is protected by error handling that catches
  `subprocess.CalledProcessError`
- On failure, the operator is informed via a `console_print` call
- On failure, modified files are re-staged and the commit is retried with
  `--no-verify` to bypass the pre-commit hooks
- The retry commit uses the long-form `--message` flag (not `-m`)
- All commits preserve the message format:
  `[{target_branch}] CI: Upgrade important CI environment`
- `run_command` is used for all git operations
