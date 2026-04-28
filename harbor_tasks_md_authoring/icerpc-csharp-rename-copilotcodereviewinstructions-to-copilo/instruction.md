# Rename copilot-code-review-instructions to copilot-instructions

Source: [icerpc/icerpc-csharp#4344](https://github.com/icerpc/icerpc-csharp/pull/4344)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

See https://docs.github.com/en/copilot/how-tos/use-copilot-agents/request-a-code-review/use-code-review

> Repository custom instructions can either be repository wide or path specific. You specify repository-wide custom instructions in a .github/copilot-instructions.md file in your repository. You can use this file to store information that you want Copilot to consider when reviewing code anywhere in the repository.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
