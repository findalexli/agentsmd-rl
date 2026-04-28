# feat(skills): opencode skill + fix: doctor cronjob availability

Source: [NousResearch/hermes-agent#1174](https://github.com/NousResearch/hermes-agent/pull/1174)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/autonomous-ai-agents/opencode/SKILL.md`

## What to add / change

## Changes

### 1. feat(skills): add bundled opencode autonomous-agent skill
Cherry-picked from PR #880 by @arceus77-7, enhanced with hands-on testing.

Adds `opencode` skill under `skills/autonomous-ai-agents/` with:
- One-shot `opencode run` and interactive TUI workflows
- PR review (including `opencode pr` command)
- Parallel work, session/cost management
- TUI keybindings, proper exit instructions
- Fixed `/exit` bug from original PR (not a valid command)

### 2. fix: report cronjob tool as available in hermes doctor
Cherry-picked from PR #895 by @stablegenius49, rebased with conflict resolution.

Sets `HERMES_INTERACTIVE=1` via `setdefault` in `run_doctor()` so CLI-gated tool checks (like cronjob) see the same context as the interactive CLI.

Fixes #878

### Testing
- OpenCode v1.2.25: smoke test passed, `--model` flag verified, interactive TUI tested
- Doctor tests: 8/8 passed (7 existing + 1 new regression test)
- Skills hub tests: 43/43 passed

Co-authored-by: arceus77-7 <261276524+arceus77-7@users.noreply.github.com>
Co-authored-by: stablegenius49 <stablegenius49@users.noreply.github.com>

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
