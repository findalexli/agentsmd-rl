# docs(es): add AGENTS two-pass rules for es crates

Source: [swc-project/swc#11634](https://github.com/swc-project/swc/pull/11634)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `crates/swc_es_minifier/AGENTS.md`
- `crates/swc_es_transforms/AGENTS.md`

## What to add / change

## Summary
- add AGENTS.md to crates/swc_es_transforms
- add AGENTS.md to crates/swc_es_minifier
- document strict 2-pass rule (analysis pass, then transform pass)
- document prohibition on dependencies to any swc_ecma_* crates

## Testing
- not run (docs-only change)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
