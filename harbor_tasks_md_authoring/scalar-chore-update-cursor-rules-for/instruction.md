# chore: update cursor rules for testing

Source: [scalar/scalar#7107](https://github.com/scalar/scalar/pull/7107)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/tests.mdc`

## What to add / change

* no more nested `describe()` groups
* match all test file extensions

<!-- CURSOR_SUMMARY -->
---

> [!NOTE]
> Enforces a single, non-nested describe per test and expands test globs to include e2e patterns; updates example tests accordingly.
> 
> - **Testing rules (`.cursor/rules/tests.mdc`)**:
>   - Expand `globs` to include `*.e2e-spec.ts` and `*.e2e.ts`.
>   - Require a single top-level `describe()` and forbid nested `describe()` blocks.
>   - Clarify concise `it()` descriptions without starting with "should."
> - **Example updates**:
>   - Replace nested `describe()` with flat structure: separate `describe('generateSlug')` and `describe('doSomething')`.
>   - Update imports to `custom-lib` and add a sample test for `doSomething`.
> 
> <sup>Written by [Cursor Bugbot](https://cursor.com/dashboard?tab=bugbot) for commit 9f9f5daeb5b6323aeb96b2e2da2349039d3935f4. This will update automatically on new commits. Configure [here](https://cursor.com/dashboard?tab=bugbot).</sup>
<!-- /CURSOR_SUMMARY -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
