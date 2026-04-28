# Add AGENTS.md project guide

Source: [git-ai-project/git-ai#511](https://github.com/git-ai-project/git-ai/pull/511)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary

- Adds an `AGENTS.md` file providing a comprehensive project guide for AI coding agents
- Covers build/test commands, architecture overview (binary dispatch, data flow, hook system), test infrastructure, key conventions, and common gotchas
- Documents the checkpoint → working log → authorship note pipeline, git proxy hook architecture, config system, and cross-platform considerations

## Test plan

- [ ] Verify `AGENTS.md` renders correctly on GitHub
- [ ] Confirm no existing files were modified

🤖 Generated with [Claude Code](https://claude.com/claude-code)
<!-- devin-review-badge-begin -->

---

<a href="https://app.devin.ai/review/git-ai-project/git-ai/pull/511" target="_blank">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://static.devin.ai/assets/gh-open-in-devin-review-dark.svg?v=1">
    <img src="https://static.devin.ai/assets/gh-open-in-devin-review-light.svg?v=1" alt="Open with Devin">
  </picture>
</a>
<!-- devin-review-badge-end -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
