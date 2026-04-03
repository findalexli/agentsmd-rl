# Add a /split-file Claude Code skill with verification tooling

## Problem

When splitting large Go files in the Mimir codebase into smaller focused modules, there is no reusable workflow that preserves `git log --follow` history for each new file. Developers have to rediscover the git rename/rename conflict technique each time, and there's no way to mechanically verify that all declarations were moved intact without manual review.

## What's Needed

1. **A Go CLI tool** at `tools/split-file-verify/` that parses Go source files using the AST, extracts every top-level declaration (functions, methods, types, var/const blocks), and outputs a sorted TSV of `name<TAB>sha256_hash`. This tool should:
   - Accept one or more `.go` files as arguments
   - Format method names with their receiver type (e.g., `(Server).Start`)
   - Output sorted by declaration name
   - Print a usage message and exit non-zero if no arguments are provided
   - Use only the first 16 hex characters of the SHA-256 hash

2. **A Claude Code skill** at `.claude/skills/split-file/SKILL.md` that documents the full workflow for splitting a Go file while preserving git history. The skill should cover:
   - An analysis/planning phase
   - The git rename/rename merge-conflict technique for history preservation
   - Content extraction and cleanup
   - Known gotchas (especially around `goimports` alias resolution)
   - A verification phase that uses the CLI tool above

The skill needs proper YAML frontmatter (`name`, `description`, `argument-hint` fields) and should reference the verify tool in its verification section.

## Files to Look At

- `tools/` — existing tool directory structure for reference
- `.claude/` — this directory may need to be created for the skill
- `pkg/CLAUDE.md` — Go coding conventions (import style, comment format)
