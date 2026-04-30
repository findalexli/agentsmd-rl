# chore(CLAUDE.md): add shared UI component lock convention to CLAUDE.md

Source: [infiniflow/ragflow#14381](https://github.com/infiniflow/ragflow/pull/14381)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `web/CLAUDE.md`

## What to add / change

### What problem does this PR solve?

AI coding agents (Claude, Copilot, etc.) tend to directly edit files in `src/components/ui/` when asked to tweak styles or add props, treating them like ordinary feature code. This silently breaks the shared component library that both shadcn primitives and project-authored common components live in.

This PR adds a `Shared UI Component Lock` convention to `web/CLAUDE.md` to instruct AI agents to treat the entire `src/components/ui/` directory as read-only. Any customization must be done via wrappers or composition outside the directory; exceptions require explicit user approval.

### Type of change
- [x] Other (please describe): Update `CLAUDE.md`

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
