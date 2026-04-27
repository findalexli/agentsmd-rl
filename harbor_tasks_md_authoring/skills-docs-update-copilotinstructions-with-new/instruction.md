# docs: update copilot-instructions with new skill naming convention

Source: [microsoft/skills#31](https://github.com/microsoft/skills/pull/31)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

## Summary

Follow-up to #28 - updates `.github/copilot-instructions.md` to align with the new flat skill structure.

## Changes

- **Repository Structure**: Now shows full layout including `AGENTS.md`, `CATALOG.md`, `output/`, backward-compat symlinks, and `.vscode/mcp.json`
- **Skill Naming Convention**: Added new section explaining language suffixes (`-py`, `-dotnet`, `-ts`, `-java`)
- **Featured Skills**: Updated all 17 skill names to new format (e.g., `azure-ai-search-py`, `cosmos-db-py`, `agent-framework-py`)
- **Creating New Skills**: Added naming convention guidance with examples

## Consistency

Both `AGENTS.md` and `.github/copilot-instructions.md` now reference the same skill naming convention and repository structure.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
