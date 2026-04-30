# docs: update CLAUDE.md to reflect current project structure

Source: [nyatinte/ccexp#33](https://github.com/nyatinte/ccexp/pull/33)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Overview

Update CLAUDE.md to accurately reflect the current project structure. The documentation had become outdated, making it difficult for contributors to understand the codebase, especially the sophisticated testing strategy using fs-fixture.

## AS-IS

- MenuActions shown as a single file
- Missing files: FileGroup, LoadingScreen, test helpers
- Basic testing philosophy without implementation details
- No scanner hierarchy documentation

## TO-BE

- MenuActions as a modular directory structure
- All files documented with their purposes
- Comprehensive testing strategy with fs-fixture and dependency injection
- Scanner hierarchy with BaseFileScanner pattern
- File grouping UI and release commands documented

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

* **Documentation**
  * Expanded documentation with new release management commands, detailed testing strategies, and CI/CD pipeline integration.
  * Updated architectural overview to reflect a modular scanner hierarchy, data flow, and simplified type system.
  * Enhanced user experience section with file grouping by type and keyboard navigation details.
  * Added Git hooks integration and quality pipeline information.

* **New Features**
  * Introduced modular scanner hierarchy with base and specialized scanners and exclusion patterns.
  * Added new UI components for file action menus, error boundaries, and loading screens.

* **Tests**
  * Added comprehensive tes

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
