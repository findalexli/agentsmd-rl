# Add Cursor rules for PR review / re-review

Source: [ai2cm/ace#745](https://github.com/ai2cm/ace/pull/745)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/ace-context.mdc`
- `.cursor/rules/pr-rereview.mdc`
- `.cursor/rules/pr-review.mdc`

## What to add / change

Adds rules to `.cursor/rules` which may be helpful in automating some aspects of PR review:

1. `ace-context.mdc`: Basic repo context.
2. `pr-review.mdc`:  Instructions for responding to prompts like "Review PR #N in the ace repo"
3. `pr-rereview.mdc`: Instructions for responding to prompts like "Re-review PR #N" or "Re-review PR #[N] starting from commit [SHA]"

These rules make use of GitHub's MCP server, which can be configured in Cursor's "Tools & MCP" settings. You will need a read-only personal access token with the following permissions: Pull requests, Issues, Contents, Metadata.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
