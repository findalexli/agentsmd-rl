# Restructure .claude skills into per-skill SKILL.md directories

Source: [tenstorrent/tt-metal#42546](https://github.com/tenstorrent/tt-metal/pull/42546)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `tt_metal/tt-llk/.claude/CLAUDE.md`
- `tt_metal/tt-llk/.claude/skills/arch-lookup/SKILL.md`
- `tt_metal/tt-llk/.claude/skills/debug-kernel/SKILL.md`
- `tt_metal/tt-llk/.claude/skills/port-kernel/SKILL.md`
- `tt_metal/tt-llk/.claude/skills/run-test/SKILL.md`

## What to add / change

### Summary
Convert each Claude Code skill under `tt_metal/tt-llk/.claude/skills/` from a flat `<name>.md` file into a directory containing a `SKILL.md`, so Claude Code's nested-subdirectory skill discovery picks them up automatically when the CLI is launched from inside `tt_metal/tt-llk/`.

### Notes for reviewers
- The skill content itself is unchanged — git reports these as pure renames (`arch-lookup.md` → `arch-lookup/SKILL.md`, and the same for `debug-kernel`, `port-kernel`, `run-test`).
- `tt_metal/tt-llk/.claude/CLAUDE.md` is updated in lockstep:
  - The "Skills & Agents" guidance now says skills live at `.claude/skills/<name>/SKILL.md` and are auto-discovered by the `Skill` tool, with `Read(".claude/skills/<name>/SKILL.md")` as a fallback.
  - The trigger table now lists skills by name (e.g. `arch-lookup`) with the new `SKILL.md` paths.
- Base branch is `nstamatovic/claude-code-team-setup` (not `main`) — this PR stacks onto the in-flight Claude Code team-setup branch.

### CI Status
_Auto-generated on every push. Badges update live. Click a pipeline name or badge to filter by this branch._

| Pipeline | Status | Latest Run |
|---|:---:|---|
| [Sanity tests](https://github.com/tenstorrent/tt-metal/actions/workflows/sanity-tests.yaml?query=branch:njokovic/claude-skills-restructure) | [![](https://github.com/tenstorrent/tt-metal/actions/workflows/sanity-tests.yaml/badge.svg?branch=njokovic/claude-skills-restructure)](https://github.com/tenstorrent/tt-metal/actions/workfl

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
