# Task: Fix CI Upgrade Command Error Handling

## Problem

The `upgrade` command in Airflow's Breeze CI tooling has a bug when committing changes during automated CI upgrades. If pre-commit hooks make auto-fixes that modify files during the commit, the git commit may fail, breaking the automation.

## Location

File: `dev/breeze/src/airflow_breeze/commands/ci_commands.py`

Look for the `upgrade` function. Currently, it runs a git commit command that can fail if pre-commit hooks make changes during the commit process.

## Required Changes

The fix should:

1. **Wrap the git commit in a try-except block** that catches `subprocess.CalledProcessError`
2. **On failure**, print an informative message about auto-fixes being made
3. **Stage any new changes** with `git add .` before retrying
4. **Retry the commit with `--no-verify`** flag to skip pre-commit hooks
5. **Use `--message`** instead of `-m` for the commit message flag

The retry logic should:
- First attempt: normal git commit
- If that fails: print info message, stage changes, commit with `--no-verify`

## Example Behavior

Before the fix, if pre-commit hooks modified files during commit:
```
git commit -m "[branch] CI: Upgrade important CI environment"
# FAILS if pre-commit hooks modify files
```

After the fix:
```
git commit --message "[branch] CI: Upgrade important CI environment"
# If fails due to pre-commit changes:
# Print: "Commit failed, assume some auto-fixes might have been made..."
git add .
git commit --no-verify --message "[branch] CI: Upgrade important CI environment"
# Succeeds
```

## Testing

The code should remain valid Python and properly handle the CalledProcessError exception from the subprocess module.

## Notes

- The subprocess module is already imported at the top of the file
- The `run_command` and `console_print` utilities are available in the module
- The commit message format is `[{target_branch}] CI: Upgrade important CI environment`
