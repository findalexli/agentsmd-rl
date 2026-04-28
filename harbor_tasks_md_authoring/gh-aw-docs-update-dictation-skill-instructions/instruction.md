# [docs] Update dictation skill instructions

Source: [github/gh-aw#7964](https://github.com/github/gh-aw/pull/7964)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/dictation/SKILL.md`

## What to add / change

## Summary

Updated the dictation skill instructions (`skills/dictation/SKILL.md`) with a comprehensive glossary of project-specific technical terms extracted from the documentation.

## Changes Made

### Glossary Enhancement
- **Extracted 412 project-specific terms** from `docs/src/content/docs/**/*.md` files
- Organized alphabetically for easy reference
- Focused on user-facing terms (excluded tooling-specific like makefile, Astro, starlight)

### Documentation Sources
Scanned key documentation files including:
- `reference/glossary.md` - Core concepts and definitions
- `reference/frontmatter.md` - Configuration options
- `reference/tools.md` - Tool configurations
- `reference/engines.md` - AI engine options
- `reference/safe-outputs.md` - Safe output types
- `reference/network.md` - Network permissions
- `reference/safe-inputs.md` - Custom tool definitions
- `setup/cli.md` - CLI commands
- `reference/triggers.md` - Workflow triggers

### Speech-to-Text Error Corrections
- Comprehensive mapping table for common misrecognitions
- Spacing and hyphenation rules for compound terms
- Preservation guidelines for YAML-specific syntax (underscores vs hyphens)
- Context-aware corrections (e.g., "pull request" vs "pull-request" vs "pull_request")

### Frontmatter Updates
- Enhanced `name` field: "Dictation Instructions" (more descriptive)
- Improved `description` field with project context
- Added "Technical Context" section explaining gh-aw

### Focus Guidelines
- Clear instruction 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
