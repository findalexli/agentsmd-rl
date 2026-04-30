# Build: Improve docs guidance in AGENTS.md

Source: [MudBlazor/MudBlazor#13116](https://github.com/MudBlazor/MudBlazor/pull/13116)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Updates the docs authoring guidance for component pages and examples. The new section consolidates existing docs rules with clearer expectations for page structure, example naming, realistic sample content, visible code, accessibility notes, and generated docs test constraints.

**Checklist:**
<!-- If you're unsure about any of these, don't hesitate to ask. We're here to help! -->
- [x] I've read the [contribution guidelines](CONTRIBUTING.md)
- [x] My code follows the style of this project
- [x] I've added or updated relevant unit tests

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
