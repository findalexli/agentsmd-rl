# Remove servicing PR template from Copilot instructions

Source: [dotnet/efcore#37761](https://github.com/dotnet/efcore/pull/37761)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

The servicing PR description template (with Description, Customer impact, How found, Regression, Testing, Risk sections) has been removed from `.github/copilot-instructions.md`. The PR Guidelines section now only retains the instruction to target `main` for new PRs.

<!-- START COPILOT CODING AGENT SUFFIX -->



<!-- START COPILOT ORIGINAL PROMPT -->



<details>

<summary>Original prompt</summary>

> Remove the servicing template from copilot instructions


</details>



<!-- START COPILOT CODING AGENT TIPS -->
---

💡 You can make Copilot smarter by setting up custom instructions, customizing its development environment and configuring Model Context Protocol (MCP) servers. Learn more [Copilot coding agent tips](https://gh.io/copilot-coding-agent-tips) in the docs.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
