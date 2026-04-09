# Integrate Vouch Trust Management System

## Problem

The repository needs to implement the [vouch](https://github.com/mitchellh/vouch) trust management system to manage contributor trust. This involves:

1. **Workflow automation** for checking if issue/PR authors are denounced and auto-closing their contributions
2. **Compliance checking** to ensure issues follow templates (with a 2-hour grace period)
3. **Maintainer tooling** to vouch/denounce users via issue comments
4. **Documentation updates** explaining the system to contributors

The current repository lacks:
- `.github/VOUCHED.td` — the vouch list file
- `.github/workflows/vouch-check-issue.yml` — auto-close issues from denounced users
- `.github/workflows/vouch-check-pr.yml` — auto-close PRs from denounced users
- `.github/workflows/vouch-manage-by-issue.yml` — allow maintainers to manage vouch via comments
- `.github/workflows/compliance-close.yml` — close non-compliant issues/PRs after 2 hours
- Updates to `.github/workflows/duplicate-issues.yml` — add compliance check alongside duplicate detection
- Updates to `.github/ISSUE_TEMPLATE/config.yml` — disable blank issues
- Updates to `CONTRIBUTING.md` — document the trust system and issue requirements

## Expected Behavior

After implementation:

1. When a new issue is opened, it should be checked against the denounced list and auto-closed if the author is denounced
2. When a new PR is opened, it should be similarly checked and auto-closed if denounced
3. Non-compliant issues (not following templates) should receive a comment with `<!-- issue-compliance -->` marker and be closed after 2 hours
4. Maintainers can comment `vouch @user`, `denounce @user <reason>`, or `unvouch @user` on issues to manage the vouch list
5. CONTRIBUTING.md should explain the trust system, maintainer commands, denouncement policy, and issue requirements
6. Blank issues should be disabled via the issue template configuration

## Files to Look At

- `.github/workflows/` — create new workflow files and update existing ones
- `.github/VOUCHED.td` — create the vouch list file
- `.github/ISSUE_TEMPLATE/config.yml` — disable blank issues
- `CONTRIBUTING.md` — add Trust & Vouch System and Issue Requirements sections

## Implementation Notes

- The workflows use `actions/github-script@v7` for API interactions
- The vouch list file uses a simple text format: one username per line, `-username` for denounced
- The compliance workflow looks for issues/PRs with the `needs:compliance` label and a comment containing `<!-- issue-compliance -->`
- Don't forget to update the documentation to explain all these changes to contributors!
