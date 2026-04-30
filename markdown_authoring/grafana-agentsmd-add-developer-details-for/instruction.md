# AGENTS.md: Add developer details for the AGENTS.md

Source: [grafana/grafana#117926](https://github.com/grafana/grafana/pull/117926)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `docs/AGENTS.md`

## What to add / change

<!--

Thank you for sending a pull request! Here are some tips:

1. If this is your first time, please read our contribution guide at https://github.com/grafana/grafana/blob/main/CONTRIBUTING.md

2. Ensure you include and run the appropriate tests as part of your Pull Request.

3. In a new feature or configuration option, an update to the documentation is necessary. Everything related to the documentation is under the docs folder in the root of the repository.

4. If the Pull Request is a work in progress, make use of GitHub's "Draft PR" feature and mark it as such.

5. If you can not merge your Pull Request due to a merge conflict, Rebase it. This gets it in sync with the main branch.

6. Name your PR as "<FeatureArea>: Describe your change", e.g. Alerting: Prevent race condition. If it's a fix or feature relevant for the changelog describe the user impact in the title. The PR title is used to auto-generate the changelog for issues marked with the "add to changelog" label.

7. If your PR content should be added to the What's New document for the next major or minor release, add the **add to what's new** label to your PR. Note that you should add this label to the main PR that introduces the feature; do not add this label to smaller PRs for the feature.

-->

**What is this feature?**

Add more dev tooling guidance to the AGENTS.md file

**Why do we need this feature?**

I noticed the grafana/grafana AGENTS.md file only talked about creating document

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
