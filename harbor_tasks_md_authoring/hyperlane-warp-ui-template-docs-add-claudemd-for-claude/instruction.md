# docs: add CLAUDE.md for Claude Code guidance

Source: [hyperlane-xyz/hyperlane-warp-ui-template#866](https://github.com/hyperlane-xyz/hyperlane-warp-ui-template/pull/866)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
- Add CLAUDE.md documentation file to help Claude Code instances work effectively with this codebase
- Includes development commands, architecture overview, key directories, data flow, configuration, and testing instructions

## Test plan
- [x] Verify file content is accurate and matches codebase structure
- [x] Ensure all referenced commands work (`pnpm dev`, `pnpm test`, etc.)

🤖 Generated with [Claude Code](https://claude.ai/code)

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

* **Documentation**
  * Added comprehensive developer documentation including setup instructions, configuration guidance, and development workflows for the Hyperlane Warp UI Template.

<sub>✏️ Tip: You can customize this high-level summary in your review settings.</sub>

<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
