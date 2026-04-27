# docs: Expand CLAUDE.md with comprehensive architecture and development guide

Source: [CherryHQ/cherry-studio#13241](https://github.com/CherryHQ/cherry-studio/pull/13241)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

### What this PR does

Before this PR:
- CLAUDE.md contained minimal guidance on development commands and project structure
- Lacked detailed information about architecture, services, database layers, and conventions
- Missing documentation on contribution restrictions and tech stack details

After this PR:
- Comprehensive architecture documentation covering Electron structure, main/renderer processes, and packages
- Detailed service registry for main process (WindowService, MCPService, KnowledgeService, etc.)
- Complete Redux store slice documentation with state shape reference
- Database layer documentation (IndexedDB + SQLite/Drizzle)
- IPC communication patterns and tracing setup
- AI Core package architecture and provider abstraction details
- Multi-window architecture overview
- Tech stack matrix with all key dependencies
- Code style conventions, file naming, i18n guidelines
- Testing guidelines and v2 refactoring blockers
- Security best practices

### Why we need it and why it was done in this way

This documentation update serves as a comprehensive reference for AI coding assistants and contributors working on the Cherry Studio codebase. The expanded guide:

1. **Reduces onboarding friction** - New contributors and AI assistants can understand the full architecture without diving into source code
2. **Clarifies contribution restrictions** - Explicitly documents the v2.0.0 refactoring blockers to prevent rejected PRs
3. **Standardizes conventions** - Provides clear g

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
