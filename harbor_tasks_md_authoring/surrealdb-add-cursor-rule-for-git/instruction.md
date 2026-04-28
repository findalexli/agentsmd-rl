# Add cursor rule for git safety guidelines

Source: [surrealdb/surrealdb#7255](https://github.com/surrealdb/surrealdb/pull/7255)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/git-safety.mdc`

## What to add / change

## What is the motivation?

Prevent AI agents from amending pushed commits or force-pushing branches without explicit user consent. This codifies git safety practices as an always-applied Cursor rule.

## What does this change do?

Adds `.cursor/rules/git-safety.mdc` with `alwaysApply: true` that instructs AI agents to:

- Never amend a commit that has been pushed to a remote
- Never amend without explicit user request
- Never force-push without explicit user request
- Create new follow-up commits for formatting/linting changes
- Never run destructive git commands without explicit request

## What is your testing strategy?

Not applicable — Cursor rule file only.

## Security Considerations

No security implications — this is a Cursor configuration file that restricts agent behaviour.

## Is this related to any issues?

- [x] No related issues

## Have you read the Contributing Guidelines?

- [x] I have read the [Contributing Guidelines](https://github.com/surrealdb/surrealdb/blob/main/CONTRIBUTING.md)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
