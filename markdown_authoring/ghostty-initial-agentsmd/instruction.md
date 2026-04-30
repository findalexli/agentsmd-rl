# Initial AGENTS.md

Source: [ghostty-org/ghostty#8507](https://github.com/ghostty-org/ghostty/pull/8507)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

I've been using agents a lot more with Ghostty and so are contributors. Ghostty welcomes AI contributions (but they must be disclosed as AI assisted), and this AGENTS.md will help everyone using agents work better with the codebase.

This AGENTS.md has thus far been working for me very successfully, despite being simple. I suspect we'll add to it as time goes on but I also want to avoid making it too large and polluting the context.

**Changes should not be made to `AGENTS.md` unless it demonstrably improves agent behavior.** To demonstrate agent behavior, I'd prefer sharing an amp thread before and after the change with the same prompt and model to show an improvement.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
