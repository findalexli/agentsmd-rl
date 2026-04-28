# Update CLAUDE.md documentation

Source: [SukramJ/homematicip_local#963](https://github.com/SukramJ/homematicip_local/pull/963)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

- Update project version from 1.91.0 to 2.0.0
- Update aiohomematic from 2025.12.1 to 2025.12.17
- Update aiohomematic-test-support from 2025.12.1 to 2025.12.17
- Update pytest-homeassistant-custom-component from 0.13.297 to 0.13.300
- Update pylint from 4.0.3 to 4.0.4
- Update ruff from 0.14.5 to 0.14.8
- Update config entry migration version from 10 to 12
- Update minimum HA version from 2025.8.0 to 2025.10.0

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
