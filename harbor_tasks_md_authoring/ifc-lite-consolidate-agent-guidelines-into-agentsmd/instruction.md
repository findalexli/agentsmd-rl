# Consolidate agent guidelines into AGENTS.md

Source: [louistrue/ifc-lite#226](https://github.com/louistrue/ifc-lite/pull/226)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursorrules`
- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

## Summary

Consolidates duplicate agent guidelines from `CLAUDE.md` and `.cursorrules` into a single, comprehensive `AGENTS.md` document. This eliminates redundancy and establishes a single source of truth for all AI agent guidelines in the project.

## Changes

- **Created `AGENTS.md`**: New comprehensive guidelines document containing:
  - Project overview and feature list
  - Project structure and file organization
  - License header requirements (TypeScript/JavaScript/CSS and Rust)
  - Critical standards (IFC schema compliance, performance requirements, TypeScript standards)
  - Code style and key patterns
  - On-demand extraction pattern documentation
  - Multi-model federation guidelines
  - Pre-change checklist
  - Testing instructions
  - Common pitfalls and solutions
  - Changesets workflow (required for releases)
  - Commit guidelines
  - Pre-submission checklist

- **Updated `CLAUDE.md`**: Replaced full content with a redirect to `AGENTS.md`
  - Maintains file for backward compatibility
  - Points users to the canonical guidelines document

- **Updated `.cursorrules`**: Replaced full content with a redirect to `AGENTS.md`
  - Maintains file for Cursor IDE compatibility
  - Points users to the canonical guidelines document

## Benefits

- **Single source of truth**: All agent guidelines in one location
- **Easier maintenance**: Updates only need to be made in one place
- **Better organization**: Comprehensive structure with clear sections
- **Backward compatibility

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
