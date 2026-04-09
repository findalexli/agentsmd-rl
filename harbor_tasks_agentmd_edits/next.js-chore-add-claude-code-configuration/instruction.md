# chore: add Claude Code configuration

## Problem

The Next.js repository lacks Claude Code configuration files to help AI assistants understand the project's development workflow, build commands, testing procedures, and CI failure analysis patterns. Without these configuration files, AI assistants may provide incorrect guidance or use outdated/incorrect commands when helping with development tasks.

## Expected Behavior

Create the Claude Code configuration files that document:
1. Graphite-based git workflow (not raw git commands)
2. Build commands (pnpm-based)
3. Testing commands and fast iteration workflows
4. CI failure analysis instructions
5. Git ignore rules for Claude Code local files

## Files to Look At

- `CLAUDE.md` — needs to be created at repository root with development guide
- `.claude/commands/ci-failures.md` — needs to be created with CI analysis instructions
- `.gitignore` — needs to ignore Claude Code local settings
- `.alexignore` — needs to ignore `.claude/` directory and `CLAUDE.md`

## Reference

Based on PR #87943 which adds Claude Code configuration to help AI assistants work effectively with the Next.js codebase.

Key requirements:
- Use Graphite (`gt` commands) instead of raw git commands
- Document pnpm-based build system
- Include fast local development workflow with watch mode
- Document testing commands (pnpm test-dev-turbo, test-start-turbo, etc.)
- Add CI failure analysis command with parallel subagent log analysis
- Ignore local Claude Code files in .gitignore
- Ignore .claude/ and CLAUDE.md from alex linting
