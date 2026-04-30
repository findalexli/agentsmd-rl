# feat(ai): codify 7-day reassignment rule in ticket-intake (#10215)

Source: [neomjs/neo#10413](https://github.com/neomjs/neo/pull/10413)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agent/skills/ticket-intake/references/ticket-intake-workflow.md`

## What to add / change

## The Intent
Codifies the existing 7-day reassignment rule from `CONTRIBUTING.md` into the active agent `ticket-intake` skill protocol, satisfying sub-issue #10215 of Epic #10214.

## The Architecture
- Replaces the blind `manage_issue_assignees` auto-assign in `.agent/skills/ticket-intake/references/ticket-intake-workflow.md` section 3a.
- Introduces a read-before-write check (via `get_local_issue_by_id`).
- Codifies the 7-day grace period, defining "qualifying feedback" (assignee or maintainer comment) and requiring a mandatory attribution comment for self-serve reassignments.

## The Empiricism
- Verified the markdown edits syntactically.
- Verified alignment with existing Neo.mjs contribution guidelines.

## The Approval Gate
- Required: Cross-family peer review per #10208 mandate.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
