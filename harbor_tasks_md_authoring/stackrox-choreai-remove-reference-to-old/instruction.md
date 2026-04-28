# chore(AI): Remove reference to old repo from AGENTS.md

Source: [stackrox/stackrox#17530](https://github.com/stackrox/stackrox/pull/17530)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Description

We should not point to the legacy repo, because it is still private. Agents would not be able to access it normally, and if someone who has access to that repo then gave their agent a token, it could leak references to old customers.

## User-facing documentation

- [x] [CHANGELOG.md] update is not needed
- [x] documentation  is not needed

## Testing and quality

- [x] CI results are [inspected](https://docs.google.com/document/d/1d5ga073jkv4CO1kAJqp8MPGpC6E1bwyrCGZ7S5wKg3w/edit?tab=t.0#heading=h.w4ercgtcg0xp)

The UI e2e test failure is a flake. Not wasting compute resources to re-run.

### Automated testing

no test changes needed

### How I validated my change

PR review

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
