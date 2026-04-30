# docs: add AGENT.md

Source: [alibaba/OpenSandbox#36](https://github.com/alibaba/OpenSandbox/pull/36)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

# Summary
add AGENT.md

# Testing
- [ x ] Not run (explain why)
- [ ] Unit tests
- [ ] Integration tests
- [ ] e2e / manual verification

# Breaking Changes
- [x ] None
- [ ] Yes (describe impact and migration path)

# Checklist
- [ ] Linked Issue or clearly described motivation
- [ ] Added/updated docs (if needed)
- [ ] Added/updated tests (if needed)
- [ ] Security impact considered
- [ ] Backward compatibility considered

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
