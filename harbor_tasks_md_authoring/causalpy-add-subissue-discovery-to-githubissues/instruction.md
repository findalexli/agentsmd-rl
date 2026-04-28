# Add sub-issue discovery to github-issues skill

Source: [pymc-labs/CausalPy#817](https://github.com/pymc-labs/CausalPy/pull/817)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/skills/github-issues/reference/issue-evaluation.md`
- `.github/skills/github-issues/reference/parent-child-issues.md`

## What to add / change

## Summary

Add sub-issue discovery guidance to the github-issues skill so agents check for native GitHub sub-issues when evaluating issues.

- **issue-evaluation.md**: Add a "Check for sub-issues" step using the `subIssues` / `parent` GraphQL fields, and note to review sub-issues during context analysis.
- **parent-child-issues.md**: Add a "Discover existing sub-issues" section (step 6) with the correct GraphQL query and a warning not to use the older `trackedIssues` / `trackedInIssues` fields.

## Motivation

GitHub's native sub-issues use the `subIssues` GraphQL field, not `trackedIssues`. Without this guidance, agents default to the wrong API and silently miss existing sub-issues on a parent issue.

## Test plan

- [x] Skill files are valid markdown
- [x] No code changes; documentation-only

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
