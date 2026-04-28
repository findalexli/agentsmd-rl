# Add more claude rules

Source: [stacklok/toolhive#4782](https://github.com/stacklok/toolhive/pull/4782)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/rules/go-style.md`
- `.claude/rules/testing.md`

## What to add / change

## Summary

<!--
REQUIRED. You MUST explain:
1. WHY this change is needed (the problem or motivation)
2. WHAT changed (concise bullet points)

The diff shows the code — your summary must provide the context a reviewer
needs to understand the purpose without reading the diff first.
-->
Generate more rules about style and testing, extrapolated from the comments and bugs in latest prs and reviews

<!--
Link related issues. Use "Closes" or "Fixes" to auto-close on merge.
Remove this line if there is no related issue.
-->


## Type of change

<!-- REQUIRED. Check exactly one. -->

- [ ] Bug fix
- [ ] New feature
- [ ] Refactoring (no behavior change)
- [ ] Dependency update
- [x] Documentation
- [ ] Other (describe):

## Test plan

<!--
REQUIRED. Check every verification step you actually ran.
You MUST check at least one item. If you only did manual testing,
describe exactly what you tested below the checkbox.
-->

- [ ] Unit tests (`task test`)
- [ ] E2E tests (`task test-e2e`)
- [x] Linting (`task lint-fix`)
- [ ] Manual testing (describe below)

## Changes

<!--
Optional — include for PRs touching more than a few files to help
reviewers navigate the diff. Remove this entire section for small PRs.
-->

| File | Change |
|------|--------|
|      |        |

## Does this introduce a user-facing change?

<!--
If yes, describe the change from the user's perspective. This helps with release notes.
If no, write "No".
Remove thi

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
