# [Chore] Add Agents.md to help coding agents

Source: [marmelab/react-admin#11005](https://github.com/marmelab/react-admin/pull/11005)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `Agents.md`

## What to add / change

## Problem

The core team uses Copilot Chat and Copilot Code Reviews. Yet some of the common practices from the core team aren't known to coding agents. 

## Solution

Provide an Agents.md, which is automatically added to the context by coding agents. 

## How To Test

Ask your assistant to add a new feature (e.g. a `createMany` data provider method).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
