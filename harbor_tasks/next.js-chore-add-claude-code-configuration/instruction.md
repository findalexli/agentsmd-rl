# chore: add Claude Code configuration

## Problem

The Next.js repository lacks Claude Code configuration files to help AI assistants understand the project's development workflow, build commands, testing procedures, and CI failure analysis patterns. Without these configuration files, AI assistants may provide incorrect guidance or use outdated/incorrect commands when helping with development tasks.

## Expected Behavior

Create Claude Code configuration files with the following exact content:

### CLAUDE.md (root directory)

Create `CLAUDE.md` at repository root with these exact sections:

**Header and sections:**
- Header: `# Next.js Development Guide`
- `## Git Workflow` section documenting Graphite (`gt`) commands including:
  - `gt create <branch-name> -m "message"`
  - `gt submit --no-edit` (use `--no-edit` flag to avoid interactive prompts)
  - `gt checkout <branch>`
  - `gt modify -a --no-edit`
- `## Build Commands` section
- `## Testing` section documenting these exact commands:
  - `pnpm test-dev-turbo`
  - `pnpm test-start-turbo`
  - `pnpm test-unit`

**Graphite safety rules section:**
Create a section containing this exact text:
- Section header: `Graphite Stack Safety Rules`
- `Never use \`git stash\` with Graphite` (as a warning/best practice)
- References to `gt checkout` and `gt modify` commands

### .claude/commands/ci-failures.md

Create `.claude/commands/ci-failures.md` with:
- Header: `# Check CI Failures`
- Use `gh api` command for fetching CI logs
- Include `in_progress` handling for runs
- Reference `subagent` or `Parallel subagent` for parallel analysis

### .gitignore (append entries)

Add these exact entries to `.gitignore`:
```
# Claude Code (local settings and session files)
.claude/settings.local.json
.claude/plans/
.claude/todos.json
CLAUDE.local.md
```

### .alexignore (append entries)

Add these exact entries to `.alexignore`:
```
.claude/
CLAUDE.md
```

## File Locations

- `CLAUDE.md` — root directory, Next.js development guide
- `.claude/commands/ci-failures.md` — CI failure analysis command
- `.gitignore` — append Claude Code ignores to existing file
- `.alexignore` — append Claude Code ignores to existing file

## Reference

Based on PR #87943 which adds Claude Code configuration to help AI assistants work effectively with the Next.js codebase. The configuration should follow Graphite-based git workflow patterns and pnpm-based build system conventions.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
