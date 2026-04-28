# t1022: Make AGENTS.md tool-agnostic

Source: [marcusquinn/aidevops#1329](https://github.com/marcusquinn/aidevops/pull/1329)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/AGENTS.md`
- `AGENTS.md`

## What to add / change

WIP - incremental commits

Ref #1326

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

* **Documentation**
  * Updated AI tool references throughout configuration documentation to reflect Claude Code as the primary coding assistant.

* **Chores**
  * Updated CLI and configuration references for consistency with current tooling.

<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
