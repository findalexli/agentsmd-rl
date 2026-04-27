# docs(agents): tighten code-comment rule to short, why-only

Source: [stablyai/orca#883](https://github.com/stablyai/orca/pull/883)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary
- AI agents were generating wordy multi-paragraph \"Why:\" comments. Updated AGENTS.md §Code Comments to require short (1–2 line) comments that capture only the non-obvious reason — no restating what the code does, narrating mechanism, or verbatim design-doc citations.

## Test plan
- [x] AGENTS.md renders correctly

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
