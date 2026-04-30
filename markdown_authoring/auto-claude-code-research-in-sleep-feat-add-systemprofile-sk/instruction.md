# feat: add system-profile skill

Source: [wanshuiyin/Auto-claude-code-research-in-sleep#76](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep/pull/76)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/system-profile/SKILL.md`

## What to add / change

## Summary
- Add new `system-profile` skill for performance profiling targets (scripts, processes, GPU, memory, interconnect)
- Supports both external profiling tools (cProfile, py-spy, nvidia-smi, etc.) and code instrumentation
- Produces structured reports with CPU/memory/interconnect/GPU tables and actionable recommendations
- Includes mandatory instrumentation changelog for easy cleanup

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
