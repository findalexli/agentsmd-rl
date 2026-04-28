# Add cursor rule for pull request guidelines

Source: [surrealdb/surrealdb#7248](https://github.com/surrealdb/surrealdb/pull/7248)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/pull-requests.mdc`

## What to add / change

## What is the motivation?

AI coding assistants (Cursor, Claude, etc.) working in this repo need guidance on how to format pull request descriptions. Without a rule, PRs created by agents may not follow the project's template format, requiring manual edits.

## What does this change do?

Adds an always-applied Cursor rule (`.cursor/rules/pull-requests.mdc`) that instructs AI agents to follow the project's PR template format when creating pull requests. The rule covers:

- Required PR body sections (motivation, description, testing strategy, security considerations, related issues, contributing guidelines)
- When to apply labels (`breaking-change`, `needs-documentation`, `Modifies env vars or commands`)
- Guidance against force-pushing after PR creation unless explicitly requested

## What is your testing strategy?

No code changes — this is a Cursor rule file only. Validated by using it in practice during agent-assisted PR creation.

## Security Considerations

No security implications — this is a documentation/tooling-only change that adds guidance for AI assistants.

## Is this related to any issues?

- [x] No related issues

## Have you read the Contributing Guidelines?

- [x] I have read the [Contributing Guidelines](https://github.com/surrealdb/surrealdb/blob/main/CONTRIBUTING.md)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
