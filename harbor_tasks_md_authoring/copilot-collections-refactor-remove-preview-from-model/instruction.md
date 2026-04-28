# refactor: remove "(Preview)" from model name in prompt files for consistency

Source: [TheSoftwareHouse/copilot-collections#1](https://github.com/TheSoftwareHouse/copilot-collections/pull/1)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/prompts/implement-ui.prompt.md`
- `.github/prompts/implement.prompt.md`
- `.github/prompts/plan.prompt.md`
- `.github/prompts/research.prompt.md`
- `.github/prompts/review-ui.prompt.md`
- `.github/prompts/review.prompt.md`

## What to add / change

See the PR for the intended changes to the listed file(s).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
