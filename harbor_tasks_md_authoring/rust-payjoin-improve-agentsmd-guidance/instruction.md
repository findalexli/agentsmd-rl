# Improve AGENTS.md guidance

Source: [payjoin/rust-payjoin#1344](https://github.com/payjoin/rust-payjoin/pull/1344)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary
- Specify concrete AI disclosure format (`Disclosure: co-authored by <agent-name>`) instead of vague "required in PR body"
- Add nix tooling section: tools come from direnv, new tools go in `flake.nix`

## Test plan
- [x] Verify AGENTS.md renders correctly on GitHub
- [x] Confirm direnv/nix guidance is accurate for new contributors

Disclosure: co-authored by Claude Code

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
