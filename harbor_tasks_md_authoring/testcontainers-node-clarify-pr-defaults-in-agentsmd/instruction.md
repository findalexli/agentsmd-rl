# Clarify PR defaults in AGENTS.md

Source: [testcontainers/testcontainers-node#1303](https://github.com/testcontainers/testcontainers-node/pull/1303)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary

- add an instruction-precedence section to `AGENTS.md`
- clarify that PR titles must not include automated prefixes such as `[codex]`
- clarify that PRs should be opened ready for review by default and only use draft when explicitly requested or intentionally not ready

## Why

The current `AGENTS.md` guidance did not explicitly state that repository-specific instructions override generic agent defaults, and it did not explicitly define the default PR review state. Making those rules explicit reduces avoidable process mistakes in future agent-driven changes.

## Impact

This is a documentation-only clarification. It does not change runtime behavior or public APIs.

## Verification

- `npm run format`
- `npm run lint`

## Test results summary

- `npm run format`: passed
- `npm run lint`: passed

## Evidence this is not breaking

- documentation-only change with no code, package, or API changes

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
