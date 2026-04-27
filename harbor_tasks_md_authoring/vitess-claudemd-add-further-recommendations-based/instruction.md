# `CLAUDE.md`: add further recommendations based on testing 

Source: [vitessio/vitess#19671](https://github.com/vitessio/vitess/pull/19671)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

<!--
  Thank you for your contribution to the Vitess project.
  How to contribute: https://vitess.io/docs/contributing/
  Please first make sure there is an open Issue to discuss the feature/fix suggested in this PR.
  If this is a new feature, please mark the Issue as "RFC".
 -->

<!-- if this PR is Work in Progress please create it as a Draft Pull Request -->

## Description

This PR adds a few tweaks to `CLAUDE.md` ~~and the `e2e-tests` Claude-skill~~ based on some snags I've ran into while using Claude Code

For the most part, there are few cases where Claude is missing project-specific context and norms. It's also forgetting to run `gofumpt` often, so that signal is strengthened

~~For `e2e-tests`, the main issue is the skill has trouble understanding how to teardown the cluster, despite there being a script clearly named that~~

## Related Issue(s)

<!-- List related issues and pull requests. If this PR fixes an issue, please add it using Fixes #????  -->

## Checklist

-   [x] "Backport to:" labels have been added if this change should be back-ported to release branches
-   [x] If this change is to be back-ported to previous releases, a justification is included in the PR description
-   [x] Tests were added or are not required
-   [x] Did the new or modified tests pass consistently locally and on CI?
-   [x] Documentation was added or is not required

## Deployment Notes

<!-- Notes regarding deployment of the contained body of work. The

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
