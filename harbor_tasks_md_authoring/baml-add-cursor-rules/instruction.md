# add cursor rules

Source: [BoundaryML/baml#2452](https://github.com/BoundaryML/baml/pull/2452)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/instructions.mdc`

## What to add / change

<!-- ELLIPSIS_HIDDEN -->


> [!IMPORTANT]
> Adds `.cursor/rules/instructions.mdc` with setup, testing, and formatting instructions for BAML development.
> 
>   - **New File**:
>     - Adds `.cursor/rules/instructions.mdc` with instructions for BAML development.
>   - **Setup**:
>     - Install `mise` using `curl https://mise.run | sh`.
>   - **Testing**:
>     - Prefer Rust unit tests; use Python integ tests with `uv`, `maturin`, and `pytest` if needed.
>     - Update `baml_src` with `uv run baml-cli generate` after changes.
>   - **Environment**:
>     - Use `infisical CLI` if available, otherwise ensure correct env vars.
>   - **Formatting**:
>     - Run `cargo fmt` with specific configs in `engine` directory for Rust files.
> 
> <sup>This description was created by </sup>[<img alt="Ellipsis" src="https://img.shields.io/badge/Ellipsis-blue?color=175173">](https://www.ellipsis.dev?ref=BoundaryML%2Fbaml&utm_source=github&utm_medium=referral)<sup> for 7e2eb30eff5843c7c6ae1f2ff966dae758d468da. You can [customize](https://app.ellipsis.dev/BoundaryML/settings/summaries) this summary. It will automatically update as commits are pushed.</sup>


<!-- ELLIPSIS_HIDDEN -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
