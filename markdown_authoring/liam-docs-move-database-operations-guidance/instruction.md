# 📝(docs): Move database operations guidance to package-specific CLAUDE.md

Source: [liam-hq/liam#3568](https://github.com/liam-hq/liam/pull/3568)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`
- `frontend/internal-packages/db/CLAUDE.md`

## What to add / change

## Issue

- resolve: Documentation organization improvement

## Why is this change needed?

Improved organization of documentation by:
1. Moving database operations guidance from main CLAUDE.md to package-specific location
2. Adding "Delete fearlessly, Git remembers" principle to core principles  
3. Fixing code block formatting inconsistencies in CLAUDE.md

This follows the "less is more" principle by keeping the main CLAUDE.md focused on essential project-wide guidance while placing specialized documentation in appropriate package locations.

🤖 Generated with [Claude Code](https://claude.ai/code)

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

* **Documentation**
  * Improved Markdown formatting for command examples and code blocks.
  * Expanded development guidelines with clearer principles to streamline code clarity and cleanup.
  * Updated a code example to clarify required parameters in the Code Editing section.
  * Added a new guidance doc for working with database operations, including references to the migration and type-generation workflow.

* **Chores**
  * Editorial cleanup and consistency adjustments across internal docs.

* **Note**
  * No user-facing functionality changes.

<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
