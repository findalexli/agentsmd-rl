# fix(skills): harden plugin root resolution across install modes

Source: [Lum1104/Understand-Anything#95](https://github.com/Lum1104/Understand-Anything/pull/95)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `understand-anything-plugin/skills/understand-dashboard/SKILL.md`
- `understand-anything-plugin/skills/understand/SKILL.md`

## What to add / change

## Summary

This PR improves plugin root resolution robustness for `/understand` and `/understand-dashboard` across different installation modes and hosts.

### What changed

- Prioritize `CLAUDE_PLUGIN_ROOT` as the first plugin-root candidate (runtime-provided root should win)
- Keep existing universal symlink fallback: `~/.understand-anything-plugin`
- Keep self-relative fallback from `~/.agents/skills/...` real path
- Add Copilot personal-skills fallback from `~/.copilot/skills/...` real path
- Add common clone-path fallbacks:
  - `~/.codex/understand-anything/understand-anything-plugin`
  - `~/.opencode/understand-anything/understand-anything-plugin`
  - `~/.pi/understand-anything/understand-anything-plugin`
  - `~/understand-anything/understand-anything-plugin`
- Align root-resolution behavior between `understand` and `understand-dashboard`
- Improve error diagnostics by listing all checked candidates in failure output

## Why

`/understand` could fail with “Cannot find the understand-anything plugin root” in valid installs where:

- `~/.understand-anything-plugin` is absent, and
- `~/.agents/skills/...` is unavailable/unresolvable, while
- a valid runtime root is available (e.g. `CLAUDE_PLUGIN_ROOT`).

This could also cause inconsistent behavior between skills (`/understand` vs `/understand-dashboard`) and potential version mismatch when multiple roots exist.

## Impact

- Fixes root resolution regressions in Claude native setups
- Improves compatibility for Copilot per

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
