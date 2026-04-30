# chore: adding agents.md for copilot

Source: [open-policy-agent/gatekeeper-library#676](https://github.com/open-policy-agent/gatekeeper-library/pull/676)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

**What this PR does / why we need it**:

**Which issue(s) does this PR fix** *(optional, using `fixes #<issue number>(, fixes #<issue_number>, ...)` format, will close the issue(s) when the PR gets merged)*:
Fixes #

<!--
**Are you making changes to Gatekeeper Library policies?**
Please refer to [How to contribute to the library](https://open-policy-agent.github.io/gatekeeper-library/website/#how-to-contribute-to-the-library) to add new policies or update existing policies.

**Are you updating an existing policy?**
Please run `make generate generate-website-docs generate-artifacthub-artifacts` to generate the templates and docs.
-->

**Special notes for your reviewer**:

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
