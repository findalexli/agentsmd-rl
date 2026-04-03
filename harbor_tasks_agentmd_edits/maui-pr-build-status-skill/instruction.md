# Add a Copilot CLI Skill for Querying PR Build Status

## Problem

The .NET MAUI repository uses Azure DevOps (dnceng-public org, public project) for CI/CD builds triggered by GitHub PRs. Currently, there is no way for Copilot CLI to help developers investigate build failures — they have to manually navigate Azure DevOps web UI to find build IDs, check which stages failed, and dig through logs for error messages and test failures.

## What's Needed

Create a new Copilot CLI skill at `.github/skills/pr-build-status/` that allows Copilot to query Azure DevOps build information for GitHub PRs. The skill should include:

1. **A SKILL.md file** with proper frontmatter (name, description, metadata) documenting the skill, its scripts, workflow, and prerequisites. This is the agent config file that Copilot CLI reads to understand the skill's capabilities.

2. **PowerShell scripts** in a `scripts/` subdirectory that implement the actual Azure DevOps API queries:
   - A script to get Azure DevOps build IDs associated with a GitHub PR number (using `gh pr checks` to find DevOps links)
   - A script to get detailed build status including stages, results, and failed/canceled jobs (using the Azure DevOps builds and timeline APIs)
   - A script to get build errors and test failures from build logs — extracting MSBuild errors, `##[error]` markers, and failed test details with error messages and stack traces (using the timeline API to find failed tasks/jobs and their log URLs)

## Requirements

- All Azure DevOps API calls must target the public `dnceng-public` org and `public` project (no auth needed)
- Scripts should use `pwsh` (PowerShell 7+) and accept parameters via `[CmdletBinding()] param(...)` blocks
- The build ID retrieval script should default to `dotnet/maui` as the repo
- Build info and error scripts should accept a BuildId parameter and support filtering (e.g., failed-only, errors-only, tests-only)
- GitHub CLI (`gh`) is required for the PR checks query
- After implementing the scripts, update the SKILL.md to document the complete skill including all scripts, their usage, the recommended workflow, and prerequisites

## Files to Look At

- `.github/copilot-instructions.md` — existing Copilot config; see the "Custom Agents" section for how skills/agents are documented in this repo
- `.github/skills/` — this directory doesn't exist yet; you'll create it
