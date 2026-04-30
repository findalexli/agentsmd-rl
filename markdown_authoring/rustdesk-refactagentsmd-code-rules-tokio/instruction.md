# refact(AGENTS.md): code rules, tokio

Source: [rustdesk/rustdesk#14911](https://github.com/rustdesk/rustdesk/pull/14911)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

* **Documentation**
  * Rewrote guide into a concise reference with a high-level project layout and pointer to configuration locations (removed step-by-step build/test commands).
  * Condensed Rust guidelines into compact bullets on error handling, borrowing, cloning, dependency restraint, and idiomatic simplicity.
  * Added explicit Tokio rules forbidding nested runtimes/blocking in async and recommending proper async primitives and blocking boundaries.
  * Streamlined editing hygiene into minimal-diff and consistency guidance.
<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
