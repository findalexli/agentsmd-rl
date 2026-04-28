# Add `AGENTS.md`

Source: [grafana/k6#5612](https://github.com/grafana/k6/pull/5612)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## What?

Adds `AGENTS.md` and loads `CLAUDE.md`.

## Why?

This makes most agents less confused.

The `@` syntax makes agents to include the whole `CLAUDE.md` file.

See:
- https://agents.md/
- https://developers.openai.com/codex/guides/agents-md/
- https://cursor.com/docs/context/rules
etc.

## Note

Since `AGENTS.md` is cross-agent, it might even more sense to move all `CLAUDE.md` rules into `AGENTS.md` and load it from `CLAUDE.md`. But, this is a good first step at least.

## Checklist

<!-- 
If you haven't read the contributing guidelines https://github.com/grafana/k6/blob/master/CONTRIBUTING.md 
and code of conduct https://github.com/grafana/k6/blob/master/CODE_OF_CONDUCT.md yet, please do so
-->

- [x] I have performed a self-review of my code.
- [ ] I have commented on my code, particularly in hard-to-understand areas.
- [ ] I have added tests for my changes.
- [ ] I have run linter and tests locally (`make check`) and all pass.

## Checklist: Documentation (only for k6 maintainers and if relevant)

**Please do not merge this PR until the following items are filled out.**

- [x] I have added the correct milestone and labels to the PR.
- [ ] I have updated the release notes: _link_
- [ ] I have updated or added an issue to the [k6-documentation](https://github.com/grafana/k6-docs): grafana/k6-docs#NUMBER if applicable
- [ ] I have updated or added an issue to the [TypeScript definitions](https://github.com/grafana/k6-DefinitelyTyp

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
