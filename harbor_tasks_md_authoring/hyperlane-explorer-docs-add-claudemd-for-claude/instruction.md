# docs: add CLAUDE.md for Claude Code guidance

Source: [hyperlane-xyz/hyperlane-explorer#244](https://github.com/hyperlane-xyz/hyperlane-explorer/pull/244)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
- Add CLAUDE.md documentation file to help Claude Code instances work effectively with this codebase
- Includes development commands, architecture overview, state management patterns, and code style guidelines

## Test plan
- [x] Verify CLAUDE.md content is accurate and helpful
- [x] File follows the standard CLAUDE.md format

🤖 Generated with [Claude Code](https://claude.com/claude-code)

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

* **Documentation**
  * Added comprehensive developer guidance documentation including project overview, development commands, state management and data fetching architecture, blockchain integration details, URL state handling, dependencies, environment configuration, and code style conventions.

<sub>✏️ Tip: You can customize this high-level summary in your review settings.</sub>

<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
