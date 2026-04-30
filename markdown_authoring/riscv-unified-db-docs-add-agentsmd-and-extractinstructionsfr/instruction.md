# docs: add AGENTS.md and extract-instructions-from-subsection skill

Source: [riscv/riscv-unified-db#1734](https://github.com/riscv/riscv-unified-db/pull/1734)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/extract-instructions-from-subsection/SKILL.md`
- `AGENTS.md`

## What to add / change

## Summary

### AGENTS

- Adds `AGENTS.md` to provide Generative AI tools such as Claude Code with project-specific guidance
- Documents common commands for regression testing, generation, and development chores
- Describes repository structure, data model, Ruby gem architecture, IDL, backends, and CI/pre-commit workflow

### Skill to extract instructions from a subsection of a spec file
- Adds `SKILL.md` to `.claude/skills/extract-instructions-from-subsection/` directory

## Test plan

- [ ] No functional code changes; verify file renders correctly on GitHub
- [ ] Confirm pre-commit hooks pass (YAML/JSON linting, prettier)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
