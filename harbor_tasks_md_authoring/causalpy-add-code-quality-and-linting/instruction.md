# Add code quality and linting guidelines to `AGENTS.md`

Source: [pymc-labs/CausalPy#572](https://github.com/pymc-labs/CausalPy/pull/572)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Introduces a new section detailing code quality checks, including pre-commit usage, ruff commands for linting and formatting, and notes on linting rules and documentation exclusions.

<!-- readthedocs-preview causalpy start -->
----
📚 Documentation preview 📚: https://causalpy--572.org.readthedocs.build/en/572/

<!-- readthedocs-preview causalpy end -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
