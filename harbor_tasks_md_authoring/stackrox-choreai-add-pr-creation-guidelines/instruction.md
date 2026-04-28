# chore(AI): add PR creation guidelines to AGENTS.md

Source: [stackrox/stackrox#17219](https://github.com/stackrox/stackrox/pull/17219)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Description

Added "Creating Pull Requests" workflow section to AGENTS.md with guidelines for AI agents creating PRs.

**Problem:** AI agents need clear guidelines to create PRs that follow project standards.

**Solution:** Document requirements in AGENTS.md as single source of truth, including:
- Create PRs as draft for human review
- Add ai-assisted label
- Follow PR title format (reference check-pr-title.yaml)
- Follow PR template structure
- Keep descriptions brief and factual

**Why this approach:** Consolidates scattered tribal knowledge into documented guidelines, reduces review friction.

## User-facing documentation

- [x] [CHANGELOG.md](https://github.com/stackrox/stackrox/blob/master/CHANGELOG.md) is updated **OR** update is not needed
- [x] [documentation PR](https://spaces.redhat.com/display/StackRox/Submitting+a+User+Documentation+Pull+Request) is created and is linked above **OR** is not needed

## Testing and quality

- [x] the change is production ready: the change is [GA](https://github.com/stackrox/stackrox/blob/master/PR_GA.md), or otherwise the functionality is gated by a [feature flag](https://github.com/stackrox/stackrox/blob/master/pkg/features/README.md)
- [x] CI results are [inspected](https://docs.google.com/document/d/1d5ga073jkv4CO1kAJqp8MPGpC6E1bwyrCGZ7S5wKg3w/edit?tab=t.0#heading=h.w4ercgtcg0xp)

### Automated testing

Not needed - documentation-only change.

### How I validated my change

- Reviewed guidelines for clarity and completeness
- 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
