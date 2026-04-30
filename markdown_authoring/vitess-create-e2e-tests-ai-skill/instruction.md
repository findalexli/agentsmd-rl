# Create e2e tests AI skill

Source: [vitessio/vitess#19396](https://github.com/vitessio/vitess/pull/19396)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/e2e-tests/SKILL.md`

## What to add / change

<!--
  Thank you for your contribution to the Vitess project.
  How to contribute: https://vitess.io/docs/contributing/
  Please first make sure there is an open Issue to discuss the feature/fix suggested in this PR.
  If this is a new feature, please mark the Issue as "RFC".
 -->

<!-- if this PR is Work in Progress please create it as a Draft Pull Request -->

## Description

<!-- A few sentences describing the overall goals of the pull request's commits. -->
<!-- If this is a bug fix and you think the fix should be backported, please write so. -->
Creates an [AI skill](https://agentskills.io/home) for running and debugging end-to-end tests. In my experience, AI struggles knowing how to run them, not realizing it needs to rebuild binaries, or not knowing where it should look for logs (it's just like me!). This creates a skill under `.claude/skills`, which most CLIs should support (`.agents` is the agent-agnostic directory, but Claude Code (annoyingly) does not support it).
## Related Issue(s)

<!-- List related issues and pull requests. If this PR fixes an issue, please add it using Fixes #????  -->

## Checklist

-   [ ] "Backport to:" labels have been added if this change should be back-ported to release branches
-   [ ] If this change is to be back-ported to previous releases, a justification is included in the PR description
-   [ ] Tests were added or are not required
-   [ ] Did the new or modified tests pass consistently locally and on CI?
-  

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
