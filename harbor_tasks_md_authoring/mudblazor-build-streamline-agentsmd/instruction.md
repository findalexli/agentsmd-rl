# Build: Streamline AGENTS.md

Source: [MudBlazor/MudBlazor#12359](https://github.com/MudBlazor/MudBlazor/pull/12359)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Updated structure and wording in AGENTS.md to be more AI‑focused and less duplicative, while preserving all technical instructions and required workflows.

<!-- Describe your changes and what the purpose of them is. -->
<!-- If you made any visual changes, provide screenshots of before/after. If it has moving parts, please attach a high-quality video. -->

**Checklist:**
<!-- If you're unsure about any of these, don't hesitate to ask. We're here to help! -->
- [x] I've read the [contribution guidelines](CONTRIBUTING.md)
- [x] My code follows the style of this project
- [x] I've added or updated relevant unit tests

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
