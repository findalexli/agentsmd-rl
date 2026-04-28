# Introduce AGENTS.md and symlink CLAUDE.md to it

Source: [saleor/apps#2088](https://github.com/saleor/apps/pull/2088)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`
- `CLAUDE.md`
- `apps/smtp/AGENTS.md`
- `apps/smtp/CLAUDE.md`
- `apps/smtp/CLAUDE.md`

## What to add / change

## Scope of the PR

<!-- Describe briefly the changes made in this PR -->

## Related issues

<!-- If any, mention issues that are connected with this PR -->

## Checklist

- [ ] I added changesets and [read good practices](/.changeset/README.md).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
