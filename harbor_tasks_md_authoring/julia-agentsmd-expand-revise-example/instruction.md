# AGENTS.md: expand Revise example

Source: [JuliaLang/julia#59746](https://github.com/JuliaLang/julia/pull/59746)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Requires https://github.com/timholy/Revise.jl/pull/959 to actually work (without explicitly calling `revise()` after `track`).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
