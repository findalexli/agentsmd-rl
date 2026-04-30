# docs: add agents.md (closes #45)

Source: [Azure-Samples/azure-openai-rag-workshop#47](https://github.com/Azure-Samples/azure-openai-rag-workshop/pull/47)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/prompts/create-agents.md.prompt.md`
- `AGENTS.md`
- `src/backend/AGENTS.md`
- `src/frontend/AGENTS.md`
- `src/ingestion/AGENTS.md`
- `trainer/AGENTS.md`

## What to add / change

See the PR for the intended changes to the listed file(s).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
