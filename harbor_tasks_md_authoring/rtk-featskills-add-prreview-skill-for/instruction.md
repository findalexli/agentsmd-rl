# feat(skills): add /pr-review skill for batch PR review

Source: [rtk-ai/rtk#924](https://github.com/rtk-ai/rtk/pull/924)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/pr-review/SKILL.md`
- `CLAUDE.md`

## What to add / change

## What this adds

A new Claude Code skill `/pr-review` that automates the systematic batch review workflow for RTK pull requests, ordered by complexity (XS → S → M → L).

## How it works

For each PR, the skill:
- Checks mergeable state, CLA status, and existing reviews **before** reading the diff
- Reads the full diff and source context for non-trivial logic changes
- Presents a structured summary: link, size badge, CLA status, analysis, recommendation
- **Waits for explicit approval before any merge** — no silent auto-merging
- Posts boldguy-adapt comments on blocked PRs (conflict, unsigned CLA, CHANGES_REQUESTED) with context-appropriate templates

## Usage

```
/pr-review              # build list from open PRs, review XS first
/pr-review triage       # run /rtk-triage first, then review quick wins
/pr-review from:884     # resume from a specific PR number
```

## Also fixes

Removes a broken pre-push check in `validate-docs.sh` that compared `^mod ` count in `main.rs` (8 top-level modules) against "Total: 64 modules" in `ARCHITECTURE.md`. These are different metrics that can never match, so the check was blocking all branches unconditionally.

Also adds the missing ecosystems line to `CLAUDE.md` so the Python/Go commands check passes on develop-based branches.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
