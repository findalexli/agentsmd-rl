# Add CI / Pipeline Monitoring Scripts

## Problem

There is no convenient way to monitor CI check statuses for a given PR, wait for Docker image builds to complete, or inspect and re-run failed CI jobs. Developers (and Claude) have to manually poll `gh pr checks` and interpret the output each time.

## Expected Behavior

The repo should have reusable shell scripts in `.claude/scripts/` that:

1. **Monitor PR checks** — poll all CI checks for a given PR number until they complete, reporting pass/fail/pending counts at each interval. Exit 0 if all pass, exit 1 if any fail.
2. **Monitor Docker image builds** — given a GitHub Actions run ID, poll until the docker report job completes, then print the resulting image tags on success.

Both scripts should validate their inputs (PR number or run ID) and exit with a usage message if arguments are missing.

The scripts must be committed to the repo (not gitignored). Currently `.claude/*` is in `.gitignore` — the `.claude/scripts/` directory needs to be exempted.

After creating the scripts, update the project's `CLAUDE.md` to document these new CI monitoring capabilities, including usage examples and how to inspect/re-run failed checks.

## Files to Look At

- `.claude/scripts/` — where the monitoring scripts should live (create this directory)
- `.gitignore` — currently ignores all of `.claude/*`; needs to allow `.claude/scripts/`
- `CLAUDE.md` — project instructions for Claude; needs a new section documenting CI monitoring
