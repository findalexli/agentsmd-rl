# Support workflow run URLs in analyze-ci skill

## Problem

The `analyze-ci` skill (`.claude/skills/src/skills/commands/analyze_ci.py`) currently accepts PR URLs (`/pull/123`) and individual job URLs (`/actions/runs/123/job/456`), but not bare workflow run URLs like `https://github.com/mlflow/mlflow/actions/runs/22626454465`.

Users frequently copy run URLs from the GitHub Actions UI, but pasting one into the skill produces an error about invalid URL format.

## Expected Behavior

The skill must accept bare workflow run URLs — URLs of the form `https://github.com/owner/repo/actions/runs/N` where `N` is a run ID — as input. When given a run URL, it must fetch all failed jobs from that run and analyze them, the same way it already does for PR URLs and job URLs.

The URL dispatching must be careful: job URLs (`/actions/runs/N/job/M`) are a superset pattern of run URLs, so the dispatch logic must check for job URLs before (or with higher priority than) bare run URLs to avoid false positives.

### URL pattern requirements

The skill must define a regex pattern (as a module-level name ending in `_PATTERN`) that matches bare workflow run URLs and captures two groups:
- group(1): the `owner/repo` string
- group(2): the run ID as a decimal digit string

The pattern must NOT match URLs that contain a `/job/` path segment (job URLs must be handled separately).

### resolve_urls requirements

The `resolve_urls()` async function must dispatch run URLs by:
1. Matching the URL against the run URL pattern
2. Extracting `owner`, `repo`, and `run_id` from the pattern groups
3. Calling `client.get_jobs(owner, repo, run_id)` to fetch jobs for the run
4. Filtering to only failed jobs (`conclusion == "failure"`)
5. Adding those jobs to the result list

### Documentation requirements

The error message for unrecognized URLs must mention that workflow run URLs are a valid format.

The skill documentation (`.claude/skills/analyze-ci/SKILL.md`) must include an example of a bare workflow run URL (showing `actions/runs/N` without any `/job/` suffix) in both the Usage and Examples sections.

## Files to Look At

- `.claude/skills/src/skills/commands/analyze_ci.py` — URL patterns, `resolve_urls()` dispatch logic, and help text
- `.claude/skills/src/skills/github/client.py` — `get_jobs()` method for fetching jobs by run ID
- `.claude/skills/analyze-ci/SKILL.md` — skill documentation (must be updated to show run URL examples)
