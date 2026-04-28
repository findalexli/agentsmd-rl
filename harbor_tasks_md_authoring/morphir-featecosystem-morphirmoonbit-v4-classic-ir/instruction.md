# feat(ecosystem): morphir-moonbit v4 classic IR types & ecosystem updates

Source: [finos/morphir#620](https://github.com/finos/morphir/pull/620)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `ecosystem/AGENTS.md`

## What to add / change

## Summary

This PR bundles sets of ecosystem submodule updates and integrates recent changes.

### 1. \morphir-moonbit\ v4 classic IR work
- Tracks \eature/v4-spec-schema\ branch on \morphir-moonbit\
- Adds validated \NameToken\ constructors with parse-don't-verify pattern
- Refactors package source files into \src/\ subdirectory
- Adds classic IR naming types with full test coverage:
  - \FQName\, \QName\, \ModuleName\, \PackageName\, \Path\

### 2. Ecosystem tooling updates
- Adds \morphir-elm\ submodule tracking the remixed branch
- Adds build and test tasks for \morphir-moonbit\ in mise config

*(Note: Also cleanly resolves merges with the newly added \morphir-python\ tracking from \main\)*

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
