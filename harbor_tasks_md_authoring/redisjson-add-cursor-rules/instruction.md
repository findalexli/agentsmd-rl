# Add Cursor Rules

Source: [RedisJSON/RedisJSON#1496](https://github.com/RedisJSON/RedisJSON/pull/1496)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/rust.mdc`
- `.cursor/rules/testing.mdc`

## What to add / change

<!-- CURSOR_SUMMARY -->
> [!NOTE]
> **Low Risk**
> Adds editor guidance docs only; no production code paths or runtime behavior are modified.
> 
> **Overview**
> Adds two new Cursor rule documents under `.cursor/rules/` to standardize contributor guidance.
> 
> Introduces a comprehensive `rust.mdc` best-practices guide (organization, idioms, performance, error handling, `unsafe` documentation, and reuse of existing error helpers) and a `testing.mdc` guide for organizing/running Python flow tests and Rust unit tests.
> 
> <sup>Written by [Cursor Bugbot](https://cursor.com/dashboard?tab=bugbot) for commit 44737d41902a70d53ff57345cf699445c112a868. This will update automatically on new commits. Configure [here](https://cursor.com/dashboard?tab=bugbot).</sup>
<!-- /CURSOR_SUMMARY -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
