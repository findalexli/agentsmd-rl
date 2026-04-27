# add skill

Source: [Agent-Field/SWE-AF#9](https://github.com/Agent-Field/SWE-AF/pull/9)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `docs/SKILL.md`

## What to add / change

## Summary

A new skill for agents to utilize while working with SWE-AF.

## Notes

Created with GLM-5 based on main. Tested for functionality and it is definitely helpful for setting up the env, starting the service, and triggering builds via the API.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
