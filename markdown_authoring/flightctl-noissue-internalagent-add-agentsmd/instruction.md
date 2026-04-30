# NO-ISSUE: internal/agent: add AGENTS.md

Source: [flightctl/flightctl#1653](https://github.com/flightctl/flightctl/pull/1653)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `internal/agent/AGENTS.md`

## What to add / change

This PR is intended to provide context for Ai agents which are contributing to this repo. There should be a balance between moving quickly and ensuring the project remains maintainable and stable. This document serves as a source of truth to improve iteration.

ref. https://agents.md/#examples

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

* **Documentation**
  * Added "Flightctl Agent Contribution Guidelines" for agent contributors.
  * Clarifies agent responsibilities (reconciliation, resource reporting, app lifecycle, OS config).
  * Describes architecture and key components (boot/init, queuing, file operations, managers).
  * Outlines failure handling, threading model, graceful shutdown, and config reload.
  * Establishes core principles, testing standards, test scaffold, and a code review checklist.
<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
