# docs(skill): add remote / split / android / troubleshooting sections

Source: [BANANASJIM/rdc-cli#213](https://github.com/BANANASJIM/rdc-cli/pull/213)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `src/rdc/_skills/SKILL.md`

## What to add / change

## Summary

- Extend the installed agent skill (`src/rdc/_skills/SKILL.md`) with four new sections after **Shader Edit-Replay**: **Remote Capture Workflow**, **Split Mode (thin client)**, **Android Workflow**, and **Troubleshooting**.
- Expand **Core Workflow** step 1 to list the four \`rdc open\` variants (local / \`--proxy\` / \`--connect --token\` / \`--android\`).
- No code or command behavior changes; \`commands-quick-ref.md\` is already current.

## Why

The current SKILL.md predates Phase 6 / 7 / S / 7D / 7D.1 / 7D.2 shipping. An AI agent reading it could not discover that rdc-cli supports PC-to-PC remote capture, Split thin-client mode, or the Android device workflow at all — the information was only reachable by exhaustively scanning the command reference table.

Context: external issue #212 asks for a "first-class out-of-box" remote workflow on Linux. The capability has shipped; the onboarding surface was missing. This PR closes the skill-layer gap. (UX-layer improvements like \`rdc remote setup HOST\` and progress callbacks are tracked separately.)

## Test plan

- [x] \`pixi run rdc install-skill --check\` → \`Skill files are installed and current.\`
- [x] \`pixi run check\` (ruff + mypy strict + 2780 pytest + 92.51% coverage) green via pre-commit hook
- [x] No changes to \`commands-quick-ref.md\` (auto-generated, already in sync with master)
- [x] Verified the Split-mode output description against \`session.py:281-287\` (the \`host:/port:/token:/connect with:\` f

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
