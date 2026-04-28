# ref: Reorganize AGENTS.md into focused, nested structure

Source: [getsentry/sentry#104690](https://github.com/getsentry/sentry/pull/104690)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `src/AGENTS.md`
- `src/CLAUDE.md`
- `static/AGENTS.md`
- `static/CLAUDE.md`
- `tests/AGENTS.md`
- `tests/CLAUDE.md`

## What to add / change

## Summary

Reorganizes the AGENTS.md documentation to improve maintainability and reduce context overhead for AI agents.

### Changes

- **Trimmed top-level AGENTS.md** from ~1550 lines to ~300 lines (~80% reduction)
- **Created nested AGENTS.md files** for detailed patterns:
  - `src/AGENTS.md` - Backend development patterns (API, Celery, architecture, database)
  - `tests/AGENTS.md` - Python testing patterns and best practices
  - `static/AGENTS.md` - Frontend development patterns (React, design system, testing)
- **Top-level AGENTS.md now focuses on critical information**:
  - Overview and project structure
  - Linting and testing commands
  - Python environment requirements
  - Security guidelines (IDOR prevention)
  - Exception handling rules
- **Added CLAUDE.md files** in each directory that reference their respective AGENTS.md
- **Moved anti-patterns** section from top-level to `src/AGENTS.md`
- **Removed verbose commenting guidelines** from `src/AGENTS.md`

### Rationale

The original AGENTS.md was becoming too large and contained both critical information (security rules, testing commands) and detailed patterns (API examples, design system). This made it harder for AI agents to:
- Quickly find critical information
- Load efficiently due to token limits
- Maintain focus on essential rules

This reorganization ensures agents see critical information immediately while keeping detailed patterns accessible in context-appropriate locations.

### Note

AI agents don't reli

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
