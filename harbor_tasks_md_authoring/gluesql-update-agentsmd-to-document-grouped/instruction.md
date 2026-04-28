# Update AGENTS.md to document grouped use convention

Source: [gluesql/gluesql#1788](https://github.com/gluesql/gluesql/pull/1788)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary
- document single-`use` grouping rule in AGENTS instructions

## Testing
- `cargo fmt --all`
- `cargo clippy --all-targets -- -D warnings`
- `cargo test --manifest-path core/Cargo.toml --lib --quiet`


------
https://chatgpt.com/codex/tasks/task_e_68c6742e1620832a8bdafe9c3ef56f23

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

* **Documentation**
  * Added a guideline to group imports under a single “use” statement where possible.
  * Clarifies import formatting conventions for consistency and readability.
  * No changes to functionality, tests, or runtime behavior.
  * No impact on public APIs or exported entities.

<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
