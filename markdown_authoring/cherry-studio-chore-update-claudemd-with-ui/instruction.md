# chore: update CLAUDE.md with UI design migration details

Source: [CherryHQ/cherry-studio#10021](https://github.com/CherryHQ/cherry-studio/pull/10021)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

Add section about migrating from antd & styled-components to HeroUI, including link to HeroUI docs.

<!-- Template from https://github.com/kubevirt/kubevirt/blob/main/.github/PULL_REQUEST_TEMPLATE.md?-->
<!--  Thanks for sending a pull request!  Here are some tips for you:
1. Consider creating this PR as draft: https://github.com/CherryHQ/cherry-studio/blob/main/CONTRIBUTING.md
-->

### What this PR does

Before this PR:

After this PR:

<!-- (optional, in `fixes #<issue number>(, fixes #<issue_number>, ...)` format, will close the issue(s) when PR gets merged)*: -->

Fixes #

### Why we need it and why it was done in this way

The following tradeoffs were made:

The following alternatives were considered:

Links to places where the discussion took place: <!-- optional: slack, other GH issue, mailinglist, ... -->

### Breaking changes

<!-- optional -->

If this PR introduces breaking changes, please describe the changes and the impact on users.

### Special notes for your reviewer

<!-- optional -->

### Checklist

This checklist is not enforcing, but it's a reminder of items that could be relevant to every PR.
Approvers are expected to review this list.

- [ ] PR: The PR description is expressive enough and will help future contributors
- [ ] Code: [Write code that humans can understand](https://en.wikiquote.org/wiki/Martin_Fowler#code-for-humans) and [Keep it simple](https://en.wikipedia.org/wiki/KISS_principle)
- [ ] Refactor: You

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
