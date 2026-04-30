# move copilot instructions to AGENTS.md

Source: [ggml-org/llama.cpp#18259](https://github.com/ggml-org/llama.cpp/pull/18259)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Also included more instructions about AI usage disclosure as some contributors don't read `CONTRIBUTION.md`

Tighter guidelines like https://github.com/processing/p5.js/blob/main/AGENTS.md can be more desirable, but idk why it doesn't work on claude code or copilot. The AI still make changes (even dangerous and stupid changes, like changes that violate thread safety) when I asked - they definitely never say "no" to users.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
