# docs: improve root AGENTS.md guidance

Source: [swc-project/swc#11626](https://github.com/swc-project/swc/pull/11626)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary\n- add guidance to prefer enum or dedicated types over raw string literals\n- add debugging/logging rules focused on source verification and structured Rust logging with tracing\n- add shell safety and git workflow rules for safer command usage and PR thread hygiene\n\n## Testing\n- not run (documentation-only change)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
