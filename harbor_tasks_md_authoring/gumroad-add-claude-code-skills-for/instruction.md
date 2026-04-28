# Add Claude Code skills for contributors

Source: [antiwork/gumroad#3546](https://github.com/antiwork/gumroad/pull/3546)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/commit/SKILL.md`
- `.claude/skills/create-issue/SKILL.md`
- `.claude/skills/pr-description/SKILL.md`
- `.claude/skills/pr-description/references/example.md`
- `.claude/skills/review-pr/SKILL.md`
- `.claude/skills/review-pr/references/review-guidance.md`

## What to add / change

## Problem

Contributors (and the team) repeatedly do the same workflows – writing commit messages, drafting PR descriptions, reviewing PRs, filing issues – without consistent structure or conventions. There's no shared tooling to encode CONTRIBUTING.md standards into the development loop.

## Approach

Added 4 Claude Code skills to `.claude/skills/` so anyone who clones the repo gets them automatically:

- **commit**: stages and commits following the project's message conventions
- **pr-description**: generates PR descriptions from branch diff and linked issue, with a style reference from a well-received PR
- **review-pr**: reviews PRs against CONTRIBUTING.md with 4 passes (bugs, guidelines, clarity, structure), filters noise via confidence scoring
- **create-issue**: drafts issues with What/Why/Proposed solution structure, suggests parent + sub-issues when scope is large

These are the subset of our internal skills that don't require private infrastructure.

---

This PR was implemented with AI assistance using Claude Code for code generation. All code was self-reviewed.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
