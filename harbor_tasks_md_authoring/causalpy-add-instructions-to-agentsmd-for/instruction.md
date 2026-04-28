# Add instructions to `AGENTS.md` for GitHub issue creation with CLI

Source: [pymc-labs/CausalPy#612](https://github.com/pymc-labs/CausalPy/pull/612)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Added a new section detailing how to create GitHub issues using the GitHub CLI, including prerequisites, drafting, user review, and cleanup steps. This provides a standardized workflow for reporting and tracking issues.

The point of this is to create a workflow where you can generate and submit issues while collaborating with an agent.

<!-- readthedocs-preview causalpy start -->
----
📚 Documentation preview 📚: https://causalpy--612.org.readthedocs.build/en/612/

<!-- readthedocs-preview causalpy end -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
