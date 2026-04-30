# docs: add CLAUDE.md

Source: [skyrim-multiplayer/skymp#2529](https://github.com/skyrim-multiplayer/skymp/pull/2529)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

Considering AGENTS.md instead in the future. Also, file contents is not that good. But I'd post anyway
<!-- ELLIPSIS_HIDDEN -->

----

> [!IMPORTANT]
> Adds `CLAUDE.md` with build and test instructions, including commands for building, running all tests, and running specific unit tests by tag.
> 
>   - **Documentation**:
>     - Adds `CLAUDE.md` with build and test instructions.
>     - Includes commands for building the project using `cmake --build .`.
>     - Provides instructions for running all tests with `ctest --verbose`.
>     - Details running specific unit tests by tag, e.g., `[Respawn]`.
> 
> <sup>This description was created by </sup>[<img alt="Ellipsis" src="https://img.shields.io/badge/Ellipsis-blue?color=175173">](https://www.ellipsis.dev?ref=skyrim-multiplayer%2Fskymp&utm_source=github&utm_medium=referral)<sup> for 1a500b3dd3b7ccc671f8f43b05ac91820d8235cb. You can [customize](https://app.ellipsis.dev/skyrim-multiplayer/settings/summaries) this summary. It will automatically update as commits are pushed.</sup>

<!-- ELLIPSIS_HIDDEN -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
