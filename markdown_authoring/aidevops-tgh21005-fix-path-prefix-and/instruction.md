# tGH#21005: fix path prefix and section ref clarity in .agents/AGENTS.md

Source: [marcusquinn/aidevops#21009](https://github.com/marcusquinn/aidevops/pull/21009)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/AGENTS.md`

## What to add / change

## Summary

Fixes two review findings from PR #20982 on `.agents/AGENTS.md`:

1. **HIGH (line 46)**: Added missing `.agents/` prefix to the `workflows/pre-edit.md` path reference — paths in this file resolve from repo root, so it should be `.agents/workflows/pre-edit.md`.
2. **MEDIUM (line 347)**: Clarified the ambiguous `see "Git Workflow" section below` reference (which was inside a `### Git Workflow` subsection) to `see the "## Git Workflow" section below` — making the target heading level explicit.

## Verification

Both changes are documentation-only (no shell or code changes). Confirmed correct paths:
- `git ls-files .agents/workflows/pre-edit.md` → file exists
- Section `## Git Workflow` exists at line ~561 in the same file

Resolves #21005


<!-- aidevops:sig -->
---
[aidevops.sh](https://aidevops.sh) v3.11.7 plugin for [OpenCode](https://opencode.ai) v1.14.24 with claude-sonnet-4-6 spent 46s and 1,783 tokens on this as a headless worker.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
