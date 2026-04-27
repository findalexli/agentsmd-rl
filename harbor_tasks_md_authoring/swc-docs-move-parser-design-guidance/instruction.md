# docs: Move parser design guidance into AGENTS.md

Source: [swc-project/swc#11600](https://github.com/swc-project/swc/pull/11600)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `crates/swc_es_parser/AGENTS.md`

## What to add / change

## Summary
- move `swc_es_parser` design guidance from `docs/swc-es-parser-design.md` into `crates/swc_es_parser/AGENTS.md`
- remove the legacy top-level design doc so crate-specific guidance lives next to the crate
- keep `swc_es_parser` source behavior unchanged

## Testing
- cargo test -p swc_es_parser

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
