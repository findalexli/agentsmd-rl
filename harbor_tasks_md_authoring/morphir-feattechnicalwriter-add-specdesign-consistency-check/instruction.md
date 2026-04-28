# feat(technical-writer): Add spec/design consistency check capability

Source: [finos/morphir#577](https://github.com/finos/morphir/pull/577)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/technical-writer/SKILL.md`
- `.claude/skills/technical-writer/references/spec-design-consistency.md`

## What to add / change

## Summary

- Add spec/design consistency check capability to the technical-writer skill
- Create comprehensive checklist document for reviewing spec documents against design documents
- Cover naming conventions, type/value nodes, JSON serialization, and directory structure validation

## Changes

- **SKILL.md**: Added capability #9 for Spec/Design Consistency with new workflow section
- **spec-design-consistency.md**: New reference document with detailed checklists for:
  - Canonical string format validation
  - Type/value node coverage verification
  - Specifications vs definitions documentation
  - JSON serialization format checks
  - Directory structure validation (Document Tree mode)
  - Cross-reference and terminology validation

## Test plan

- [ ] Review the checklist document for completeness
- [ ] Apply checklist to existing spec documents to verify utility

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
