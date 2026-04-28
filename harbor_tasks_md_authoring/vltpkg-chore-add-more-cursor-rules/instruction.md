# chore: add more cursor rules

Source: [vltpkg/vltpkg#1473](https://github.com/vltpkg/vltpkg/pull/1473)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/catalogs.mdc`
- `.cursor/rules/dep-id.mdc`
- `.cursor/rules/docs-website.mdc`
- `.cursor/rules/dss-breadcrumb.mdc`
- `.cursor/rules/install-build-phases.mdc`
- `.cursor/rules/registries-and-auth.mdc`
- `.cursor/rules/security-archive.mdc`
- `.cursor/rules/smoke-tests.mdc`
- `.cursor/rules/spec-parsing.mdc`
- `.cursor/rules/vlt-json-config.mdc`
- `.cursor/rules/vlx.mdc`
- `.cursor/rules/workspaces.mdc`

## What to add / change

Adds extra context when working with specific subsystems of the vlt CLI.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
