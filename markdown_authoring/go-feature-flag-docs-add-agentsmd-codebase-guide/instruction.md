# docs: Add AGENTS.md codebase guide

Source: [thomaspoignant/go-feature-flag#4459](https://github.com/thomaspoignant/go-feature-flag/pull/4459)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

This PR adds an AGENTS.md file to help AI agents and developers understand the GO Feature Flag codebase structure, architecture, and development workflow.

## Changes
- Created comprehensive AGENTS.md guide (condensed to under 300 lines)
- Documents project architecture, directory structure, and key concepts
- Includes development workflow, testing patterns, and code patterns
- Documents logging patterns (slog for Go module, Echo+Zap for relay proxy)
- Documents module structure (modules/core and modules/evaluation)
- Includes PR template policy
- Provides quick reference for common tasks

## Key Sections
- Project overview and architecture
- Directory structure and key components
- Common tasks (adding retrievers/exporters/notifiers)
- Testing patterns (table-driven tests)
- Development workflow (Makefile commands)
- Code patterns and logging patterns
- Module details and OpenFeature provider information

The file follows the PR template requirements and provides essential information in a condensed format.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
