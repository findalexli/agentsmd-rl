# chore: Add cursor rules for AI integrations contributions

Source: [getsentry/sentry-javascript#19167](https://github.com/getsentry/sentry-javascript/pull/19167)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/adding-a-new-ai-integration.mdc`
- `.cursor/rules/sdk_development.mdc`

## What to add / change

This PR adds `.cursor/rules/adding-a-new-ai-integration.mdc`, a complete reference guide for implementing AI provider integrations (OpenAI, Anthropic, Vercel AI, LangChain, etc.) in the Sentry JavaScript SDK.

Closes #19168 (added automatically)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
