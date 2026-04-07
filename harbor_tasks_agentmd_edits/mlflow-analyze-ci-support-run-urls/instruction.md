# Support workflow run URLs in analyze-ci skill

## Problem

The `analyze-ci` skill (`.claude/skills/src/skills/commands/analyze_ci.py`) currently accepts PR URLs (`/pull/123`) and individual job URLs (`/actions/runs/123/job/456`), but not bare workflow run URLs like `https://github.com/mlflow/mlflow/actions/runs/22626454465`.

Users frequently copy run URLs from the GitHub Actions UI, but pasting one into the skill produces an error about invalid URL format.

## Expected Behavior

The skill should accept workflow run URLs (`github.com/owner/repo/actions/runs/N`) as input. When given a run URL, it should fetch all failed jobs from that run and analyze them, the same way it already does for PR URLs.

The URL dispatching must be careful: job URLs (`/actions/runs/N/job/M`) are a superset of run URLs, so the pattern matching order matters to avoid false positives.

The error message for unrecognized URLs should mention the new run URL format.

## Files to Look At

- `.claude/skills/src/skills/commands/analyze_ci.py` — URL patterns and `resolve_urls()` dispatch logic
- `.claude/skills/src/skills/github/client.py` — `get_jobs()` method already exists for fetching jobs by run ID
- `.claude/skills/analyze-ci/SKILL.md` — skill documentation (usage and examples should reflect the new URL format)
