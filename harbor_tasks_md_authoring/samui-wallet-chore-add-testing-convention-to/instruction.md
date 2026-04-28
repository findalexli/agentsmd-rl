# chore: add testing convention to AGENTS.md

Source: [samui-build/samui-wallet#124](https://github.com/samui-build/samui-wallet/pull/124)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

<!-- ELLIPSIS_HIDDEN -->



> [!IMPORTANT]
> Adds detailed testing guidelines to `AGENTS.md`, specifying test structure, sections, patterns, and key requirements.
> 
>   - **Testing Guidelines**:
>     - Added detailed testing guidelines to `AGENTS.md`.
>     - Specifies test structure with `describe` and `it` blocks, including `beforeEach` and `afterEach` hooks.
>     - Defines test sections for expected and unexpected behavior, requiring console mocking for the latter.
>     - Enforces ARRANGE/ACT/ASSERT pattern with explicit comments and assertion counts.
>     - Allows combined ACT & ASSERT for error tests.
>     - Key requirements include explicit assertions, comments, console mocking, type error handling, and clear descriptions.
> 
> <sup>This description was created by </sup>[<img alt="Ellipsis" src="https://img.shields.io/badge/Ellipsis-blue?color=175173">](https://www.ellipsis.dev?ref=samui-build%2Fsamui-wallet&utm_source=github&utm_medium=referral)<sup> for 5305d0e61115ae9f5d62335e5af40e5508c11bb5. You can [customize](https://app.ellipsis.dev/samui-build/settings/summaries) this summary. It will automatically update as commits are pushed.</sup>

<!-- ELLIPSIS_HIDDEN -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
