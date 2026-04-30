# Add dependencies and clarify triggers in bria-ai skill description

Source: [Bria-AI/bria-skill#12](https://github.com/Bria-AI/bria-skill/pull/12)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/bria-ai/SKILL.md`

## What to add / change

- Introduced a list of dependencies including BRIA_API_KEY, Python, and Node.js versions.
- Clarified the description by explicitly stating that triggers are image generation tasks, enhancing user understanding of capabilities.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
