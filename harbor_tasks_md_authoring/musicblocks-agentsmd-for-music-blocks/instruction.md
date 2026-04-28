# Agents.md for music blocks

Source: [sugarlabs/musicblocks#6575](https://github.com/sugarlabs/musicblocks/pull/6575)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Adds a root-level AGENTS.md tailored for Music Blocks so AI tools used by contributors can work with clearer, repo-specific guidance.

The goal is to improve AI-generated contributions by pushing agents to:
- understand the relevant code path before editing
- fix the underlying cause instead of applying symptom-only patches
- make small, reviewable changes that follow Music Blocks conventions
- request browser testing with clear steps when UI/runtime behavior needs manual verification

i've made this by referring to couple of github repo's. 
Any improvement/addition is much welcome. 


- [x] Documentation

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
