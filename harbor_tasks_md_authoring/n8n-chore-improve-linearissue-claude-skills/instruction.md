# chore: Improve linear-issue claude skills (no-changelog)

Source: [n8n-io/n8n#27970](https://github.com/n8n-io/n8n/pull/27970)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/plugins/n8n/skills/linear-issue/SKILL.md`

## What to add / change

## Summary

Adds a security layer to 2 claude skills to check linear issues for critical labels before continuing.

## Related Linear tickets, Github issues, and Community forum posts

https://linear.app/n8n/issue/CAT-2732

## Review / Merge checklist

- [x] PR title and summary are descriptive. ([conventions](../blob/master/.github/pull_request_title_conventions.md)) <!--
   **Remember, the title automatically goes into the changelog.
   Use `(no-changelog)` otherwise.**
-->
- [ ] [Docs updated](https://github.com/n8n-io/n8n-docs) or follow-up ticket created.
- [ ] Tests included. <!--
   A bug is not considered fixed, unless a test is added to prevent it from happening again.
   A feature is not complete without tests.
-->
- [ ] PR Labeled with `Backport to Beta`, `Backport to Stable`, or `Backport to v1` (if the PR is an urgent fix that needs to be backported)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
