# docs: add functional programming guidelines to AGENTS.md

Source: [softmaple/softmaple#504](https://github.com/softmaple/softmaple/pull/504)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/CLAUDE.md`
- `AGENTS.md`

## What to add / change

- Add FP principles: pure functions, immutability, higher-order functions, function composition
- Include TypeScript examples showing good vs bad patterns
- Encourage functional patterns where possible throughout codebase

<!-- ref: https://docs.github.com/en/issues/tracking-your-work-with-issues/linking-a-pull-request-to-an-issue#linking-a-pull-request-to-an-issue-using-a-keyword -->
<!-- If it fixed a bug, please use **fixes #<issue-number>** -->
<!-- If it resolved a issue, please use **resolves #<issue-number>** -->
<!-- otherwise, use **closes #<issue-number>** instead. -->
Fixes #466 .

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

* **Documentation**
  * Added a comprehensive "Functional Programming Principles" section covering pure functions, immutability, higher-order functions, and composition with practical examples.
  * Added a new coding guidelines document outlining FP-first practices, TypeScript recommendations, error handling, testing philosophy, development workflow, and package-specific guidance.
  * Updated branch-naming guidance to require creating feature branches instead of committing directly to the default branch.
  * Minor alignment with existing testing guidelines.

<sub>✏️ Tip: You can customize this high-level summary in your review settings.</sub>
<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
