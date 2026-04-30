# Improve vmr-codeflow-status SKILL.md structure

Source: [dotnet/runtime#124150](https://github.com/dotnet/runtime/pull/124150)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/skills/vmr-codeflow-status/SKILL.md`

## What to add / change

Improves the SKILL.md for the vmr-codeflow-status skill based on patterns from the skill-builder methodology:

**Changes:**
- **Critical rules** — No PR approval/blocking (`--approve`/`--request-changes`), no branch switching (`git checkout`/`gh pr checkout`)
- **Expanded trigger description** — Added `flow status`, `missing backflow`, `blocked` keywords that match common user queries
- **Two Modes section** — Decision table clarifying PR analysis vs flow health (`-CheckMissing`) as separate modes
- **Inline anti-pattern** — Warning not to combine `-PRNumber` with `-CheckMissing`
- **Split 'What the Script Does'** — Separated into PR Analysis Mode (8 steps) and Flow Health Mode (4 steps) instead of a mixed 11-item list
- **Inline warnings** — `Unknown` health ≠ healthy, aka.ms 301 vs 302 redirect behavior

No script changes — SKILL.md documentation improvements only.

cc @dotnet/runtime-infrastructure

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
