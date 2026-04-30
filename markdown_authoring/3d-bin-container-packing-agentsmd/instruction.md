# Agents.md

Source: [skjolber/3d-bin-container-packing#1136](https://github.com/skjolber/3d-bin-container-packing/pull/1136)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `api/agents.md`
- `core/agents.md`
- `jmh/agents.md`
- `open-api/agents.md`
- `open-api/open-api-client/agents.md`
- `open-api/open-api-model/agents.md`
- `open-api/open-api-server/agents.md`
- `open-api/open-api-test/agents.md`
- `points/agents.md`
- `test/agents.md`
- `visualizer/algorithm/agents.md`
- `visualizer/api/agents.md`
- `visualizer/packaging/agents.md`
- `visualizer/viewer/agents.md`

## What to add / change

See the PR for the intended changes to the listed file(s).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
