# docs(claude): scope Navigator-only rules to interactive sessions

Source: [qf-studio/pilot#2327](https://github.com/qf-studio/pilot/pull/2327)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Problem

Pilot's executor spawns Claude Code against this very repo to implement tickets. When it does, Claude reads `CLAUDE.md` — especially \"❌ DO NOT write code directly in this session\" — and refuses every task with \"violates project workflow.\"

Three issues (GH-2305 / GH-2324 / GH-2325) failed dozens of times before this was diagnosed. The refusal text wasn't in stderr, so Pilot's error classifier reported only `unknown: exit status 1`.

## Fix

Lead `CLAUDE.md` with a **\"Who is reading this file?\"** section that distinguishes:

- **Pilot-executor sessions** — spawned by `pilot start` with a concrete task prompt. In these, Claude **is Pilot** — implement directly. The planning rules DO NOT apply.
- **Interactive dev sessions** — a human planning or reviewing on the Pilot project. In these, follow the Navigator + Pilot pipeline as before.

Detection signals for executor mode (documented in the file):
- Prompt begins with \`GitHub Issue #NNN:\` or \`Task:\`
- No interactive user follow-up
- CWD is inside a pilot worktree or a \`pilot/GH-*\` branch

The \"DO NOT write code / commit / create PRs manually\" bullets are now explicitly scoped to interactive planning sessions. Pilot-executor sessions are called out as the one exception.

## Verification

Reproduced GH-2305 manually with the scoped \`CLAUDE.md\`:
- **Before**: Claude refused with \"Refusing direct implementation — violates project workflow.\"
- **After**: Claude implemented the changes (helper extraction,

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
