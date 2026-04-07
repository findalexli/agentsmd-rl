# Revamp find-reviewable-pr Skill: Add New Priority Categories and Fix Defaults

## Problem

The `find-reviewable-pr` skill's PowerShell script (`query-reviewable-prs.ps1`) and its documentation (`SKILL.md`) are out of date. The script currently defaults to showing all categories, but in practice reviewers primarily need to see P/0 and milestoned PRs. The script also lacks several important PR categories that the team now tracks:

1. **Approved (Not Merged)** PRs that have human approval but haven't been merged yet
2. **Ready To Review** PRs from the MAUI SDK Ongoing project board
3. **Agent Reviewed** PRs that have been analyzed by the AI agent workflow (detected via `s/agent-reviewed`, `s/agent-approved`, `s/agent-changes-requested` labels)

Additionally, the script's default `-Limit` is too low, and the output is missing the Assignees column and agent review status.

## Expected Behavior

**Script changes:**
- Default `-Category` should be `"default"` (not `"all"`), showing only P/0 + milestoned PRs and excluding changes-requested PRs
- Default `-Limit` should be `100` (not `10`)
- Add three new categories to the `-Category` ValidateSet: `"approved"`, `"ready-to-review"`, `"agent-reviewed"` (plus `"default"`)
- Add new queries to fetch approved, agent-reviewed, and agent-approved PRs
- Add Assignees field to processed PR output objects
- Track agent label status (`s/agent-approved`, `s/agent-reviewed`, `s/agent-changes-requested`) and approved/ready-to-review state per PR
- Add a `Write-PREntry` helper function to replace the repeated per-category output blocks
- Implement a `Get-ReadyToReviewPRNumbers` function that queries the MAUI SDK Ongoing project board via GraphQL
- Update the priority ordering to: P/0 > Approved > Ready To Review > Milestoned > Agent Reviewed > Partner > Community > Recent > docs-maui
- Update the category switch, output functions, summary, and JSON output to support all new categories

**Documentation changes:**
- Update the SKILL.md to accurately reflect all script changes: new priority order (9 categories), new parameter values, corrected defaults, new Quick Start examples, and updated table columns (including Assignees and Agent Review)

## Files to Look At

- `.github/skills/find-reviewable-pr/scripts/query-reviewable-prs.ps1` — the PowerShell script that queries GitHub for reviewable PRs
- `.github/skills/find-reviewable-pr/SKILL.md` — the skill documentation that agents read to understand how to use this skill
