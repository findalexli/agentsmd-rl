# Add bulk-github-star skill

Source: [besoeasy/open-skills#7](https://github.com/besoeasy/open-skills/pull/7)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/bulk-github-star/SKILL.md`

## What to add / change

## Summary

Adds a new skill for bulk starring GitHub repositories from any user.

### What's included:
- Bash one-liner to star all repos from a user
- Node.js implementation with error handling
- Filter option to star only repos meeting criteria (e.g., star count threshold)
- Rate limit guidance and best practices

### Use cases:
- Supporting open source creators by starring all their work
- Bulk discovery of useful projects from a prolific developer
- Automation workflows for GitHub engagement

The skill follows the existing template format with both Bash and Node.js examples.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
