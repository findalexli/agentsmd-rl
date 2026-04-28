# chore: optimize cursor rules

Source: [vltpkg/vltpkg#1458](https://github.com/vltpkg/vltpkg/pull/1458)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/cli-sdk-workspace.mdc`
- `.cursor/rules/code-validation-workflow.mdc`
- `.cursor/rules/config-reload-jackspeak-issues.mdc`
- `.cursor/rules/cursor-rules-location.mdc`
- `.cursor/rules/graph/data-structure.mdc`
- `.cursor/rules/graph/ideal-append-nodes.mdc`
- `.cursor/rules/graph/ideal.mdc`
- `.cursor/rules/graph/index.mdc`
- `.cursor/rules/graph/load-actual.mdc`
- `.cursor/rules/graph/lockfiles.mdc`
- `.cursor/rules/graph/modifiers.mdc`
- `.cursor/rules/graph/peers.mdc`
- `.cursor/rules/graph/reify.mdc`
- `.cursor/rules/gui-validation-workflow.mdc`
- `.cursor/rules/index.mdc`
- `.cursor/rules/linting-error-handler.mdc`
- `.cursor/rules/monorepo-structure.mdc`
- `.cursor/rules/query-pseudo-selector-creation.mdc`
- `.cursor/rules/registry-development.mdc`

## What to add / change

Modernize and most importantly, compact our existing cursor rules and make sure they're applied to files it make sense to.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
