# docs: add AGENTS.md with CLAUDE.md symlink

Source: [bkrem/awesome-solidity#168](https://github.com/bkrem/awesome-solidity/pull/168)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

## Summary

- Adds `AGENTS.md` documenting the repo for AI coding agents: purpose (single-file curated list on `gh-pages`), CI check, entry-format / alphabetical-ordering rules, and `README.md` section structure.
- Incorporates the `PULL_REQUEST_TEMPLATE.md` guidance (drop `A`/`An` prefixes, avoid repeating "Solidity", dedupe URLs before adding) and the `--white-list stermi.medium.com` flag added to CI in #167.
- Adds `CLAUDE.md` as a symlink to `AGENTS.md` so Claude Code picks up the same guidance without duplication.

## Test plan

- [ ] `readlink CLAUDE.md` returns `AGENTS.md`
- [ ] `AGENTS.md` renders correctly on GitHub
- [ ] `awesome_bot` CI passes (no link changes, but confirm the added files don't break the workflow)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
