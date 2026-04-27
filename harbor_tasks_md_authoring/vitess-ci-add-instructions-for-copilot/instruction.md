# `ci`: add instructions for Copilot

Source: [vitessio/vitess#19724](https://github.com/vitessio/vitess/pull/19724)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

<!--
  Thank you for your contribution to the Vitess project.
  How to contribute: https://vitess.io/docs/contributing/
  Please first make sure there is an open Issue to discuss the feature/fix suggested in this PR.
  If this is a new feature, please mark the Issue as "RFC".
 -->

<!-- if this PR is Work in Progress please create it as a Draft Pull Request -->

## Description

This PR adds a repo config for Copilot. This should help reduce some of the lower confidence and lower severity comments

Feel free to make edits directly to the PR if you have suggestions

## Related Issue(s)

<!-- List related issues and pull requests. If this PR fixes an issue, please add it using Fixes #????  -->

## Checklist

-   [x] "Backport to:" labels have been added if this change should be back-ported to release branches
-   [x] If this change is to be back-ported to previous releases, a justification is included in the PR description
-   [x] Tests were added or are not required
-   [x] Did the new or modified tests pass consistently locally and on CI?
-   [x] Documentation was added or is not required

## Deployment Notes

<!-- Notes regarding deployment of the contained body of work. These should note any db migrations, etc. -->

### AI Disclosure

<!-- 
  A sentence or two describing whether AI was used to author any of the code in this pull request
  Example: "This PR was written primarily by Claude Code" or "Tests written by GPT-5"
  For more informa

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
