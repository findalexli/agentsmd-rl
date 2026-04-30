# chore: move cursor rules into correct directory

Source: [grafana/synthetic-monitoring-app#1484](https://github.com/grafana/synthetic-monitoring-app/pull/1484)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/documentation.mdc`
- `.cursor/rules/engineering-best-practices.mdc`
- `.cursor/rules/file-organisation.mdc`
- `.cursor/rules/reference-directory.mdc`
- `.cursor/rules/team-composition.mdc`
- `.cursor/rules/this-product.mdc`
- `.cursor/rules/when-creating-prs.mdc`
- `.cursor/rules/when-writing-tests.mdc`
- `.cursor/rules/you-and-me.mdc`

## What to add / change

I noticed I had put the cursor rules in the wrong directory. This is to put them in the right place so they are read.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
