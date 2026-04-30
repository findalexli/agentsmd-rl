# docs: update SKILL.md for new CLI commands

Source: [HuangYuChuh/ComfyUI_Skills_OpenClaw#124](https://github.com/HuangYuChuh/ComfyUI_Skills_OpenClaw/pull/124)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `SKILL.md`

## What to add / change

## Summary
- Add Quick Decision routes for new user intents: inpainting, job status, server stats, node discovery, dry run/validate
- Add Command Reference entries for new core commands: `server stats`, `run --validate`, `upload --mask`, `nodes list`, `jobs list`
- Remove parameter-level details (`--priority`, `--only`, `models`, `templates`, `logs`) per three-layer documentation strategy — these are discoverable via `--help`
- Fix Workflow Import section: remove `--check-deps` flag detail, replace with behavior guidance

## Design Philosophy Compliance
All changes follow the [CONTRIBUTING.md](./CONTRIBUTING.md) three-layer documentation strategy:
- **Layer 2 (SKILL.md)**: Only WHEN/WHY routing and special agent behavior
- **Layer 3 (`--help`)**: Command syntax and parameter details
- **Growth**: Logarithmic, not linear — standard CRUD commands stay in `--help`

## Test plan
- [ ] Verify all Quick Decision entries follow "User says X → command Y" format
- [ ] Verify all Command Reference entries are referenced by Quick Decision or Execution Flow
- [ ] Verify no parameter-level details leak into SKILL.md body

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
