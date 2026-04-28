# feat(skills): Add PM and research workflow skills

Source: [bobmatnyc/claude-mpm#298](https://github.com/bobmatnyc/claude-mpm/pull/298)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `src/claude_mpm/skills/bundled/main/cross-source-research/SKILL.md`
- `src/claude_mpm/skills/bundled/main/end-of-session/SKILL.md`
- `src/claude_mpm/skills/bundled/main/mcp-security-review/SKILL.md`
- `src/claude_mpm/skills/bundled/main/prep-meeting/SKILL.md`

## What to add / change

## Summary

Four new bundled skills adding PM, research, and session management workflows to the skills catalog:

- **mcp-security-review**: Security gate for MCP server installations. Provenance checking (vendor-hosted vs vendor-published vs community), risk classification (6 tiers), version pinning enforcement, credential exposure mapping, and ongoing maintenance protocol. Addresses a gap where the project ships 4+ MCP integrations but has no guidance on evaluating third-party packages.

- **cross-source-research**: Multi-source investigation workflow for researching topics across configured MCP tools (Slack, Confluence, Jira, GitHub, Drive, databases, analytics). Enforces depth over breadth with research standards: read content not just metadata, trace outcomes not just announcements, synthesize into actionable findings.

- **end-of-session**: Session learning persistence protocol. Captures technical discoveries, decisions, new references, and open threads into project knowledge files before a session closes, so the next session starts with full context instead of from scratch.

- **prep-meeting**: Meeting preparation workflow with attendee context gathering across connected tools, three agenda templates (decision, status/sync, exploratory), talking point preparation with anticipated pushback, and delivery via calendar/chat MCPs.

## Motivation

The bundled skills catalog currently has 44+ skills, almost all engineering-focused (TDD, Docker, debugging, security scanning, G

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
