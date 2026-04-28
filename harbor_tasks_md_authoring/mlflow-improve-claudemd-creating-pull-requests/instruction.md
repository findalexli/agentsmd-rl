# Improve CLAUDE.md Creating Pull Requests section guidance

Source: [mlflow/mlflow#17745](https://github.com/mlflow/mlflow/pull/17745)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

This PR improves the "Creating Pull Requests" section in `CLAUDE.md` by making two targeted changes:

1. **Removes redundant information**: Eliminates the sentence "The template will automatically appear when you create a PR on GitHub" as this is obvious behavior that doesn't provide actionable value to contributors.

2. **Adds practical guidance**: Introduces helpful advice to "Remove any unused checkboxes from the template to keep your PR clean and focused" which encourages contributors to actively curate their PR descriptions rather than leaving irrelevant template sections.

The changes make the documentation more actionable and focused on best practices for creating clean, well-organized pull requests. This aligns with the document's overall tone of providing practical development guidance.

These minimal changes enhance the contributor experience by replacing redundant information with useful advice that leads to better-quality pull requests.

<!-- START COPILOT CODING AGENT SUFFIX -->



<!-- START COPILOT CODING AGENT TIPS -->
---

💡 You can make Copilot smarter by setting up custom instructions, customizing its development environment and configuring Model Context Protocol (MCP) servers. Learn more [Copilot coding agent tips](https://gh.io/copilot-coding-agent-tips) in the docs.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
