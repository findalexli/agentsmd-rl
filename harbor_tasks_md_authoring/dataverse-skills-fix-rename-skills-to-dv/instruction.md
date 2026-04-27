# fix: rename skills to dv-* prefix for scannability

Source: [microsoft/Dataverse-skills#28](https://github.com/microsoft/Dataverse-skills/pull/28)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/plugins/dataverse/skills/dv-init/SKILL.md`
- `.github/plugins/dataverse/skills/dv-mcp-configure/SKILL.md`
- `.github/plugins/dataverse/skills/dv-metadata/SKILL.md`
- `.github/plugins/dataverse/skills/dv-overview/SKILL.md`
- `.github/plugins/dataverse/skills/dv-python-sdk/SKILL.md`
- `.github/plugins/dataverse/skills/dv-setup/SKILL.md`
- `.github/plugins/dataverse/skills/dv-solution/SKILL.md`

## What to add / change

## Problem

The plugin name is `dataverse`, and each SKILL.md had `name: dataverse-*` (e.g., `name: dataverse-init` in the `init/` folder). This caused issues across all three surfaces where skill names appear:

**GitHub Copilot invocation** — Copilot uses the `name:` field from SKILL.md for display. This produced redundant names: `dataverse:dataverse-init`, `dataverse:dataverse-mcp-configure`, etc.

**Claude Code invocation** — Claude uses the **folder name** (not the `name:` field) for display, so it showed `/dataverse:init` — no redundancy, but having `name: dataverse-init` in folder `init/` violated the [Agent Skills spec](https://agentskills.io/specification) which requires the name to match the folder.

**Skill list views** (both tools) — When listing installed skills, the namespace isn't always shown. Bare names like `init` and `setup` are too generic to scan — they could belong to any plugin.

### How each tool resolves skill names

| | Claude Code | GitHub Copilot |
|---|---|---|
| **Namespace source** | `plugin.json` `name` | Plugin name |
| **Skill name source** | Folder name | `name:` field in SKILL.md |
| **Before** | `/dataverse:init` | `dataverse:dataverse-init` |
| **After (bare)** | `/dataverse:init` | `dataverse:init` |
| **After (dv-)** | `/dataverse:dv-init` | `dataverse:dv-init` |
| **In skill list** | `dv-init` (scannable) | `dv-init` (scannable) |

## Solution: `dv-` prefix

We chose `dv-` over bare names or full `dataverse-` pref

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
