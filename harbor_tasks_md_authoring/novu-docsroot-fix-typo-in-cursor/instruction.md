# docs(root): fix typo in cursor dashboard rules

Source: [novuhq/novu#9704](https://github.com/novuhq/novu/pull/9704)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/dashboard.mdc`

## What to add / change

### What changed? Why was the change needed?

Fixed a typo in the dashboard rules documentation (`.cursor/rules/dashboard.mdc`). Removed duplicate "to" in line 6, changing "Do not attempt to **to** build" to "Do not attempt to build".

This corrects a grammatical error in the documentation that explains developers should not attempt to build or run the dashboard locally, as it's already running.

### Screenshots

N/A - Documentation-only change (text correction in markdown file)

<details>
<summary><strong>Expand for optional sections</strong></summary>

### Related enterprise PR
<!-- A link to a dependent pull request  -->

### Special notes for your reviewer
This is a minor documentation fix with no functional changes to the codebase.

</details>

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
