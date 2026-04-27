# chore: add architecture sequence diagrams to CLAUDE.md

Source: [breaking-brake/cc-wf-studio#256](https://github.com/breaking-brake/cc-wf-studio/pull/256)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary

Add Mermaid-formatted architecture sequence diagrams to CLAUDE.md to help developers understand the application's data flows and component interactions.

## Changes

Added 7 diagrams to the `<!-- MANUAL ADDITIONS START -->` section:

1. **Architecture Overview** - Flowchart showing Extension Host/Webview relationship and external services
2. **Workflow Save Flow** - User → Toolbar → Bridge → Command → FileService → Disk
3. **AI Workflow Generation Flow** - Including parallel schema/skill loading
4. **AI Workflow Refinement Flow** - With conversation history management
5. **Slack Workflow Share Flow** - Including sensitive data detection branch
6. **Slack Workflow Import Flow** - Via VSCode URI Handler (Deep Link)
7. **MCP Server/Tool Retrieval Flow** - With cache handling

## Impact

- Documentation only, no code changes
- Diagrams render in GitHub and VSCode Markdown preview

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
