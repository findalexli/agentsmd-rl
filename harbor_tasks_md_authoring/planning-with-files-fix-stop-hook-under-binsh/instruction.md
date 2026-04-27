# Fix Stop hook under /bin/sh (dash)

Source: [OthmanAdi/planning-with-files#57](https://github.com/OthmanAdi/planning-with-files/pull/57)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.codex/skills/planning-with-files/SKILL.md`
- `.cursor/skills/planning-with-files/SKILL.md`
- `.kilocode/skills/planning-with-files/SKILL.md`
- `.opencode/skills/planning-with-files/SKILL.md`
- `skills/planning-with-files/SKILL.md`

## What to add / change

# Fix: POSIX sh Compatibility for Claude Code Stop Hook (Debian/Ubuntu)
## Summary
On Debian/Ubuntu, Claude Code runs hooks via `/bin/sh` (often `dash`). The Stop hook command in several SKILL.md variants used bash-only syntax (`[[ ... ]]` and `&>`), causing the following errors:
- `/bin/sh: 1: [[: not found`
- `/bin/sh: 1: : Permission denied`

This PR rewrites the Stop hook command to be POSIX `sh` compatible while retaining the original behavior: use PowerShell on Windows when available; otherwise run `check-complete.sh`.

## Changes
- Replace bashisms (`[[` / `&>`) with POSIX constructs (`[` / `case` / `>/dev/null 2>&1`)
- Use `uname -s` + `OS=Windows_NT` for shell-agnostic Windows detection
- Run `check-complete.sh` via `sh` (no assumptions about executable bit/shebang)

## Affected Files
- `skills/planning-with-files/SKILL.md`
- `.codex/skills/planning-with-files/SKILL.md`
- `.cursor/skills/planning-with-files/SKILL.md`
- `.kilocode/skills/planning-with-files/SKILL.md`
- `.opencode/skills/planning-with-files/SKILL.md`

## Repro / Test
- Verified the updated Stop hook snippet runs under `/bin/sh` (dash) without errors:
  `CLAUDE_PLUGIN_ROOT=/tmp/planning-with-files /bin/sh -c '<stop hook snippet>'`

## Context
Addresses the dash/`/bin/sh` Stop hook failure described by @aqlkzf in #32.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
