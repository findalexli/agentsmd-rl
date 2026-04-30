# docs: enforce code signoff in AGENTS.md

Source: [jaegertracing/helm-charts#706](https://github.com/jaegertracing/helm-charts/pull/706)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Please verify that the DCO signoff requirement is clear and correctly placed in AGENTS.md.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
