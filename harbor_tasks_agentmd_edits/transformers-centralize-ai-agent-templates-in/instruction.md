# Centralize AI agent configuration into `.ai/` directory

## Problem

The repository's AI agent configuration files (`AGENTS.md`, `CLAUDE.md`) currently live at the repo root as standalone files. `CLAUDE.md` contains only `@AGENTS.md` (a reference directive), and there is no central place for agent skills. This scattered layout makes it hard to manage agent-specific assets across different tools (Claude Code, OpenAI Codex, Cursor) and doesn't scale as more skills are added.

## What needs to happen

1. **Create a `.ai/` directory** as the single source of truth for all agent configuration:
   - Move `AGENTS.md` content into `.ai/AGENTS.md`, adding a section that explains how local agents should set themselves up (running make targets to wire tool-specific assets).
   - Create a skills subdirectory `.ai/skills/` with at least one skill — a type-checking skill (`add-or-fix-type-checking`) that documents the workflow for fixing `ty` type-checker errors using the project's conventions.

2. **Replace root config files with symlinks** so that tools expecting `AGENTS.md` or `CLAUDE.md` at the root still find valid content:
   - `AGENTS.md` → `.ai/AGENTS.md`
   - `CLAUDE.md` → `.ai/AGENTS.md`

3. **Add Makefile targets** for local agent setup:
   - `make claude` — creates `.claude/skills` as a symlink to `.ai/skills`
   - `make codex` — creates `.agents/skills` as a symlink to `.ai/skills`
   - `make clean-ai` — removes the generated symlinks
   - Register these as `.PHONY` targets.

4. **Update supporting files**:
   - Add `.agents/skills` and `.claude/skills` to `.gitignore` (they're generated, not committed).
   - Add a section to `CONTRIBUTING.md` explaining the AI agent setup workflow.

## Files to look at

- `AGENTS.md` — current agent guidance (will become a symlink)
- `CLAUDE.md` — current Claude config (will become a symlink)
- `Makefile` — needs new targets
- `CONTRIBUTING.md` — needs new section
- `.gitignore` — needs new exclusions
