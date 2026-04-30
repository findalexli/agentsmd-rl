# chore: update CLAUDE.md guidelines and deprecate chat UI AI editing

Source: [breaking-brake/cc-wf-studio#562](https://github.com/breaking-brake/cc-wf-studio/pull/562)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
- Add planning guideline requiring context gathering from github-knowledge MCP before Plan Mode
- Add AI Editing Features section documenting MCP server as the active approach
- Mark chat UI-based AI editing (generation, refinement, skill generation) as discontinued
- Remove obsolete detailed documentation for deprecated chat UI AI editing features

## Changes
- **Planning Guidelines**: New section requiring `search_decisions`, `search_domain_knowledge`, `get_decision_detail`, `get_module_history` usage in Plan Mode
- **AI Editing Features**: New section with MCP server sequence diagram (active) and chat UI deprecation notice
- **Removed**: AI Workflow Refinement sequence diagram, AI-Assisted Skill Node Generation section, AI-Assisted Workflow Generation section
- **Cleaned up**: Related Active Technologies entries for deprecated features

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
