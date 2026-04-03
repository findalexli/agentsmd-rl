# Add PR label management to test verification skill

## Problem

The `verify-tests-fail-without-fix` skill runs test verification but provides no persistent indicator of the result on the PR itself. After verification completes, the only record is console output and log files. Other team members and automation have no quick way to see whether AI-written tests were validated without reading logs.

Additionally, the PR number auto-detection only tries `gh pr view`, which fails for branches from forks since `gh pr view` only finds PRs associated with the current branch on the origin remote.

## Expected Behavior

1. After test verification completes, the skill should automatically update labels on the PR to indicate the verification result. There should be two mutually exclusive labels — one for when tests correctly fail without the fix (reproduction confirmed), and one for when tests pass without the fix (reproduction failed). The labels should toggle: adding one should remove the other.

2. PR number auto-detection should have a fallback mechanism that works across forks.

3. The skill's SKILL.md documentation should be updated to describe the new label management feature, including what labels are used, when they're applied, and how they behave.

## Files to Look At

- `.github/skills/verify-tests-fail-without-fix/scripts/verify-tests-fail.ps1` — the PowerShell verification script that needs the label management function and improved PR detection
- `.github/skills/verify-tests-fail-without-fix/SKILL.md` — skill documentation that should be updated to cover the new feature
