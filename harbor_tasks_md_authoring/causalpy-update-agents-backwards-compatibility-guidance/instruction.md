# Update AGENTS backwards compatibility guidance

Source: [pymc-labs/CausalPy#686](https://github.com/pymc-labs/CausalPy/pull/686)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary

Clarify that backwards compatibility should only be preserved for released APIs, not for APIs introduced within the same PR.

Fixes #684

## Changes

- Document the backwards compatibility guidance in `AGENTS.md`.

## Testing

- Not run (documentation-only change).

## Checklist

- [ ] Pre-commit checks pass
- [ ] All tests pass
- [ ] Documentation updated (if applicable)
- [x] Follows project coding conventions

<!-- readthedocs-preview causalpy start -->
----
📚 Documentation preview 📚: https://causalpy--686.org.readthedocs.build/en/686/

<!-- readthedocs-preview causalpy end -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
