# Enhance AGENTS.md with structure, configuration, testing, and review

Source: [seratch/ChatGPT-in-Slack#124](https://github.com/seratch/ChatGPT-in-Slack/pull/124)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

- Expand structure (constants, i18n, Slack manifests)
- Add CI workflow paths and a quick syntax check example
- Clarify file-scoped testing and Commit/PR expectations (ask first)
- Add production-safety guard; keep security practices explicit

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
