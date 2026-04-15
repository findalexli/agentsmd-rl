# Revamp find-reviewable-pr Skill: New Priority Categories and Updated Defaults

## Problem

The `find-reviewable-pr` skill in the dotnet/maui repository needs updates to both its PowerShell script and its SKILL.md documentation. The skill is located at:

- `.github/skills/find-reviewable-pr/scripts/query-reviewable-prs.ps1`
- `.github/skills/find-reviewable-pr/SKILL.md`

### What's Wrong

1. **Missing PR categories**: The script doesn't support several categories the team now tracks:
   - **Approved (Not Merged)** — PRs with human approval that haven't been merged yet
   - **Ready To Review** — PRs from the MAUI SDK Ongoing project board
   - **Agent Reviewed** — PRs analyzed by the AI agent workflow (detected via `s/agent-reviewed` and `s/agent-approved` labels)

2. **Inadequate defaults**: Without arguments, the script defaults to showing all PR categories. In practice, reviewers primarily need to see P/0 and milestoned PRs. The `-Limit` parameter default is also too restrictive.

3. **Missing output fields**: PR entries don't include assignee information or agent review status.

4. **Documentation outdated**: SKILL.md doesn't document the new categories, updated defaults, or the Assignees output column.

## Requirements

### PowerShell Script (`query-reviewable-prs.ps1`)

**Existing structure to preserve**: The script already defines these helper functions that must be retained: `Invoke-GitHubWithRetry`, `Add-UniquePRs`, `Get-ReviewStatus`, `Get-ProjectStatus`, `Get-PRCategory`, `Get-PRComplexity`. The script uses a `param()` block with `[ValidateSet(...)]` parameter validation and sets `$ErrorActionPreference`.

**Parameter defaults**: When invoked without arguments, the script must use `$Category = "default"` and `$Limit = 100`. The `-Category` parameter's ValidateSet must accept `"default"`, `"approved"`, `"ready-to-review"`, and `"agent-reviewed"` (among any existing values).

**New functions needed**: The script must define a function named `Write-PREntry` for formatting and outputting individual PR entries, and a function named `Get-ReadyToReviewPRNumbers` for fetching PR numbers from the MAUI SDK Ongoing project board via GraphQL.

**Default category behavior**: The `"default"` category must combine P/0 and milestoned PRs while filtering out any PRs with `CHANGES_REQUESTED` review status. The category switch must include a `"default"` case, and the merged results must be held in a `$defaultPRs` variable.

**PR data fields**: Each PR output object must include an `Assignees` field. The script must reference the labels `s/agent-reviewed` and `s/agent-approved`.

### SKILL.md Documentation

**Priority Categories section**: Must list at least 9 numbered categories. The following categories must be included:
- **Approved (Not Merged)** — PRs with human approval not yet merged
- **Ready To Review** — PRs from the MAUI SDK Ongoing project board
- **Agent Reviewed** — PRs analyzed by the AI agent workflow

**Required sections**: The document must include `## Priority Categories`, `## Quick Start`, and `## Script Parameters` sections. Usage examples must use ` ```bash ` code blocks. P/0 must be documented as a priority category.

**Parameter table**: The parameter documentation table must show `-Category` defaulting to `default` and `-Limit` defaulting to `100`.

**Output columns**: The documented output columns must include `Assignees`.

## Files to Look At

- `.github/skills/find-reviewable-pr/scripts/query-reviewable-prs.ps1` — the PowerShell script that queries GitHub for reviewable PRs
- `.github/skills/find-reviewable-pr/SKILL.md` — the skill documentation that agents read to understand how to use this skill
