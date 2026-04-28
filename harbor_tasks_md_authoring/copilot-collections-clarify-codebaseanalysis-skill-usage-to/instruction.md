# Clarify codebase-analysis skill usage to resolve conflicting report instructions

Source: [TheSoftwareHouse/copilot-collections#16](https://github.com/TheSoftwareHouse/copilot-collections/pull/16)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/prompts/code-quality-check.prompt.md`

## What to add / change

The `code-quality-check.prompt.md` instructed agents to "load and follow" the `codebase-analysis` skill, which includes its own report template instructions (`codebase-analysis.example.md`). This conflicted with the prompt's own "Report Structure" section that defines a different report format and filename (`code-quality-report.md`).

## Changes

- Updated the `codebase-analysis` skill reference to clarify it's for the analysis process only
- Added explicit note that this prompt's "Report Structure" section overrides any report/template instructions from the skill

```diff
- `codebase-analysis` - for the structured codebase analysis process and report template
+ `codebase-analysis` - for the structured codebase analysis process only (note: this prompt's "Report Structure" section overrides any report/template instructions from the skill)
```

This ensures agents use the skill's analysis methodology while following this prompt's specific report requirements.

<!-- START COPILOT CODING AGENT TIPS -->
---

💡 You can make Copilot smarter by setting up custom instructions, customizing its development environment and configuring Model Context Protocol (MCP) servers. Learn more [Copilot coding agent tips](https://gh.io/copilot-coding-agent-tips) in the docs.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
