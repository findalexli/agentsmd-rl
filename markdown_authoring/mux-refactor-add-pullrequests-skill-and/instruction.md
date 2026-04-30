# 🤖 refactor: add pull-requests skill and migrate PR docs from AGENTS.md

Source: [coder/mux#1826](https://github.com/coder/mux/pull/1826)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.mux/skills/pull-requests/SKILL.md`
- `docs/AGENTS.md`

## What to add / change

Adds a new `pull-requests` agent skill and migrates PR-related documentation from AGENTS.md into it.

## Changes

- **New skill:** `.mux/skills/pull-requests/SKILL.md`
  - Attribution footer requirements (🤖 emoji, mux cost/model footer)
  - PR lifecycle rules (reuse PRs, force-push, no auto-merge)
  - CI validation workflow (`wait_pr_checks.sh`)
  - Status decoding table (`mergeable`, `mergeStateStatus`)
  - Codex review workflow (heredoc pattern)
  - Title conventions and description guidelines

- **Updated:** `docs/AGENTS.md`
  - Replaced ~40 lines of PR docs with a single skill reference
  - Keeps AGENTS.md focused on codebase patterns, delegates PR workflow to skill

The skill is now discoverable via `agent_skill_read({ name: "pull-requests" })`.

---

_Generated with `mux` • Model: `anthropic:claude-opus-4-5` • Thinking: `high` • Cost: `$0.42`_

<!-- mux-attribution: model=anthropic:claude-opus-4-5 thinking=high costs=0.42 -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
