# Create an `AGENTS.md` file

Source: [WordPress/secure-custom-fields#213](https://github.com/WordPress/secure-custom-fields/pull/213)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## What?
This PR adds an `AGENTS.md` file with instructions to help AI agents work with this repository.

<!-- In a few words, what is the PR actually doing? -->

## Why?
AI agents are becoming increasingly popular as a supporting development tool. Rather than ignoring this fact, providing guidelines for AI agents will help them be more effective, resulting in a better and faster developer experience with reduced cost and environmental impact.

## How?
By following the [AGENTS.md](https://agents.md/) format supported by many agents. It's not a formal spec, but a de facto standard, which focuses on:
> - Give agents a clear, predictable place for instructions.
> - Keep READMEs concise and focused on human contributors.
> - Provide precise, agent-focused guidance that complements existing README and docs.

This first iteration includes dev environment tips, testing instructions, and PR instructions.

## Testing Instructions
1. Run your favorite AI agent and ask it to lint or run tests, which is something they usually don't get right on the first try

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
