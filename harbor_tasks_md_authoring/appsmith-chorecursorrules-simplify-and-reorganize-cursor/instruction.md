# chore(cursor-rules): simplify and reorganize cursor rules for CE

Source: [appsmithorg/appsmith#41691](https://github.com/appsmithorg/appsmith/pull/41691)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/agent-behavior.mdc`
- `.cursor/rules/backend.mdc`
- `.cursor/rules/commit/semantic-pr-validator.mdc`
- `.cursor/rules/commit/semantic-pr.md`
- `.cursor/rules/frontend.mdc`
- `.cursor/rules/index.md`
- `.cursor/rules/index.mdc`
- `.cursor/rules/infra.mdc`
- `.cursor/rules/quality/performance-optimizer.mdc`
- `.cursor/rules/quality/pre-commit-checks.mdc`
- `.cursor/rules/task-list.mdc`
- `.cursor/rules/testing/test-generator.mdc`
- `.cursor/rules/verification/bug-fix-verifier.mdc`
- `.cursor/rules/verification/feature-implementation-validator.mdc`
- `.cursor/rules/verification/feature-verifier.mdc`
- `.cursor/rules/verification/workflow-validator.mdc`

## What to add / change

## Description

Reorganize and simplify `.cursor/rules/` for the CE codebase:

- **Added** focused domain rules: `agent-behavior.mdc`, `backend.mdc`, `frontend.mdc`, `infra.mdc`
- **Simplified** existing rules (`index.mdc`, `semantic-pr-validator.mdc`, `performance-optimizer.mdc`, `test-generator.mdc`, `bug-fix-verifier.mdc`, `feature-verifier.mdc`, `workflow-validator.mdc`) — reduced verbosity and removed redundant content
- **Removed** obsolete/redundant rules: `semantic-pr.md`, `index.md`, `pre-commit-checks.mdc`, `task-list.mdc`, `feature-implementation-validator.mdc`

Net result: **+443 / -3,764 lines** — leaner, more actionable rules.

## Communication
Should the DevRel and Marketing teams inform users about this change?
- [ ] Yes
- [x] No


Made with [Cursor](https://cursor.com)

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

* **Documentation**
  * Added comprehensive stack and infrastructure documentation for backend, frontend, and infra.
  * Added agent behavior, task-management, and workflow guidance.
  * Replaced previously automated validation rules with static reference checklists for PRs, testing, bug fixes, feature implementation, performance, and workflow reviews.
  * Consolidated and restructured rule indexing into an architecture-oriented overview.
* **Chores**
  * Removed legacy executable rule implementations and activation hooks.
<!-- end of auto-generated comment: release notes by coderabbit.ai -->



## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
