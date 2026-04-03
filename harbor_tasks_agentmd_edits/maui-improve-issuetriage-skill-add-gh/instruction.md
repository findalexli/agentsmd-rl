# Improve issue-triage skill: Add gh CLI checks and fix workflow

## Problem

The issue-triage skill at `.github/skills/issue-triage/` has several problems that cause agents to misuse it during triage sessions:

1. **No prerequisite checks**: The PowerShell scripts (`init-triage-session.ps1` and `query-issues.ps1`) don't verify that the GitHub CLI (`gh`) is installed or authenticated before trying to use it. When `gh` is missing, the scripts fail with cryptic errors instead of helpful messages.

2. **Fragile milestone fetching**: `init-triage-session.ps1` uses `gh api` to fetch milestones, then parses the JSON output line-by-line. This is brittle — PowerShell has `Invoke-RestMethod` which handles JSON natively and doesn't require `gh` for simple unauthenticated API calls.

3. **Missing workflow guidance**: The SKILL.md documentation doesn't warn agents against common mistakes like:
   - Using ad-hoc GitHub API queries instead of the skill's scripts (which have proper exclusion filters)
   - Guessing milestone names like "SR2" or "SR3" instead of using actual names from the init session
   - Stopping and asking the user when an issue batch runs out, instead of automatically loading more

## Expected Behavior

- Both scripts should check that `gh` is installed and authenticated at the start, exiting with clear installation instructions if not
- `init-triage-session.ps1` should use `Invoke-RestMethod` for milestone fetching instead of `gh api` parsing
- SKILL.md should document prerequisites, the critical rule to always use skill scripts, what to do when a batch runs out (Step 6), and a table of common mistakes to avoid

## Files to Look At

- `.github/skills/issue-triage/SKILL.md` — Skill documentation that agents read during triage
- `.github/skills/issue-triage/scripts/init-triage-session.ps1` — Session initialization script
- `.github/skills/issue-triage/scripts/query-issues.ps1` — Issue query script

After making the code changes, update the SKILL.md documentation to reflect the new behavior and add guidance to prevent the workflow mistakes described above.
