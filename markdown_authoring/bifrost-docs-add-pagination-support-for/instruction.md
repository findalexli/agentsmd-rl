# docs: add pagination support for PR review threads

Source: [maximhq/bifrost#2393](https://github.com/maximhq/bifrost/pull/2393)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/resolve-pr-comments/SKILL.md`

## What to add / change

## Summary

Enhanced the resolve-pr-comments skill to handle PRs with more than 100 review threads by implementing cursor-based pagination and fixing the reply endpoint usage.

## Changes

- **Added pagination support**: Implemented cursor-based pagination for GraphQL `reviewThreads` queries to handle PRs with more than 100 review threads, ensuring all unresolved comments are discovered
- **Fixed reply endpoint documentation**: Corrected the API endpoint usage to use `POST .../pulls/PR_NUMBER/comments/COMMENT_ID/replies` instead of the incorrect create-comment endpoint with `in_reply_to`
- **Improved error handling**: Added troubleshooting for 422 errors when using wrong reply endpoints
- **Enhanced data parsing**: Modified jq parsing to avoid control character issues by separating comment body fetching from pagination logic
- **Added batch workflow support**: Documented workflow for handling multiple comments in sequence (fix all → push → post all replies)

## Type of change

- [ ] Bug fix
- [x] Feature
- [ ] Refactor
- [x] Documentation
- [ ] Chore/CI

## Affected areas

- [ ] Core (Go)
- [ ] Transports (HTTP)
- [ ] Providers/Integrations
- [ ] Plugins
- [ ] UI (Next.js)
- [x] Docs

## How to test

Test the pagination functionality with a PR that has more than 100 review threads:

```sh
# Test pagination loop for large PRs
gh api graphql -f query='query { repository(owner: "OWNER", name: "REPO") { pullRequest(number: PR_NUMBER) { reviewThreads(first: 100) { pageInfo { hasNe

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
