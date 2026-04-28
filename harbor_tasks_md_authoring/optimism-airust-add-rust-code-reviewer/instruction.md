# ai(rust): add rust code reviewer to claude skills

Source: [ethereum-optimism/optimism#20318](https://github.com/ethereum-optimism/optimism/pull/20318)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/agents/rust-code-reviewer.md`

## What to add / change

## Description

Adds a `rust-code-reviewer` to claude skills on the monorepo

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
