# Add PR label management to test verification skill

## Problem

The `verify-tests-fail-without-fix` skill runs test verification but provides no persistent indicator of the result on the PR itself. After verification completes, the only record is console output and log files. Other team members and automation have no quick way to see whether AI-written tests were validated without reading logs.

Additionally, the PR number auto-detection only tries `gh pr view`, which fails for branches from forks since `gh pr view` only finds PRs associated with the current branch on the origin remote.

## Expected Behavior

1. **Label Management Function**: Create a PowerShell function named `Update-VerificationLabels` that:
   - Takes a `-ReproductionConfirmed` boolean parameter
   - Uses two label constants: `$LabelConfirmed` set to `"s/ai-reproduction-confirmed"` and `$LabelFailed` set to `"s/ai-reproduction-failed"`
   - Uses variables `$labelToAdd` and `$labelToRemove` to implement toggle logic
   - Uses GitHub REST API with `DELETE` method to remove the opposite label
   - Uses GitHub REST API with `POST` method to add the appropriate label
   - Checks `$LASTEXITCODE` for error handling
   - Has a guard for when PR number is `"unknown"`

2. **Label Constants**: Define `$LabelConfirmed` and `$LabelFailed` in the script with values:
   - `$LabelConfirmed = "s/ai-reproduction-confirmed"`
   - `$LabelFailed = "s/ai-reproduction-failed"`

3. **Function Calls**: Call `Update-VerificationLabels` with `-ReproductionConfirmed` parameter:
   - Call with `$true` when tests correctly fail without the fix (reproduction confirmed)
   - Call with `$false` when tests pass without the fix (reproduction failed)
   - Must be called on all 4 verification code paths in the script

4. **PR Detection Fallback**: Improve PR number auto-detection:
   - Keep `gh pr view` as the primary detection method
   - Add fallback using `gh pr list --head` that works across forks
   - Use a variable named `$foundPR` to track whether a PR was found

5. **Documentation Update**: Update `SKILL.md` to include:
   - A section titled exactly `## PR Labels`
   - Both label names: `s/ai-reproduction-confirmed` and `s/ai-reproduction-failed`
   - Description of toggle behavior (adding one label removes the other)
   - A table describing the labels
   - Updated workflow steps mentioning "PR labels"

## Files to Modify

- `.github/skills/verify-tests-fail-without-fix/scripts/verify-tests-fail.ps1` — add the `Update-VerificationLabels` function, label constants, function calls on all paths, and improved PR detection with `$foundPR` variable
- `.github/skills/verify-tests-fail-without-fix/SKILL.md` — add `## PR Labels` section with both label names and toggle behavior description
