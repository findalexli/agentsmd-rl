# docs(rules): add pr_workflow.md with lessons from PR #806

Source: [llama-farm/llamafarm#807](https://github.com/llama-farm/llamafarm/pull/807)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/rules/pr_workflow.md`

## What to add / change

## Summary

Adds `.claude/rules/pr_workflow.md` capturing workflow guidance that emerged from the long review cycle on #806 (offline-mode deployment story). Five practical gotchas worth documenting for future AI-assisted work in this repo:

1. **Verify CI after pushing** — don't stop at "pushed"; query `statusCheckRollup` + `code-scanning/alerts` via `gh api`. Distinguish `BLOCKED` by review from `BLOCKED` by CI.

2. **Bot reviewers re-post stale comments** — cubic / qodo / github-advanced-security re-comment on every new commit with updated line numbers, producing duplicates. Use the `code-scanning/alerts` API as the authoritative state, not the PR comment list. Dismiss known false positives via API with detailed justification rather than endless restructuring.

3. **CodeQL py/path-injection requires basic-block locality** — the sanitizer and sink must be in the same basic block. Helper functions break the analysis because parameters re-taint on return. The pattern that works: realpath + commonpath in a compound conditional with the filesystem sink. Patterns that don't: startswith, Path wrapping, cross-function helpers.

4. **Pre-existing bugs can surface on merge** — concurrent-write races and Unicode encoding crashes only fire under specific timing or log content. Before assuming a failure is caused by your PR, check if the same test passed on the last green main and whether your PR actually touches the failing code path.

5. **Windows UTF-8 stdout reconfigure** — Python r

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
