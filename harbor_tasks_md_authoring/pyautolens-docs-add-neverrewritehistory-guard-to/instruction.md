# docs: add Never-rewrite-history guard to CLAUDE.md / AGENTS.md

Source: [PyAutoLabs/PyAutoLens#478](https://github.com/PyAutoLabs/PyAutoLens/pull/478)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

## Summary
Append a `## Never rewrite history` section to this repo's `CLAUDE.md` and/or `AGENTS.md` (whichever exist) listing destructive history operations that should never run on a remote-tracked branch, with the canonical clean-working-tree sequence as the only correct alternative.

One of 17 PRs implementing PyAutoLabs/PyAutoPrompt#7 (history-rewrite-guard umbrella).

## Test Plan
- [ ] `grep "## Never rewrite history" CLAUDE.md AGENTS.md` returns the section.
- [ ] Existing content of these files is unchanged above the new section.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
