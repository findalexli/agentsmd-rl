# Improve SKILL.md for AI agent compatibility

Source: [gradio-app/daggr#26](https://github.com/gradio-app/daggr/pull/26)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/daggr/SKILL.md`

## What to add / change

## Summary
- Use `uvx` instead of `uv pip install` for simpler, more reliable execution
- Replace `gradio_client` API discovery with `curl` to OpenAPI endpoint (avoids blocking on sleeping Spaces)
- Add `includeNonRunning=false` filter to Space search URLs to only find running Spaces
- Add Troubleshooting section covering Space timeouts and port conflicts
- Bump version to 1.1

## Test plan
- [x] Verified `uvx daggr --help` works
- [x] Verified Space search with `includeNonRunning=false` returns only running Spaces

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
