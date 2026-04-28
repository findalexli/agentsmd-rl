# docs(skills): add Claude Code compatible guides and update README

Source: [Eventual-Inc/Daft#6116](https://github.com/Eventual-Inc/Daft/pull/6116)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/daft-distributed-scaling/SKILL.md`
- `.claude/skills/daft-docs-navigation/SKILL.md`
- `.claude/skills/daft-udf-tuning/SKILL.md`

## What to add / change

This PR introduces a new `.claude/skills` directory containing Claude Code-compatible skill definitions. These guides are designed to help AI coding assistants better understand Daft's distributed architecture and API patterns.

### Included Skills:
- **`distributed-scaling`**: Recipes for converting single-node workflows to distributed Ray execution.
  - *New*: Includes the "ByteDance Formula" for calculating optimal partition counts and batch sizes to maximize cluster utilization.
- **`udf-tuning`**: Overview and tuning advice for legacy `@daft.udf` and new `@daft.func` / `@daft.cls` APIs, focusing on resource management (CPU/GPU) and concurrency.
- **`docs-navigation`**: Tips for navigating Daft documentation (both `docs.daft.ai` and the local `docs/` tree) effectively.

### Changes:
- Added `.claude/skills/distributed-scaling/SKILL.md`
- Added `.claude/skills/udf-tuning/SKILL.md`
- Added `.claude/skills/docs-navigation/SKILL.md`
- Updated `README.rst` with instructions on how to use these skills with Claude Code.

These skills favor concise, actionable examples and include direct references to the official Daft documentation.

## Changes Made

<!-- Describe what changes were made and why. Include implementation details if necessary. -->

## Related Issues

<!-- Link to related GitHub issues, e.g., "Closes #123" -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
