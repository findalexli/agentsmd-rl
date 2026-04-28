# Add AGENTS.md with instructions for agents working in this repo

Source: [kubernetes/org#5912](https://github.com/kubernetes/org/pull/5912)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Based on our conventions, this adds an AGENT.md file to this repo. This could be used with a tool like GitHub Copilot to potentially automate some stuff.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
