# docs: Add migration timestamp guidance to @n8n/db AGENTS.md (no-changelog)

Source: [n8n-io/n8n#28444](https://github.com/n8n-io/n8n/pull/28444)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `packages/@n8n/db/AGENTS.md`

## What to add / change

## Summary

I saw a migration on master use a rounded up "future" timestamp, which is mildly annoying if you add an exact timestamp one after and they seem out of order as a result

Adds a "Creating Migrations" section to `packages/@n8n/db/AGENTS.md` instructing developers and AI agents to use exact Unix millisecond timestamps (not rounded or fabricated values) when naming migration files.

## Related Linear tickets, Github issues, and Community forum posts

N/A

## Review / Merge checklist

- [x] I have seen this code, I have run this code, and I take responsibility for this code.
- [ ] PR title and summary are descriptive. ([conventions](../blob/master/.github/pull_request_title_conventions.md))
- [ ] [Docs updated](https://github.com/n8n-io/n8n-docs) or follow-up ticket created.
- [ ] Tests included.
- [ ] PR Labeled with `Backport to Beta`, `Backport to Stable`, or `Backport to v1` (if the PR is an urgent fix that needs to be backported)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
