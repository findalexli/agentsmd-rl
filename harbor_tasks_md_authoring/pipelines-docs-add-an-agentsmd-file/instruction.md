# docs: Add an AGENTS.md file

Source: [kubeflow/pipelines#12254](https://github.com/kubeflow/pipelines/pull/12254)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

**Description of your changes:**

This is an initial AGENTS.md file we can iterate to help AI code editors.

**Checklist:**
- [x] You have [signed off your commits](https://www.kubeflow.org/docs/about/contributing/#sign-off-your-commits)
- [x] The title for your pull request (PR) should follow our title convention. [Learn more about the pull request title convention used in this repository](https://github.com/kubeflow/pipelines/blob/master/CONTRIBUTING.md#pull-request-title-convention). 
<!--
   PR titles examples:
    * `fix(frontend): fixes empty page. Fixes #1234`
       Use `fix` to indicate that this PR fixes a bug.
    * `feat(backend): configurable service account. Fixes #1234, fixes #1235`
       Use `feat` to indicate that this PR adds a new feature. 
    * `chore: set up changelog generation tools`
       Use `chore` to indicate that this PR makes some changes that users don't need to know.
    * `test: fix CI failure. Part of #1234`
        Use `part of` to indicate that a PR is working on an issue, but shouldn't close the issue when merged.
-->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
