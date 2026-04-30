# docs: Add launchd/cron naming convention to AGENTS.md

Source: [marcusquinn/aidevops#2319](https://github.com/marcusquinn/aidevops/pull/2319)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/AGENTS.md`

## What to add / change

## Summary

- Adds `sh.aidevops.*` naming convention for launchd plists and cron jobs
- Ensures all scheduled tasks are discoverable in System Settings > Login Items & Extensions
- Any main agent can create routines, so this convention belongs in the shared AGENTS.md

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
