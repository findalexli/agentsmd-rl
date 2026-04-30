# feat(skills): add architecture-decision-records skill

Source: [affaan-m/everything-claude-code#555](https://github.com/affaan-m/everything-claude-code/pull/555)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/architecture-decision-records/SKILL.md`

## What to add / change

## Summary
Adds an `architecture-decision-records` skill that captures architectural decisions made during Claude Code sessions as structured ADR documents.

## Motivation
Architectural decisions typically live in Slack threads, PR comments, or someone's memory — and are lost within weeks. This skill turns "we decided to use X because Y" moments into durable, searchable records that live alongside the code.

## What It Does
- **Detects** decision moments from explicit signals ("let's go with X") and implicit signals (comparing frameworks, discussing trade-offs)
- **Captures** structured ADRs using the Michael Nygard format: Context → Decision → Alternatives Considered → Consequences
- **Maintains** numbered ADR files in `docs/adr/` with a README index
- **Manages** ADR lifecycle: proposed → accepted → deprecated/superseded

## Key Design Decisions
- Uses the widely-adopted lightweight ADR format (not heavyweight ATAM or similar)
- Categorizes 8 decision types worth recording (tech choices, architecture patterns, API design, data modeling, infra, security, testing, process)
- Explicitly excludes trivial decisions (variable naming, formatting)
- Integrates with planner agent (suggest ADR for arch changes) and code-reviewer agent (flag PRs missing ADRs)

## Type
- [x] Skill
- [ ] Agent
- [ ] Hook
- [ ] Command

## Testing
- Verified skill format matches existing skills
- ADR format tested against real-world decision scenarios
- Includes Antigravity `openai.yaml` following existi

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
